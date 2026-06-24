"""
工具注册表 - 管理工具的注册和分发
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    def to_schema(self) -> Dict[str, Any]:
        """转换为 Anthropic API 格式"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


class Tool(ABC):
    """
    工具基类
    
    所有工具都必须继承此类并实现 execute 方法
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """工具参数定义"""
        return {}
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
        
        Returns:
            执行结果字符串
        """
        pass
    
    def get_definition(self) -> ToolDefinition:
        """获取工具定义"""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具 Schema（用于 API 调用）"""
        return self.get_definition().to_schema()


class ToolRegistry:
    """
    工具注册表
    
    管理所有可用工具的注册和分发
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, tool: Tool) -> None:
        """
        注册工具
        
        Args:
            tool: 工具实例
        """
        self._tools[tool.name] = tool
        self._handlers[tool.name] = tool.execute
    
    def unregister(self, tool_name: str) -> None:
        """
        注销工具
        
        Args:
            tool_name: 工具名称
        """
        self._tools.pop(tool_name, None)
        self._handlers.pop(tool_name, None)
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """
        获取工具实例
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具实例，如果不存在返回 None
        """
        return self._tools.get(tool_name)
    
    def get_handler(self, tool_name: str) -> Optional[Callable]:
        """
        获取工具处理函数
        
        Args:
            tool_name: 工具名称
        
        Returns:
            处理函数，如果不存在返回 None
        """
        return self._handlers.get(tool_name)
    
    def get_schemas(self, tool_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        获取工具 Schema 列表
        
        Args:
            tool_names: 工具名称列表，如果为 None 则返回所有工具
        
        Returns:
            工具 Schema 列表
        """
        if tool_names is None:
            tools = self._tools.values()
        else:
            tools = [self._tools[name] for name in tool_names if name in self._tools]
        
        return [tool.get_schema() for tool in tools]
    
    def get_handlers(self, tool_names: Optional[List[str]] = None) -> Dict[str, Callable]:
        """
        获取工具处理函数字典
        
        Args:
            tool_names: 工具名称列表，如果为 None 则返回所有工具
        
        Returns:
            处理函数字典
        """
        if tool_names is None:
            return self._handlers.copy()
        
        return {
            name: handler 
            for name, handler in self._handlers.items() 
            if name in tool_names
        }
    
    def list_tools(self) -> List[str]:
        """列出所有工具名称"""
        return list(self._tools.keys())
    
    def has_tool(self, tool_name: str) -> bool:
        """检查工具是否存在"""
        return tool_name in self._tools
    
    def execute(self, tool_name: str, **kwargs) -> str:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            **kwargs: 工具参数
        
        Returns:
            执行结果
        
        Raises:
            ValueError: 工具不存在
        """
        handler = self.get_handler(tool_name)
        if not handler:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return handler(**kwargs)
