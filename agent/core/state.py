"""
State 模块 - Agent 状态管理

管理 Agent 的运行状态
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class AgentStatus(str, Enum):
    """Agent 状态枚举"""
    IDLE = "idle"              # 空闲
    RUNNING = "running"        # 运行中
    WAITING = "waiting"        # 等待用户输入
    ERROR = "error"            # 错误状态
    COMPLETED = "completed"    # 完成


class ToolCallStats(BaseModel):
    """工具调用统计"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    tool_counts: Dict[str, int] = Field(default_factory=dict)


class AgentState(BaseModel):
    """
    Agent 状态类
    
    记录 Agent 的运行状态和统计信息
    """
    # 基本状态
    status: AgentStatus = AgentStatus.IDLE
    session_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # 循环状态
    turn_count: int = 0
    max_turns: int = 100
    current_model: Optional[str] = None
    
    # 工具统计
    tool_stats: ToolCallStats = Field(default_factory=ToolCallStats)
    
    # 错误信息
    last_error: Optional[str] = None
    error_count: int = 0
    
    # 上下文信息
    token_count: int = 0
    context_window: int = 200000
    
    class Config:
        use_enum_values = True
    
    def start(self, session_id: str, model: str) -> None:
        """开始新会话"""
        self.status = AgentStatus.RUNNING
        self.session_id = session_id
        self.start_time = datetime.now()
        self.end_time = None
        self.turn_count = 0
        self.current_model = model
        self.tool_stats = ToolCallStats()
        self.last_error = None
        self.error_count = 0
    
    def stop(self) -> None:
        """停止会话"""
        self.status = AgentStatus.COMPLETED
        self.end_time = datetime.now()
    
    def error(self, error_message: str) -> None:
        """记录错误"""
        self.status = AgentStatus.ERROR
        self.last_error = error_message
        self.error_count += 1
    
    def increment_turn(self) -> None:
        """增加轮次"""
        self.turn_count += 1
    
    def record_tool_call(self, tool_name: str, success: bool) -> None:
        """记录工具调用"""
        self.tool_stats.total_calls += 1
        if success:
            self.tool_stats.successful_calls += 1
        else:
            self.tool_stats.failed_calls += 1
        
        # 更新工具计数
        if tool_name in self.tool_stats.tool_counts:
            self.tool_stats.tool_counts[tool_name] += 1
        else:
            self.tool_stats.tool_counts[tool_name] = 1
    
    def is_running(self) -> bool:
        """是否正在运行"""
        return self.status == AgentStatus.RUNNING
    
    def has_exceeded_max_turns(self) -> bool:
        """是否超过最大轮次"""
        return self.turn_count >= self.max_turns
    
    def get_duration(self) -> Optional[float]:
        """获取运行时长（秒）"""
        if not self.start_time:
            return None
        
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取状态摘要"""
        return {
            "status": self.status,
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "duration": self.get_duration(),
            "tool_stats": {
                "total": self.tool_stats.total_calls,
                "successful": self.tool_stats.successful_calls,
                "failed": self.tool_stats.failed_calls,
                "top_tools": dict(
                    sorted(
                        self.tool_stats.tool_counts.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5]
                )
            },
            "error_count": self.error_count,
            "last_error": self.last_error,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "status": self.status,
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "turn_count": self.turn_count,
            "max_turns": self.max_turns,
            "current_model": self.current_model,
            "tool_stats": self.tool_stats.dict(),
            "last_error": self.last_error,
            "error_count": self.error_count,
            "token_count": self.token_count,
            "context_window": self.context_window,
        }
