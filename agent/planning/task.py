"""
任务系统 - 任务管理和持久化
"""

import json
import os
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(BaseModel):
    """任务"""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    # 依赖关系
    blocked_by: List[str] = Field(default_factory=list)
    blocks: List[str] = Field(default_factory=list)
    
    # 时间信息
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # 执行信息
    assigned_to: Optional[str] = None  # Agent ID
    result: Optional[str] = None
    error: Optional[str] = None
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
    
    def start(self) -> None:
        """开始执行"""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()
    
    def complete(self, result: str = None) -> None:
        """标记为完成"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
    
    def fail(self, error: str) -> None:
        """标记为失败"""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error = error
    
    def block(self, blocker_id: str) -> None:
        """标记为被阻塞"""
        self.status = TaskStatus.BLOCKED
        if blocker_id not in self.blocked_by:
            self.blocked_by.append(blocker_id)
    
    def unblock(self, blocker_id: str) -> None:
        """解除阻塞"""
        if blocker_id in self.blocked_by:
            self.blocked_by.remove(blocker_id)
        if not self.blocked_by:
            self.status = TaskStatus.READY
    
    def is_ready(self) -> bool:
        """是否准备好执行"""
        return (
            self.status in (TaskStatus.PENDING, TaskStatus.READY) and
            not self.blocked_by
        )


class TaskManager:
    """
    任务管理器
    
    管理任务的创建、执行、持久化
    """
    
    def __init__(self, storage_path: str = None):
        self._tasks: Dict[str, Task] = {}
        self._counter: int = 0
        self._storage_path = storage_path or ".agentforge/tasks.json"
    
    def create(
        self, 
        title: str, 
        description: str = "",
        priority: TaskPriority = TaskPriority.MEDIUM,
        blocked_by: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Task:
        """
        创建任务
        
        Args:
            title: 任务标题
            description: 任务描述
            priority: 优先级
            blocked_by: 阻塞任务 ID 列表
            metadata: 元数据
        
        Returns:
            新创建的任务
        """
        self._counter += 1
        task_id = f"task_{self._counter}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            blocked_by=blocked_by or [],
            metadata=metadata or {}
        )
        
        # 如果没有依赖，状态为 READY
        if not task.blocked_by:
            task.status = TaskStatus.READY
        
        self._tasks[task_id] = task
        
        # 更新阻塞关系
        for blocker_id in (blocked_by or []):
            blocker = self._tasks.get(blocker_id)
            if blocker:
                blocker.blocks.append(task_id)
        
        return task
    
    def get(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self._tasks.get(task_id)
    
    def start(self, task_id: str, agent_id: str = None) -> Optional[Task]:
        """开始执行任务"""
        task = self._tasks.get(task_id)
        if task and task.is_ready():
            task.start()
            task.assigned_to = agent_id
            return task
        return None
    
    def complete(self, task_id: str, result: str = None) -> Optional[Task]:
        """完成任务"""
        task = self._tasks.get(task_id)
        if task:
            task.complete(result)
            
            # 解除被阻塞的任务
            for blocked_id in task.blocks:
                blocked_task = self._tasks.get(blocked_id)
                if blocked_task:
                    blocked_task.unblock(task_id)
            
            return task
        return None
    
    def fail(self, task_id: str, error: str) -> Optional[Task]:
        """任务失败"""
        task = self._tasks.get(task_id)
        if task:
            task.fail(error)
            return task
        return None
    
    def list_all(self) -> List[Task]:
        """列出所有任务"""
        return list(self._tasks.values())
    
    def list_by_status(self, status: TaskStatus) -> List[Task]:
        """按状态列出任务"""
        return [
            task for task in self._tasks.values()
            if task.status == status
        ]
    
    def list_ready(self) -> List[Task]:
        """列出可执行的任务"""
        return [
            task for task in self._tasks.values()
            if task.is_ready()
        ]
    
    def get_next_task(self) -> Optional[Task]:
        """获取下一个可执行的任务（按优先级排序）"""
        ready_tasks = self.list_ready()
        if not ready_tasks:
            return None
        
        # 按优先级排序
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
        }
        
        ready_tasks.sort(key=lambda t: priority_order.get(t.priority, 2))
        return ready_tasks[0]
    
    def save(self) -> None:
        """持久化到文件"""
        data = {
            "counter": self._counter,
            "tasks": {
                task_id: task.dict()
                for task_id, task in self._tasks.items()
            }
        }
        
        # 创建目录
        Path(self._storage_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self._storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    
    def load(self) -> bool:
        """从文件加载"""
        if not os.path.exists(self._storage_path):
            return False
        
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self._counter = data.get("counter", 0)
            self._tasks = {
                task_id: Task(**task_data)
                for task_id, task_data in data.get("tasks", {}).items()
            }
            
            return True
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return False
    
    def get_summary(self) -> Dict[str, Any]:
        """获取任务摘要"""
        all_tasks = self.list_all()
        
        return {
            "total": len(all_tasks),
            "ready": len(self.list_ready()),
            "running": len(self.list_by_status(TaskStatus.RUNNING)),
            "completed": len(self.list_by_status(TaskStatus.COMPLETED)),
            "failed": len(self.list_by_status(TaskStatus.FAILED)),
            "blocked": len(self.list_by_status(TaskStatus.BLOCKED)),
        }
    
    def to_dependency_graph(self) -> str:
        """导出为依赖图（Mermaid 格式）"""
        lines = ["graph TD"]
        
        for task in self._tasks.values():
            # 节点样式
            style = ""
            if task.status == TaskStatus.COMPLETED:
                style = ":::completed"
            elif task.status == TaskStatus.RUNNING:
                style = ":::running"
            elif task.status == TaskStatus.FAILED:
                style = ":::failed"
            
            lines.append(f"    {task.id}[\"{task.title}\"]{style}")
            
            # 依赖关系
            for blocker_id in task.blocked_by:
                lines.append(f"    {blocker_id} --> {task.id}")
        
        # 添加样式
        lines.extend([
            "",
            "    classDef completed fill:#90EE90",
            "    classDef running fill:#87CEEB",
            "    classDef failed fill:#FFB6C1",
        ])
        
        return "\n".join(lines)
