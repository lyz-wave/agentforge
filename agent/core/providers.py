"""
多模型支持模块

支持 Anthropic、OpenAI、DeepSeek 等多种模型
"""

import os
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod


class BaseModelProvider(ABC):
    """模型提供商基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def chat(
        self,
        messages: List[Dict],
        system: str = None,
        tools: List[Dict] = None,
        max_tokens: int = 8000,
    ) -> Dict[str, Any]:
        pass


class AnthropicProvider(BaseModelProvider):
    """Anthropic Claude 提供商"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    @property
    def name(self) -> str:
        return "anthropic"
    
    def chat(self, messages, system=None, tools=None, max_tokens=8000):
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["system"] = system
        if tools:
            kwargs["tools"] = tools
        
        response = self.client.messages.create(**kwargs)
        
        # 转换为统一格式
        content = []
        for block in response.content:
            if block.type == "text":
                content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input
                })
        
        return {
            "content": content,
            "stop_reason": response.stop_reason,
            "model": response.model,
        }


class OpenAIProvider(BaseModelProvider):
    """OpenAI 提供商"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
    
    @property
    def name(self) -> str:
        return "openai"
    
    def chat(self, messages, system=None, tools=None, max_tokens=8000):
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if system:
            kwargs["messages"] = [{"role": "system", "content": system}] + messages
        if tools:
            # 转换工具格式
            kwargs["tools"] = self._convert_tools(tools)
        
        response = self.client.chat.completions.create(**kwargs)
        
        # 转换为统一格式
        content = []
        choice = response.choices[0]
        
        if choice.message.content:
            content.append({"type": "text", "text": choice.message.content})
        
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                content.append({
                    "type": "tool_use",
                    "id": tc.id,
                    "name": tc.function.name,
                    "input": eval(tc.function.arguments)  # 简化处理
                })
        
        stop_reason = "tool_use" if choice.message.tool_calls else "end_turn"
        
        return {
            "content": content,
            "stop_reason": stop_reason,
            "model": response.model,
        }
    
    def _convert_tools(self, tools):
        """转换 Anthropic 工具格式为 OpenAI 格式"""
        converted = []
        for tool in tools:
            converted.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("input_schema", {})
                }
            })
        return converted


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek 提供商（基于 OpenAI API）"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat"):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://api.deepseek.com/v1"
        )
    
    @property
    def name(self) -> str:
        return "deepseek"


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter 提供商（支持多种模型）"""
    
    def __init__(self, api_key: str, model: str = "anthropic/claude-3.5-sonnet"):
        super().__init__(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1"
        )
    
    @property
    def name(self) -> str:
        return "openrouter"


class LocalProvider(OpenAIProvider):
    """本地模型提供商（如 Ollama、LM Studio）"""
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434/v1"):
        super().__init__(
            api_key="not-needed",
            model=model,
            base_url=base_url
        )
    
    @property
    def name(self) -> str:
        return "local"


def create_provider(
    provider: str = None,
    api_key: str = None,
    model: str = None,
    base_url: str = None,
) -> BaseModelProvider:
    """
    创建模型提供商
    
    Args:
        provider: 提供商名称 (anthropic, openai, deepseek, openrouter, local)
        api_key: API Key
        model: 模型名称
        base_url: 自定义 API 地址
    
    Returns:
        模型提供商实例
    """
    # 自动检测提供商
    if not provider:
        if os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("DEEPSEEK_API_KEY"):
            provider = "deepseek"
        elif os.getenv("OPENROUTER_API_KEY"):
            provider = "openrouter"
        else:
            provider = "local"
    
    # 获取 API Key
    if not api_key:
        env_keys = {
            "anthropic": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "deepseek": "DEEPSEEK_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }
        env_key = env_keys.get(provider)
        if env_key:
            api_key = os.getenv(env_key)
    
    # 创建提供商
    if provider == "anthropic":
        return AnthropicProvider(api_key=api_key, model=model or "claude-sonnet-4-20250514")
    elif provider == "openai":
        return OpenAIProvider(api_key=api_key, model=model or "gpt-4o")
    elif provider == "deepseek":
        return DeepSeekProvider(api_key=api_key, model=model or "deepseek-chat")
    elif provider == "openrouter":
        return OpenRouterProvider(api_key=api_key, model=model or "anthropic/claude-3.5-sonnet")
    elif provider == "local":
        return LocalProvider(model=model or "llama3", base_url=base_url or "http://localhost:11434/v1")
    else:
        raise ValueError(f"Unknown provider: {provider}")


# 快捷函数
def create_anthropic(api_key: str, model: str = "claude-sonnet-4-20250514") -> AnthropicProvider:
    return AnthropicProvider(api_key, model)

def create_openai(api_key: str, model: str = "gpt-4o") -> OpenAIProvider:
    return OpenAIProvider(api_key, model)

def create_deepseek(api_key: str, model: str = "deepseek-chat") -> DeepSeekProvider:
    return DeepSeekProvider(api_key, model)
