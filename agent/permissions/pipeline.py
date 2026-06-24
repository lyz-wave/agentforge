"""
权限管线 - 实现三道闸门检查
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from agent.permissions.rules import PermissionRule


class PermissionResult(str, Enum):
    """权限检查结果"""
    ALLOW = "allow"          # 允许执行
    DENY = "deny"            # 拒绝执行
    ASK = "ask"              # 需要用户确认


class PermissionDecision(BaseModel):
    """权限决策"""
    result: PermissionResult
    reason: Optional[str] = None
    rule_name: Optional[str] = None


class PermissionPipeline:
    """
    权限管线
    
    实现三道闸门的权限检查机制
    """
    
    def __init__(self):
        self._rules: List[PermissionRule] = []
        self._deny_patterns: List[str] = [
            "rm -rf /",
            "sudo",
            "shutdown",
            "reboot",
            "mkfs",
            "dd if=",
            "> /dev/sda",
        ]
    
    def add_rule(self, rule: PermissionRule) -> None:
        """添加权限规则"""
        self._rules.append(rule)
    
    def add_deny_pattern(self, pattern: str) -> None:
        """添加拒绝模式"""
        self._deny_patterns.append(pattern)
    
    def check(self, tool_name: str, tool_input: Dict[str, Any]) -> PermissionDecision:
        """
        检查权限
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
        
        Returns:
            权限决策
        """
        # 闸门 1: 拒绝列表检查
        deny_result = self._check_deny_list(tool_name, tool_input)
        if deny_result:
            return PermissionDecision(
                result=PermissionResult.DENY,
                reason=deny_result,
                rule_name="deny_list"
            )
        
        # 闸门 2: 规则匹配检查
        for rule in self._rules:
            if rule.matches(tool_name, tool_input):
                # 闸门 3: 根据规则类型决定
                if rule.should_ask():
                    return PermissionDecision(
                        result=PermissionResult.ASK,
                        reason=rule.get_reason(),
                        rule_name=rule.name
                    )
                elif rule.should_deny():
                    return PermissionDecision(
                        result=PermissionResult.DENY,
                        reason=rule.get_reason(),
                        rule_name=rule.name
                    )
        
        # 默认允许
        return PermissionDecision(result=PermissionResult.ALLOW)
    
    def _check_deny_list(self, tool_name: str, tool_input: Dict[str, Any]) -> Optional[str]:
        """
        检查拒绝列表
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
        
        Returns:
            如果被拒绝，返回原因；否则返回 None
        """
        # 只检查 bash 工具的命令
        if tool_name == "bash":
            command = tool_input.get("command", "")
            for pattern in self._deny_patterns:
                if pattern in command:
                    return f"Blocked: '{pattern}' is on the deny list"
        
        return None
    
    def ask_user(self, tool_name: str, tool_input: Dict[str, Any], reason: str) -> PermissionResult:
        """
        询问用户
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
            reason: 需要确认的原因
        
        Returns:
            用户的决策
        """
        print(f"\n⚠️  {reason}")
        print(f"   Tool: {tool_name}")
        print(f"   Input: {tool_input}")
        
        try:
            choice = input("   Allow? [y/N] ").strip().lower()
            if choice in ("y", "yes"):
                return PermissionResult.ALLOW
            else:
                return PermissionResult.DENY
        except (EOFError, KeyboardInterrupt):
            return PermissionResult.DENY
