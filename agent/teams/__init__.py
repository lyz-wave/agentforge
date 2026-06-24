"""
团队协作系统 - 多 Agent 协作

实现消息总线、异步邮箱、权限冒泡等功能
"""

from agent.teams.bus import MessageBus, MessageType
from agent.teams.mailbox import AsyncMailbox, MailMessage
from agent.teams.coordinator import TeamCoordinator

# 创建全局组件
message_bus = MessageBus()

__all__ = [
    "message_bus",
    "MessageBus",
    "MessageType",
    "AsyncMailbox",
    "MailMessage",
    "TeamCoordinator",
]
