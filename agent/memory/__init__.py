"""
记忆系统 - 持久化记忆和上下文管理

实现记忆的选择、提取、consolidation 功能
"""

from agent.memory.store import MemoryStore, MemoryEntry
from agent.memory.compaction import ContextCompactor

# 创建全局记忆存储
memory_store = MemoryStore()

__all__ = [
    "memory_store",
    "MemoryStore",
    "MemoryEntry",
    "ContextCompactor",
]
