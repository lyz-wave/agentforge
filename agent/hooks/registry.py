"""
Hook 注册表 - 管理扩展点
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Callable
from pydantic import BaseModel


class HookEvent(str, Enum):
    """Hook 事件枚举"""
    USER_PROMPT_SUBMIT = "UserPromptSubmit"
    PRE_TOOL_USE = "PreToolUse"
    POST_TOOL_USE = "PostToolUse"
    STOP = "Stop"


class HookResult(BaseModel):
    """Hook 结果"""
    should_continue: bool = True
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class HookCallback:
    """Hook 回调包装器"""
    
    def __init__(
        self, 
        callback: Callable,
        name: str,
        priority: int = 0,
        description: str = ""
    ):
        self.callback = callback
        self.name = name
        self.priority = priority
        self.description = description
    
    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)


class HookRegistry:
    """
    Hook 注册表
    
    管理所有 Hook 的注册和触发
    """
    
    def __init__(self):
        self._hooks: Dict[str, List[HookCallback]] = {
            event.value: [] for event in HookEvent
        }
    
    def register(
        self, 
        event: str, 
        callback: Callable,
        name: str = None,
        priority: int = 0,
        description: str = ""
    ) -> None:
        """
        注册 Hook
        
        Args:
            event: 事件名称
            callback: 回调函数
            name: Hook 名称（用于调试）
            priority: 优先级（越高越先执行）
            description: 描述
        """
        if event not in self._hooks:
            raise ValueError(f"Unknown hook event: {event}")
        
        hook = HookCallback(
            callback=callback,
            name=name or callback.__name__,
            priority=priority,
            description=description
        )
        
        self._hooks[event].append(hook)
        
        # 按优先级排序
        self._hooks[event].sort(key=lambda h: h.priority, reverse=True)
    
    def unregister(self, event: str, name: str) -> None:
        """
        注销 Hook
        
        Args:
            event: 事件名称
            name: Hook 名称
        """
        if event in self._hooks:
            self._hooks[event] = [
                h for h in self._hooks[event] 
                if h.name != name
            ]
    
    def trigger(self, event: str, *args, **kwargs) -> Optional[str]:
        """
        触发 Hook
        
        Args:
            event: 事件名称
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            如果有 Hook 返回非 None 值，返回该值
        """
        if event not in self._hooks:
            return None
        
        for hook in self._hooks[event]:
            try:
                result = hook(*args, **kwargs)
                if result is not None:
                    return result
            except Exception as e:
                # Hook 执行失败，记录错误但继续执行
                print(f"Warning: Hook '{hook.name}' failed: {e}")
        
        return None
    
    def list_hooks(self, event: str = None) -> Dict[str, List[str]]:
        """
        列出所有 Hook
        
        Args:
            event: 事件名称（可选）
        
        Returns:
            Hook 列表
        """
        if event:
            return {
                event: [h.name for h in self._hooks.get(event, [])]
            }
        
        return {
            event: [h.name for h in hooks]
            for event, hooks in self._hooks.items()
        }
    
    def clear(self, event: str = None) -> None:
        """
        清空 Hook
        
        Args:
            event: 事件名称（可选，如果为 None 则清空所有）
        """
        if event:
            self._hooks[event] = []
        else:
            for event in self._hooks:
                self._hooks[event] = []


# 预定义的 Hook 处理器

def log_hook(event: str, *args, **kwargs) -> None:
    """日志 Hook - 记录事件"""
    print(f"[HOOK] {event}: {args}")


def permission_hook(block) -> Optional[str]:
    """权限 Hook - 检查权限"""
    # 这里可以集成权限系统
    return None


def summary_hook(messages: list) -> Optional[str]:
    """摘要 Hook - 在停止时打印摘要"""
    tool_count = sum(
        1 for m in messages
        for b in (m.get("content") if isinstance(m.get("content"), list) else [])
        if isinstance(b, dict) and b.get("type") == "tool_result"
    )
    print(f"\n[HOOK] Session used {tool_count} tool calls")
    return None
