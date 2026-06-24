"""
异步邮箱 - Agent 的消息队列
"""

import asyncio
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from collections import deque


class MailMessage(BaseModel):
    """邮件消息"""
    id: str
    sender: str
    subject: str
    content: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    read: bool = False
    priority: int = 0  # 优先级，越高越重要
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AsyncMailbox:
    """
    异步邮箱
    
    为每个 Agent 提供异步消息队列
    """
    
    def __init__(self, agent_id: str, max_size: int = 1000):
        self.agent_id = agent_id
        self.max_size = max_size
        self._inbox: deque = deque(maxlen=max_size)
        self._outbox: deque = deque(maxlen=max_size)
        self._counter: int = 0
        self._event = asyncio.Event()
    
    async def receive(self, timeout: float = None) -> Optional[MailMessage]:
        """
        接收消息（异步等待）
        
        Args:
            timeout: 超时时间（秒）
        
        Returns:
            接收到的消息，超时返回 None
        """
        if self._inbox:
            message = self._inbox.popleft()
            message.read = True
            return message
        
        # 等待新消息
        try:
            await asyncio.wait_for(self._event.wait(), timeout=timeout)
            if self._inbox:
                message = self._inbox.popleft()
                message.read = True
                return message
        except asyncio.TimeoutError:
            pass
        
        return None
    
    def receive_nowait(self) -> Optional[MailMessage]:
        """
        接收消息（不等待）
        
        Returns:
            接收到的消息，没有返回 None
        """
        if self._inbox:
            message = self._inbox.popleft()
            message.read = True
            return message
        return None
    
    def send(
        self,
        receiver: str,
        subject: str,
        content: Any,
        priority: int = 0,
        metadata: Dict[str, Any] = None
    ) -> MailMessage:
        """
        发送消息
        
        Args:
            receiver: 接收者
            subject: 主题
            content: 内容
            priority: 优先级
            metadata: 元数据
        
        Returns:
            发送的消息
        """
        self._counter += 1
        message = MailMessage(
            id=f"mail_{self._counter}",
            sender=self.agent_id,
            subject=subject,
            content=content,
            priority=priority,
            metadata=metadata or {}
        )
        
        self._outbox.append(message)
        return message
    
    def deliver(self, message: MailMessage) -> None:
        """
        投递消息到收件箱
        
        Args:
            message: 要投递的消息
        """
        self._inbox.append(message)
        self._event.set()
        self._event.clear()
    
    def get_inbox(self, unread_only: bool = False) -> List[MailMessage]:
        """
        获取收件箱消息
        
        Args:
            unread_only: 是否只返回未读消息
        
        Returns:
            消息列表
        """
        if unread_only:
            return [m for m in self._inbox if not m.read]
        return list(self._inbox)
    
    def get_outbox(self) -> List[MailMessage]:
        """获取发件箱消息"""
        return list(self._outbox)
    
    def mark_read(self, message_id: str) -> bool:
        """标记消息为已读"""
        for msg in self._inbox:
            if msg.id == message_id:
                msg.read = True
                return True
        return False
    
    def mark_all_read(self) -> int:
        """标记所有消息为已读"""
        count = 0
        for msg in self._inbox:
            if not msg.read:
                msg.read = True
                count += 1
        return count
    
    def clear_inbox(self) -> int:
        """清空收件箱"""
        count = len(self._inbox)
        self._inbox.clear()
        return count
    
    def clear_outbox(self) -> int:
        """清空发件箱"""
        count = len(self._outbox)
        self._outbox.clear()
        return count
    
    @property
    def unread_count(self) -> int:
        """未读消息数量"""
        return sum(1 for m in self._inbox if not m.read)
    
    @property
    def total_count(self) -> int:
        """总消息数量"""
        return len(self._inbox)
