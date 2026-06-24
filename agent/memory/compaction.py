"""
上下文压缩 - 管理上下文窗口
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CompactionResult(BaseModel):
    """压缩结果"""
    original_tokens: int
    compacted_tokens: int
    messages_removed: int
    summary: Optional[str] = None


class ContextCompactor:
    """
    上下文压缩器
    
    管理上下文窗口，防止超出 token 限制
    """
    
    def __init__(
        self, 
        max_tokens: int = 200000,
        compact_threshold: float = 0.8,
        target_ratio: float = 0.5
    ):
        self.max_tokens = max_tokens
        self.compact_threshold = compact_threshold
        self.target_ratio = target_ratio
    
    def estimate_tokens(self, messages: List[Dict[str, Any]]) -> int:
        """
        估算消息的 token 数量
        
        简单估算：每个字符约 1 个 token
        """
        total_chars = 0
        
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        total_chars += len(str(block))
                    else:
                        total_chars += len(str(block))
        
        # 粗略估算：4 字符 ≈ 1 token
        return total_chars // 4
    
    def should_compact(self, messages: List[Dict[str, Any]]) -> bool:
        """检查是否需要压缩"""
        estimated_tokens = self.estimate_tokens(messages)
        return estimated_tokens > (self.max_tokens * self.compact_threshold)
    
    def compact(
        self, 
        messages: List[Dict[str, Any]],
        strategy: str = "smart"
    ) -> tuple[List[Dict[str, Any]], CompactionResult]:
        """
        压缩上下文
        
        Args:
            messages: 消息列表
            strategy: 压缩策略 (simple, smart, summary)
        
        Returns:
            压缩后的消息列表和压缩结果
        """
        original_tokens = self.estimate_tokens(messages)
        
        if strategy == "simple":
            compacted, removed = self._simple_compact(messages)
        elif strategy == "smart":
            compacted, removed = self._smart_compact(messages)
        elif strategy == "summary":
            compacted, removed = self._summary_compact(messages)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        compacted_tokens = self.estimate_tokens(compacted)
        
        result = CompactionResult(
            original_tokens=original_tokens,
            compacted_tokens=compacted_tokens,
            messages_removed=removed,
            summary=f"Reduced from {original_tokens} to {compacted_tokens} tokens"
        )
        
        return compacted, result
    
    def _simple_compact(
        self, 
        messages: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        简单压缩 - 保留最近的消息
        
        删除较早的消息，只保留最近的消息
        """
        target_tokens = int(self.max_tokens * self.target_ratio)
        estimated_tokens = self.estimate_tokens(messages)
        
        if estimated_tokens <= target_tokens:
            return messages, 0
        
        # 计算需要保留的消息比例
        ratio = target_tokens / estimated_tokens
        keep_count = max(1, int(len(messages) * ratio))
        
        # 保留第一条（用户输入）和最后的消息
        if len(messages) > 1:
            compacted = [messages[0]] + messages[-(keep_count-1):]
        else:
            compacted = messages
        
        return compacted, len(messages) - len(compacted)
    
    def _smart_compact(
        self, 
        messages: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        智能压缩 - 保留重要消息
        
        保留：第一条、最后几条、包含工具调用的消息
        """
        if len(messages) <= 3:
            return messages, 0
        
        target_tokens = int(self.max_tokens * self.target_ratio)
        
        # 标记重要消息
        important_indices = set()
        important_indices.add(0)  # 第一条
        
        # 保留最后 3 条
        for i in range(max(0, len(messages) - 3), len(messages)):
            important_indices.add(i)
        
        # 保留包含工具调用的消息
        for i, msg in enumerate(messages):
            content = msg.get("content", "")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") in ("tool_use", "tool_result"):
                        important_indices.add(i)
                        break
        
        # 构建压缩后的消息
        compacted = []
        removed = 0
        
        for i, msg in enumerate(messages):
            if i in important_indices:
                compacted.append(msg)
            else:
                removed += 1
        
        # 如果还是太多，使用简单压缩
        if self.estimate_tokens(compacted) > target_tokens:
            return self._simple_compact(compacted)
        
        return compacted, removed
    
    def _summary_compact(
        self, 
        messages: List[Dict[str, Any]]
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        摘要压缩 - 用摘要替换中间消息
        
        将中间的消息替换为摘要
        """
        if len(messages) <= 5:
            return messages, 0
        
        # 保留前 2 条和后 3 条
        head = messages[:2]
        tail = messages[-3:]
        middle = messages[2:-3]
        
        # 生成摘要
        summary_parts = []
        for msg in middle:
            content = msg.get("content", "")
            if isinstance(content, str):
                # 提取前 100 个字符作为摘要
                summary_parts.append(content[:100] + "..." if len(content) > 100 else content)
        
        summary = "[Previous context: " + " | ".join(summary_parts[:5]) + "]"
        
        # 构建压缩后的消息
        compacted = head + [{"role": "user", "content": summary}] + tail
        
        return compacted, len(middle)
    
    def snip_large_output(
        self, 
        content: str, 
        max_chars: int = 10000
    ) -> str:
        """
        截断大输出
        
        Args:
            content: 输出内容
            max_chars: 最大字符数
        
        Returns:
            截断后的内容
        """
        if len(content) <= max_chars:
            return content
        
        half = max_chars // 2
        return content[:half] + f"\n\n... [truncated {len(content) - max_chars} chars] ...\n\n" + content[-half:]
