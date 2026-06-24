"""
消息总线 - Agent 间通信
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Callable
from pydantic import BaseModel, Field
from datetime import datetime
import asyncio
from collections import defaultdict


class MessageType(str, Enum):
    """消息类型"""
    REQUEST = "request"        # 请求
    RESPONSE = "response"      # 响应
    NOTIFICATION = "notification"  # 通知
    ERROR = "error"            # 错误
    HEARTBEAT = "heartbeat"    # 心跳


class BusMessage(BaseModel):
    """总线消息"""
    id: str
    type: MessageType
    sender: str
    receiver: str  # "*" 表示广播
    content: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MessageBus:
    """
    消息总线
    
    实现 Agent 间的异步消息传递
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._message_history: List[BusMessage] = []
        self._counter: int = 0
    
    def subscribe(self, agent_id: str, callback: Callable) -> None:
        """
        订阅消息
        
        Args:
            agent_id: Agent ID
            callback: 消息回调函数
        """
        self._subscribers[agent_id].append(callback)
    
    def unsubscribe(self, agent_id: str) -> None:
        """取消订阅"""
        self._subscribers.pop(agent_id, None)
    
    def publish(self, message: BusMessage) -> None:
        """
        发布消息
        
        Args:
            message: 要发布的消息
        """
        self._message_history.append(message)
        
        # 发送给特定接收者
        if message.receiver != "*":
            for callback in self._subscribers.get(message.receiver, []):
                try:
                    callback(message)
                except Exception as e:
                    print(f"Error delivering message to {message.receiver}: {e}")
        else:
            # 广播
            for agent_id, callbacks in self._subscribers.items():
                if agent_id != message.sender:
                    for callback in callbacks:
                        try:
                            callback(message)
                        except Exception as e:
                            print(f"Error broadcasting to {agent_id}: {e}")
    
    def send(
        self,
        sender: str,
        receiver: str,
        content: Any,
        msg_type: MessageType = MessageType.REQUEST,
        reply_to: str = None,
        metadata: Dict[str, Any] = None
    ) -> BusMessage:
        """
        发送消息
        
        Args:
            sender: 发送者
            receiver: 接收者
            content: 消息内容
            msg_type: 消息类型
            reply_to: 回复的消息 ID
            metadata: 元数据
        
        Returns:
            发送的消息
        """
        self._counter += 1
        message = BusMessage(
            id=f"msg_{self._counter}",
            type=msg_type,
            sender=sender,
            receiver=receiver,
            content=content,
            reply_to=reply_to,
            metadata=metadata or {}
        )
        
        self.publish(message)
        return message
    
    def broadcast(
        self,
        sender: str,
        content: Any,
        msg_type: MessageType = MessageType.NOTIFICATION,
        metadata: Dict[str, Any] = None
    ) -> BusMessage:
        """
        广播消息
        
        Args:
            sender: 发送者
            content: 消息内容
            msg_type: 消息类型
            metadata: 元数据
        
        Returns:
            广播的消息
        """
        return self.send(
            sender=sender,
            receiver="*",
            content=content,
            msg_type=msg_type,
            metadata=metadata
        )
    
    def get_history(
        self,
        agent_id: str = None,
        msg_type: MessageType = None,
        limit: int = 100
    ) -> List[BusMessage]:
        """
        获取消息历史
        
        Args:
            agent_id: Agent ID（过滤）
            msg_type: 消息类型（过滤）
            limit: 返回数量限制
        
        Returns:
            消息列表
        """
        messages = self._message_history
        
        if agent_id:
            messages = [
                m for m in messages
                if m.sender == agent_id or m.receiver == agent_id
            ]
        
        if msg_type:
            messages = [
                m for m in messages
                if m.type == msg_type
            ]
        
        return messages[-limit:]
    
    def clear_history(self) -> None:
        """清空消息历史"""
        self._message_history.clear()
