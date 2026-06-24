"""
Message 模块 - 消息管理

定义消息类型和消息管理功能
"""

from enum import Enum
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ToolUse(BaseModel):
    """工具调用块"""
    type: str = "tool_use"
    id: str
    name: str
    input: Dict[str, Any]


class ToolResult(BaseModel):
    """工具结果块"""
    type: str = "tool_result"
    tool_use_id: str
    content: str
    is_error: bool = False


class TextBlock(BaseModel):
    """文本块"""
    type: str = "text"
    text: str


# 内容块类型
ContentBlock = Union[ToolUse, ToolResult, TextBlock, Dict[str, Any]]


class Message(BaseModel):
    """
    消息类
    
    表示 Agent 对话中的单条消息
    """
    role: MessageRole
    content: Union[str, List[ContentBlock]]
    
    class Config:
        use_enum_values = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 格式"""
        if isinstance(self.content, str):
            return {
                "role": self.role,
                "content": self.content
            }
        
        # 处理列表内容
        content_list = []
        for block in self.content:
            if isinstance(block, BaseModel):
                content_list.append(block.dict())
            elif isinstance(block, dict):
                content_list.append(block)
            else:
                content_list.append({"type": "text", "text": str(block)})
        
        return {
            "role": self.role,
            "content": content_list
        }
    
    @classmethod
    def user(cls, content: str) -> "Message":
        """创建用户消息"""
        return cls(role=MessageRole.USER, content=content)
    
    @classmethod
    def assistant(cls, content: Union[str, List[ContentBlock]]) -> "Message":
        """创建助手消息"""
        return cls(role=MessageRole.ASSISTANT, content=content)
    
    @classmethod
    def system(cls, content: str) -> "Message":
        """创建系统消息"""
        return cls(role=MessageRole.SYSTEM, content=content)
    
    @classmethod
    def tool_result(cls, tool_use_id: str, content: str, is_error: bool = False) -> "Message":
        """创建工具结果消息"""
        return cls(
            role=MessageRole.USER,
            content=[ToolResult(
                tool_use_id=tool_use_id,
                content=content,
                is_error=is_error
            )]
        )


class MessageHistory:
    """
    消息历史管理器
    
    管理 Agent 对话的消息历史
    """
    
    def __init__(self, max_messages: int = 100):
        self.messages: List[Message] = []
        self.max_messages = max_messages
    
    def add(self, message: Message) -> None:
        """添加消息"""
        self.messages.append(message)
        # 限制消息数量
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
    
    def add_user(self, content: str) -> None:
        """添加用户消息"""
        self.add(Message.user(content))
    
    def add_assistant(self, content: Union[str, List[ContentBlock]]) -> None:
        """添加助手消息"""
        self.add(Message.assistant(content))
    
    def add_tool_result(self, tool_use_id: str, content: str, is_error: bool = False) -> None:
        """添加工具结果"""
        self.add(Message.tool_result(tool_use_id, content, is_error))
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """获取所有消息（API 格式）"""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self) -> None:
        """清空消息历史"""
        self.messages.clear()
    
    def __len__(self) -> int:
        return len(self.messages)
    
    def __getitem__(self, index: int) -> Message:
        return self.messages[index]
