"""
工具系统 - 实现工具注册和执行

提供可扩展的工具系统，支持动态注册和分发
"""

from agent.tools.registry import ToolRegistry, Tool, ToolDefinition
from agent.tools.bash import BashTool
from agent.tools.file import ReadFileTool, WriteFileTool, EditFileTool
from agent.tools.glob import GlobTool

# 创建全局工具注册表
registry = ToolRegistry()

# 注册内置工具
registry.register(BashTool())
registry.register(ReadFileTool())
registry.register(WriteFileTool())
registry.register(EditFileTool())
registry.register(GlobTool())

__all__ = [
    "registry",
    "ToolRegistry",
    "Tool",
    "ToolDefinition",
    "BashTool",
    "ReadFileTool",
    "WriteFileTool",
    "EditFileTool",
    "GlobTool",
]
