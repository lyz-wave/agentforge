"""
Agent Loop - 核心循环实现

实现 Agent 的核心循环模式：
1. 接收用户输入
2. 调用 LLM
3. 判断是否需要工具
4. 执行工具并返回结果
5. 循环直到完成
"""

import os
import uuid
import asyncio
from typing import List, Optional, Dict, Any, Callable, Union
from datetime import datetime

import anthropic
from dotenv import load_dotenv

from agent.core.message import Message, MessageRole, MessageHistory, ContentBlock
from agent.core.state import AgentState, AgentStatus

# 加载环境变量
load_dotenv()


class Agent:
    """
    Agent 核心类
    
    实现基于 Claude Code 架构的 Agent 循环
    """
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_handlers: Optional[Dict[str, Callable]] = None,
        max_turns: int = 100,
        max_tokens: int = 8000,
        api_key: Optional[str] = None,
    ):
        """
        初始化 Agent
        
        Args:
            model: 模型名称
            system_prompt: 系统提示词
            tools: 工具定义列表
            tool_handlers: 工具处理函数字典
            max_turns: 最大轮次
            max_tokens: 最大 token 数
            api_key: Anthropic API Key
        """
        # 模型配置
        self.model = model
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.max_turns = max_turns
        self.max_tokens = max_tokens
        
        # API 客户端
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # 工具系统
        self.tools = tools or []
        self.tool_handlers = tool_handlers or {}
        
        # 状态管理
        self.state = AgentState()
        self.history = MessageHistory()
        
        # Hook 系统（将在后续实现）
        self._hooks: Dict[str, List[Callable]] = {
            "UserPromptSubmit": [],
            "PreToolUse": [],
            "PostToolUse": [],
            "Stop": [],
        }
    
    def _default_system_prompt(self) -> str:
        """默认系统提示词"""
        return """You are a helpful AI assistant with access to various tools.

When you need to perform actions, use the available tools.
Always think step by step and explain your reasoning.
If you encounter errors, try to fix them or ask for clarification.

Available capabilities:
- Execute shell commands
- Read and write files
- Search for files and content
- And more...
"""
    
    def register_hook(self, event: str, callback: Callable) -> None:
        """
        注册 Hook
        
        Args:
            event: 事件名称 (UserPromptSubmit, PreToolUse, PostToolUse, Stop)
            callback: 回调函数
        """
        if event not in self._hooks:
            raise ValueError(f"Unknown hook event: {event}")
        self._hooks[event].append(callback)
    
    def _trigger_hooks(self, event: str, *args) -> Optional[str]:
        """
        触发 Hook
        
        Args:
            event: 事件名称
            *args: 传递给回调的参数
        
        Returns:
            如果有 Hook 返回非 None 值，返回该值（用于阻止操作）
        """
        for callback in self._hooks.get(event, []):
            result = callback(*args)
            if result is not None:
                return result
        return None
    
    def run(self, query: str, verbose: bool = False) -> str:
        """
        执行用户查询（同步版本）
        
        Args:
            query: 用户查询
            verbose: 是否显示详细信息
        
        Returns:
            Agent 的最终响应
        """
        # 生成会话 ID
        session_id = str(uuid.uuid4())[:8]
        
        # 初始化状态
        self.state.start(session_id, self.model)
        self.history.clear()
        
        # 添加用户消息
        self.history.add_user(query)
        
        # 触发 UserPromptSubmit Hook
        hook_result = self._trigger_hooks("UserPromptSubmit", query)
        if hook_result:
            return hook_result
        
        try:
            # 执行 Agent Loop
            response = self._agent_loop(verbose)
            
            # 停止状态
            self.state.stop()
            
            return response
            
        except Exception as e:
            self.state.error(str(e))
            raise
    
    def _agent_loop(self, verbose: bool = False) -> str:
        """
        Agent 核心循环
        
        这是 Agent 的核心，实现了 while True 循环模式
        """
        while True:
            # 检查是否超过最大轮次
            if self.state.has_exceeded_max_turns():
                return f"Error: Exceeded maximum turns ({self.max_turns})"
            
            # 增加轮次
            self.state.increment_turn()
            
            if verbose:
                print(f"\n--- Turn {self.state.turn_count} ---")
            
            # 调用 LLM
            response = self._call_llm()
            
            # 添加助手消息到历史
            self.history.add_assistant(response.content)
            
            # 检查是否需要继续（是否有工具调用）
            if not self._has_tool_use(response):
                # 没有工具调用，提取文本响应
                final_text = self._extract_text(response)
                
                # 触发 Stop Hook
                hook_result = self._trigger_hooks("Stop", self.history.messages)
                if hook_result:
                    # Hook 要求继续
                    self.history.add_user(hook_result)
                    continue
                
                return final_text
            
            # 执行工具调用
            tool_results = self._execute_tools(response, verbose)
            
            # 添加工具结果到历史
            self.history.add_tool_results(tool_results)
    
    def _call_llm(self) -> anthropic.types.Message:
        """调用 LLM"""
        messages = self.history.get_messages()
        
        # 准备工具定义
        tools_param = self.tools if self.tools else anthropic.NOT_GIVEN
        
        return self.client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=messages,
            tools=tools_param,
            max_tokens=self.max_tokens,
        )
    
    def _has_tool_use(self, response: anthropic.types.Message) -> bool:
        """检查响应是否包含工具调用"""
        for block in response.content:
            if block.type == "tool_use":
                return True
        return False
    
    def _extract_text(self, response: anthropic.types.Message) -> str:
        """从响应中提取文本"""
        texts = []
        for block in response.content:
            if hasattr(block, "text"):
                texts.append(block.text)
        return "\n".join(texts) if texts else ""
    
    def _execute_tools(
        self, 
        response: anthropic.types.Message, 
        verbose: bool = False
    ) -> List[Dict[str, Any]]:
        """
        执行工具调用
        
        Args:
            response: LLM 响应
            verbose: 是否显示详细信息
        
        Returns:
            工具结果列表
        """
        results = []
        
        for block in response.content:
            if block.type != "tool_use":
                continue
            
            tool_name = block.name
            tool_input = block.input
            tool_id = block.id
            
            if verbose:
                print(f"  Tool: {tool_name}({tool_input})")
            
            # 触发 PreToolUse Hook
            hook_result = self._trigger_hooks("PreToolUse", block)
            if hook_result:
                # Hook 阻止了工具执行
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": str(hook_result),
                    "is_error": True,
                })
                self.state.record_tool_call(tool_name, False)
                continue
            
            # 执行工具
            try:
                handler = self.tool_handlers.get(tool_name)
                if not handler:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                output = handler(**tool_input)
                
                # 触发 PostToolUse Hook
                self._trigger_hooks("PostToolUse", block, output)
                
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": str(output),
                    "is_error": False,
                })
                self.state.record_tool_call(tool_name, True)
                
                if verbose:
                    print(f"    Result: {output[:100]}...")
                
            except Exception as e:
                error_msg = f"Error executing {tool_name}: {str(e)}"
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": error_msg,
                    "is_error": True,
                })
                self.state.record_tool_call(tool_name, False)
                
                if verbose:
                    print(f"    Error: {error_msg}")
        
        return results
    
    def get_state_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return self.state.get_summary()
    
    def print_summary(self) -> None:
        """打印状态摘要"""
        summary = self.get_state_summary()
        print("\n=== Agent Summary ===")
        print(f"Status: {summary['status']}")
        print(f"Session: {summary['session_id']}")
        print(f"Turns: {summary['turn_count']}")
        print(f"Duration: {summary['duration']:.2f}s")
        print(f"Tool Calls: {summary['tool_stats']['total']}")
        print(f"  Successful: {summary['tool_stats']['successful']}")
        print(f"  Failed: {summary['tool_stats']['failed']}")
        if summary['tool_stats']['top_tools']:
            print("Top Tools:")
            for tool, count in summary['tool_stats']['top_tools'].items():
                print(f"  - {tool}: {count}")


