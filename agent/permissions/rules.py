"""
权限规则 - 定义各种权限检查规则
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path


class PermissionRule(ABC):
    """
    权限规则基类
    
    所有权限规则都必须继承此类
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """规则名称"""
        pass
    
    @abstractmethod
    def matches(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """
        检查规则是否匹配
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
        
        Returns:
            是否匹配
        """
        pass
    
    @abstractmethod
    def should_ask(self) -> bool:
        """是否需要询问用户"""
        pass
    
    @abstractmethod
    def should_deny(self) -> bool:
        """是否应该拒绝"""
        pass
    
    @abstractmethod
    def get_reason(self) -> str:
        """获取原因说明"""
        pass


class DenyListRule(PermissionRule):
    """
    拒绝列表规则
    
    检查命令是否包含禁止的模式
    """
    
    def __init__(self, patterns: List[str]):
        self.patterns = patterns
    
    @property
    def name(self) -> str:
        return "deny_list"
    
    def matches(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """检查是否匹配拒绝模式"""
        if tool_name != "bash":
            return False
        
        command = tool_input.get("command", "")
        return any(pattern in command for pattern in self.patterns)
    
    def should_ask(self) -> bool:
        return False
    
    def should_deny(self) -> bool:
        return True
    
    def get_reason(self) -> str:
        return "Command contains forbidden pattern"


class PathRule(PermissionRule):
    """
    路径规则
    
    检查文件操作是否在允许的目录内
    """
    
    def __init__(
        self, 
        allowed_paths: List[str],
        tools: List[str] = None,
        ask_outside: bool = True
    ):
        self.allowed_paths = [Path(p).resolve() for p in allowed_paths]
        self.tools = tools or ["read_file", "write_file", "edit_file"]
        self.ask_outside = ask_outside
    
    @property
    def name(self) -> str:
        return "path_rule"
    
    def matches(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """检查是否匹配路径规则"""
        if tool_name not in self.tools:
            return False
        
        path = tool_input.get("path", "")
        if not path:
            return False
        
        # 检查路径是否在允许的目录内
        try:
            resolved_path = Path(path).resolve()
            return not any(
                resolved_path.is_relative_to(allowed)
                for allowed in self.allowed_paths
            )
        except (ValueError, OSError):
            return True
    
    def should_ask(self) -> bool:
        return self.ask_outside
    
    def should_deny(self) -> bool:
        return not self.ask_outside
    
    def get_reason(self) -> str:
        return "File operation outside allowed directories"


class CommandRule(PermissionRule):
    """
    命令规则
    
    检查特定命令模式
    """
    
    def __init__(
        self, 
        patterns: List[str],
        action: str = "ask",  # "ask" or "deny"
        reason: str = None
    ):
        self.patterns = patterns
        self.action = action
        self._reason = reason
    
    @property
    def name(self) -> str:
        return "command_rule"
    
    def matches(self, tool_name: str, tool_input: Dict[str, Any]) -> bool:
        """检查是否匹配命令模式"""
        if tool_name != "bash":
            return False
        
        command = tool_input.get("command", "")
        return any(pattern in command for pattern in self.patterns)
    
    def should_ask(self) -> bool:
        return self.action == "ask"
    
    def should_deny(self) -> bool:
        return self.action == "deny"
    
    def get_reason(self) -> str:
        return self._reason or "Command requires confirmation"
