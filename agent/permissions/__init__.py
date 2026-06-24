"""
权限系统 - 三道闸门安全管线

实现权限控制机制：
1. 拒绝列表 - 永远禁止的操作
2. 规则匹配 - 需要检查的操作
3. 用户审批 - 需要用户确认的操作
"""

from agent.permissions.pipeline import PermissionPipeline, PermissionResult
from agent.permissions.rules import PermissionRule, DenyListRule, PathRule, CommandRule

# 创建全局权限管线
pipeline = PermissionPipeline()

__all__ = [
    "pipeline",
    "PermissionPipeline",
    "PermissionResult",
    "PermissionRule",
    "DenyListRule",
    "PathRule",
    "CommandRule",
]
