"""
Hook 系统 - 扩展点机制

实现 4 个核心事件的扩展点：
- UserPromptSubmit: 用户输入提交后
- PreToolUse: 工具执行前
- PostToolUse: 工具执行后
- Stop: 循环即将退出时
"""

from agent.hooks.registry import HookRegistry, HookEvent, HookResult

# 创建全局 Hook 注册表
registry = HookRegistry()

__all__ = [
    "registry",
    "HookRegistry",
    "HookEvent",
    "HookResult",
]
