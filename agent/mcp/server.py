"""
MCP 服务器 - 提供工具给其他 Agent
"""

import json
from typing import Dict, Any, List, Callable, Optional
from pydantic import BaseModel


class MCPToolDefinition(BaseModel):
    """MCP 工具定义"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPServer:
    """
    MCP 服务器
    
    提供工具给其他 Agent 使用
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ) -> None:
        """注册工具"""
        self._tools[name] = {
            "name": name,
            "description": description,
            "input_schema": input_schema,
        }
        self._handlers[name] = handler
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具"""
        return list(self._tools.values())
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具"""
        handler = self._handlers.get(name)
        if not handler:
            raise ValueError(f"Unknown tool: {name}")
        
        return handler(**arguments)
    
    def get_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "name": self.name,
            "version": self.version,
            "tools_count": len(self._tools),
        }
