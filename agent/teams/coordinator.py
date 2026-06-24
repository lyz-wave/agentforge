"""
团队协调器 - 管理多 Agent 协作
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from agent.teams.bus import MessageBus, BusMessage, MessageType
from agent.teams.mailbox import AsyncMailbox


class TeamMember(BaseModel):
    """团队成员"""
    id: str
    name: str
    role: str = "worker"
    capabilities: List[str] = Field(default_factory=list)
    status: str = "idle"  # idle, busy, offline
    joined_at: datetime = Field(default_factory=datetime.now)


class TeamCoordinator:
    """
    团队协调器
    
    管理多 Agent 团队的协作
    """
    
    def __init__(self, team_id: str):
        self.team_id = team_id
        self._members: Dict[str, TeamMember] = {}
        self._mailboxes: Dict[str, AsyncMailbox] = {}
        self._message_bus = MessageBus()
        self._task_queue: List[Dict[str, Any]] = []
    
    def add_member(
        self, 
        agent_id: str, 
        name: str,
        role: str = "worker",
        capabilities: List[str] = None
    ) -> TeamMember:
        """
        添加团队成员
        
        Args:
            agent_id: Agent ID
            name: 名称
            role: 角色
            capabilities: 能力列表
        
        Returns:
            新成员信息
        """
        member = TeamMember(
            id=agent_id,
            name=name,
            role=role,
            capabilities=capabilities or []
        )
        
        self._members[agent_id] = member
        
        # 创建邮箱
        self._mailboxes[agent_id] = AsyncMailbox(agent_id)
        
        # 订阅消息总线
        self._message_bus.subscribe(agent_id, self._create_message_handler(agent_id))
        
        return member
    
    def remove_member(self, agent_id: str) -> bool:
        """移除团队成员"""
        if agent_id not in self._members:
            return False
        
        del self._members[agent_id]
        self._mailboxes.pop(agent_id, None)
        self._message_bus.unsubscribe(agent_id)
        
        return True
    
    def get_member(self, agent_id: str) -> Optional[TeamMember]:
        """获取成员信息"""
        return self._members.get(agent_id)
    
    def list_members(self) -> List[TeamMember]:
        """列出所有成员"""
        return list(self._members.values())
    
    def get_mailbox(self, agent_id: str) -> Optional[AsyncMailbox]:
        """获取成员邮箱"""
        return self._mailboxes.get(agent_id)
    
    def update_status(self, agent_id: str, status: str) -> None:
        """更新成员状态"""
        if agent_id in self._members:
            self._members[agent_id].status = status
    
    def find_capable_members(self, capability: str) -> List[TeamMember]:
        """查找具有特定能力的成员"""
        return [
            member for member in self._members.values()
            if capability in member.capabilities
        ]
    
    def find_idle_members(self) -> List[TeamMember]:
        """查找空闲成员"""
        return [
            member for member in self._members.values()
            if member.status == "idle"
        ]
    
    def assign_task(
        self,
        task: Dict[str, Any],
        assignee: str = None,
        capability_required: str = None
    ) -> Optional[str]:
        """
        分配任务
        
        Args:
            task: 任务信息
            assignee: 指定执行者
            capability_required: 需要的能力
        
        Returns:
            分配的 Agent ID，如果没有合适的成员返回 None
        """
        # 如果指定了执行者
        if assignee:
            if assignee in self._members:
                self._send_task(assignee, task)
                return assignee
            return None
        
        # 根据能力查找
        if capability_required:
            capable = self.find_capable_members(capability_required)
            if capable:
                # 选择空闲的成员
                idle = [m for m in capable if m.status == "idle"]
                if idle:
                    assignee = idle[0].id
                else:
                    assignee = capable[0].id
        
        # 如果还是没有，选择任意空闲成员
        if not assignee:
            idle = self.find_idle_members()
            if idle:
                assignee = idle[0].id
        
        if assignee:
            self._send_task(assignee, task)
            return assignee
        
        # 添加到任务队列
        self._task_queue.append(task)
        return None
    
    def _send_task(self, agent_id: str, task: Dict[str, Any]) -> None:
        """发送任务给成员"""
        mailbox = self._mailboxes.get(agent_id)
        if mailbox:
            mailbox.send(
                receiver=agent_id,
                subject=f"Task: {task.get('title', 'Untitled')}",
                content=task,
                priority=task.get('priority', 0)
            )
            
            # 更新状态
            self.update_status(agent_id, "busy")
    
    def broadcast_message(
        self,
        sender: str,
        content: Any,
        msg_type: MessageType = MessageType.NOTIFICATION
    ) -> None:
        """广播消息"""
        self._message_bus.broadcast(
            sender=sender,
            content=content,
            msg_type=msg_type
        )
    
    def send_message(
        self,
        sender: str,
        receiver: str,
        content: Any,
        msg_type: MessageType = MessageType.REQUEST
    ) -> None:
        """发送消息"""
        self._message_bus.send(
            sender=sender,
            receiver=receiver,
            content=content,
            msg_type=msg_type
        )
    
    def _create_message_handler(self, agent_id: str):
        """创建消息处理器"""
        def handler(message: BusMessage):
            mailbox = self._mailboxes.get(agent_id)
            if mailbox:
                mailbox.deliver(message)
        return handler
    
    def get_team_stats(self) -> Dict[str, Any]:
        """获取团队统计"""
        members = self.list_members()
        
        return {
            "team_id": self.team_id,
            "total_members": len(members),
            "idle": len([m for m in members if m.status == "idle"]),
            "busy": len([m for m in members if m.status == "busy"]),
            "offline": len([m for m in members if m.status == "offline"]),
            "pending_tasks": len(self._task_queue),
        }
