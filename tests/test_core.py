"""
测试文件 - Agent 核心功能测试
"""

import pytest
from unittest.mock import Mock, patch

from agent.core.message import Message, MessageRole, MessageHistory
from agent.core.state import AgentState, AgentStatus


class TestMessage:
    """测试消息类"""
    
    def test_create_user_message(self):
        """测试创建用户消息"""
        msg = Message.user("Hello")
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello"
    
    def test_create_assistant_message(self):
        """测试创建助手消息"""
        msg = Message.assistant("Hi there")
        assert msg.role == MessageRole.ASSISTANT
        assert msg.content == "Hi there"
    
    def test_message_to_dict(self):
        """测试消息转换为字典"""
        msg = Message.user("Test")
        d = msg.to_dict()
        assert d["role"] == "user"
        assert d["content"] == "Test"


class TestMessageHistory:
    """测试消息历史"""
    
    def test_add_message(self):
        """测试添加消息"""
        history = MessageHistory()
        history.add_user("Hello")
        assert len(history) == 1
    
    def test_get_messages(self):
        """测试获取消息"""
        history = MessageHistory()
        history.add_user("Hello")
        history.add_assistant("Hi")
        
        messages = history.get_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
    
    def test_clear_history(self):
        """测试清空历史"""
        history = MessageHistory()
        history.add_user("Hello")
        history.clear()
        assert len(history) == 0


class TestAgentState:
    """测试 Agent 状态"""
    
    def test_initial_state(self):
        """测试初始状态"""
        state = AgentState()
        assert state.status == AgentStatus.IDLE
        assert state.turn_count == 0
    
    def test_start_session(self):
        """测试开始会话"""
        state = AgentState()
        state.start("test_session", "claude-sonnet-4-20250514")
        
        assert state.status == AgentStatus.RUNNING
        assert state.session_id == "test_session"
        assert state.current_model == "claude-sonnet-4-20250514"
    
    def test_record_tool_call(self):
        """测试记录工具调用"""
        state = AgentState()
        state.record_tool_call("bash", True)
        state.record_tool_call("bash", True)
        state.record_tool_call("read_file", False)
        
        assert state.tool_stats.total_calls == 3
        assert state.tool_stats.successful_calls == 2
        assert state.tool_stats.failed_calls == 1
        assert state.tool_stats.tool_counts["bash"] == 2
    
    def test_max_turns_check(self):
        """测试最大轮次检查"""
        state = AgentState()
        state.max_turns = 5
        
        for i in range(4):
            state.increment_turn()
            assert not state.has_exceeded_max_turns()
        
        state.increment_turn()
        assert state.has_exceeded_max_turns()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
