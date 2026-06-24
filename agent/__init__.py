"""
AgentForge - 智能任务自动化框架

基于 Claude Code 架构的现代 Agent 框架
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from agent.core.loop import Agent
from agent.core.message import Message, MessageRole
from agent.core.state import AgentState

__all__ = ["Agent", "Message", "MessageRole", "AgentState"]