class AsyncAgent(Agent):
    """
    异步 Agent
    
    支持异步执行的 Agent 版本
    """
    
    async def arun(self, query: str, verbose: bool = False) -> str:
        """
        异步执行用户查询
        
        Args:
            query: 用户查询
            verbose: 是否显示详细信息
        
        Returns:
            Agent 的最终响应
        """
        # 生成会话 ID
        session_id = str(uuid.uuid4())[:8]
        
        # 初始化状态
        self.state.start(session_id, self.model)
        self.history.clear()
        
        # 添加用户消息
        self.history.add_user(query)
        
        # 触发 UserPromptSubmit Hook
        hook_result = self._trigger_hooks("UserPromptSubmit", query)
        if hook_result:
            return hook_result
        
        try:
            # 执行 Agent Loop
            response = await self._async_agent_loop(verbose)
            
            # 停止状态
            self.state.stop()
            
            return response
            
        except Exception as e:
            self.state.error(str(e))
            raise
    
    async def _async_agent_loop(self, verbose: bool = False) -> str:
        """异步 Agent 核心循环"""
        while True:
            # 检查是否超过最大轮次
            if self.state.has_exceeded_max_turns():
                return f"Error: Exceeded maximum turns ({self.max_turns})"
            
            # 增加轮次
            self.state.increment_turn()
            
            if verbose:
                print(f"\n--- Turn {self.state.turn_count} ---")
            
            # 调用 LLM（异步）
            response = await self._async_call_llm()
            
            # 添加助手消息到历史
            self.history.add_assistant(response.content)
            
            # 检查是否需要继续
            if not self._has_tool_use(response):
                final_text = self._extract_text(response)
                
                # 触发 Stop Hook
                hook_result = self._trigger_hooks("Stop", self.history.messages)
                if hook_result:
                    self.history.add_user(hook_result)
                    continue
                
                return final_text
            
            # 执行工具调用
            tool_results = self._execute_tools(response, verbose)
            
            # 添加工具结果到历史
            self.history.add_tool_results(tool_results)
    
    async def _async_call_llm(self) -> anthropic.types.Message:
        """异步调用 LLM"""
        messages = self.history.get_messages()
        tools_param = self.tools if self.tools else anthropic.NOT_GIVEN
        
        # 使用异步客户端
        async with anthropic.AsyncAnthropic() as async_client:
            return await async_client.messages.create(
                model=self.model,
                system=self.system_prompt,
                messages=messages,
                tools=tools_param,
                max_tokens=self.max_tokens,
            )
