"""
TodoWrite 工具 - 任务清单管理
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TodoStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TodoItem(BaseModel):
    """任务项"""
    id: str
    content: str
    status: TodoStatus = TodoStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    priority: int = 0  # 优先级，越高越重要
    
    class Config:
        use_enum_values = True
    
    def complete(self) -> None:
        """标记为完成"""
        self.status = TodoStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def cancel(self) -> None:
        """标记为取消"""
        self.status = TodoStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def start(self) -> None:
        """标记为进行中"""
        self.status = TodoStatus.IN_PROGRESS


class TodoManager:
    """
    Todo 管理器
    
    管理任务清单的增删改查
    """
    
    def __init__(self):
        self._todos: Dict[str, TodoItem] = {}
        self._counter: int = 0
    
    def add(self, content: str, priority: int = 0) -> TodoItem:
        """
        添加任务
        
        Args:
            content: 任务内容
            priority: 优先级
        
        Returns:
            新创建的任务项
        """
        self._counter += 1
        todo_id = f"todo_{self._counter}"
        
        todo = TodoItem(
            id=todo_id,
            content=content,
            priority=priority
        )
        
        self._todos[todo_id] = todo
        return todo
    
    def get(self, todo_id: str) -> Optional[TodoItem]:
        """获取任务"""
        return self._todos.get(todo_id)
    
    def update(self, todo_id: str, **kwargs) -> Optional[TodoItem]:
        """
        更新任务
        
        Args:
            todo_id: 任务 ID
            **kwargs: 要更新的字段
        
        Returns:
            更新后的任务项
        """
        todo = self._todos.get(todo_id)
        if not todo:
            return None
        
        for key, value in kwargs.items():
            if hasattr(todo, key):
                setattr(todo, key, value)
        
        return todo
    
    def complete(self, todo_id: str) -> Optional[TodoItem]:
        """标记任务为完成"""
        todo = self._todos.get(todo_id)
        if todo:
            todo.complete()
        return todo
    
    def cancel(self, todo_id: str) -> Optional[TodoItem]:
        """标记任务为取消"""
        todo = self._todos.get(todo_id)
        if todo:
            todo.cancel()
        return todo
    
    def start(self, todo_id: str) -> Optional[TodoItem]:
        """标记任务为进行中"""
        todo = self._todos.get(todo_id)
        if todo:
            todo.start()
        return todo
    
    def delete(self, todo_id: str) -> bool:
        """删除任务"""
        if todo_id in self._todos:
            del self._todos[todo_id]
            return True
        return False
    
    def list_all(self) -> List[TodoItem]:
        """列出所有任务"""
        return list(self._todos.values())
    
    def list_by_status(self, status: TodoStatus) -> List[TodoItem]:
        """按状态列出任务"""
        return [
            todo for todo in self._todos.values()
            if todo.status == status
        ]
    
    def list_pending(self) -> List[TodoItem]:
        """列出待办任务"""
        return self.list_by_status(TodoStatus.PENDING)
    
    def list_in_progress(self) -> List[TodoItem]:
        """列出进行中的任务"""
        return self.list_by_status(TodoStatus.IN_PROGRESS)
    
    def list_completed(self) -> List[TodoItem]:
        """列出已完成的任务"""
        return self.list_by_status(TodoStatus.COMPLETED)
    
    def clear_completed(self) -> int:
        """清除已完成的任务"""
        completed = self.list_completed()
        for todo in completed:
            del self._todos[todo.id]
        return len(completed)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取任务摘要"""
        all_todos = self.list_all()
        
        return {
            "total": len(all_todos),
            "pending": len(self.list_pending()),
            "in_progress": len(self.list_in_progress()),
            "completed": len(self.list_completed()),
            "cancelled": len(self.list_by_status(TodoStatus.CANCELLED)),
        }
    
    def to_markdown(self) -> str:
        """导出为 Markdown 格式"""
        lines = ["# Todo List\n"]
        
        # 按状态分组
        pending = self.list_pending()
        in_progress = self.list_in_progress()
        completed = self.list_completed()
        
        if in_progress:
            lines.append("## In Progress\n")
            for todo in in_progress:
                lines.append(f"- [ ] **{todo.content}** (ID: {todo.id})")
            lines.append("")
        
        if pending:
            lines.append("## Pending\n")
            for todo in pending:
                lines.append(f"- [ ] {todo.content} (ID: {todo.id})")
            lines.append("")
        
        if completed:
            lines.append("## Completed\n")
            for todo in completed:
                lines.append(f"- [x] ~~{todo.content}~~ (ID: {todo.id})")
            lines.append("")
        
        return "\n".join(lines)


class TodoTool:
    """
    TodoWrite 工具
    
    用于管理任务清单的工具
    """
    
    def __init__(self, manager: TodoManager):
        self.manager = manager
    
    @property
    def name(self) -> str:
        return "todo_write"
    
    @property
    def description(self) -> str:
        return """Manage a todo list for tracking tasks.

Operations:
- add: Add a new todo item
- update: Update a todo item
- complete: Mark a todo as completed
- cancel: Cancel a todo
- list: List all todos
- clear: Clear completed todos
"""
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "update", "complete", "cancel", "list", "clear"],
                    "description": "Operation to perform",
                },
                "todos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "content": {"type": "string"},
                            "status": {"type": "string"},
                            "priority": {"type": "integer"},
                        },
                    },
                    "description": "Todo items (for add/update operations)",
                },
            },
            "required": ["operation"],
        }
    
    def execute(self, operation: str, todos: List[Dict] = None, **kwargs) -> str:
        """执行 Todo 操作"""
        if operation == "add":
            if not todos:
                return "Error: No todos provided for add operation"
            
            results = []
            for todo_data in todos:
                content = todo_data.get("content", "")
                priority = todo_data.get("priority", 0)
                todo = self.manager.add(content, priority)
                results.append(f"Added: {todo.id} - {todo.content}")
            
            return "\n".join(results)
        
        elif operation == "update":
            if not todos:
                return "Error: No todos provided for update operation"
            
            results = []
            for todo_data in todos:
                todo_id = todo_data.get("id", "")
                todo = self.manager.update(todo_id, **todo_data)
                if todo:
                    results.append(f"Updated: {todo.id}")
                else:
                    results.append(f"Not found: {todo_id}")
            
            return "\n".join(results)
        
        elif operation == "complete":
            if not todos:
                return "Error: No todos provided for complete operation"
            
            results = []
            for todo_data in todos:
                todo_id = todo_data.get("id", "")
                todo = self.manager.complete(todo_id)
                if todo:
                    results.append(f"Completed: {todo.id} - {todo.content}")
                else:
                    results.append(f"Not found: {todo_id}")
            
            return "\n".join(results)
        
        elif operation == "cancel":
            if not todos:
                return "Error: No todos provided for cancel operation"
            
            results = []
            for todo_data in todos:
                todo_id = todo_data.get("id", "")
                todo = self.manager.cancel(todo_id)
                if todo:
                    results.append(f"Cancelled: {todo.id} - {todo.content}")
                else:
                    results.append(f"Not found: {todo_id}")
            
            return "\n".join(results)
        
        elif operation == "list":
            return self.manager.to_markdown()
        
        elif operation == "clear":
            count = self.manager.clear_completed()
            return f"Cleared {count} completed todos"
        
        else:
            return f"Error: Unknown operation: {operation}"
