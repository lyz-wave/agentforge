"""
Hook 处理器 - 预定义的 Hook 实现
"""

from typing import Optional, List, Any


def permission_check_hook(block) -> Optional[str]:
    """
    权限检查 Hook
    
    在工具执行前检查权限
    """
    # 这里可以集成权限系统
    # 返回 None 表示允许，返回字符串表示阻止
    return None


def log_tool_call_hook(block, output=None) -> None:
    """
    工具调用日志 Hook
    
    记录工具调用信息
    """
    if output is not None:
        # PostToolUse
        print(f"[LOG] Tool {block.name} completed")
    else:
        # PreToolUse
        print(f"[LOG] Tool {block.name} called with {block.input}")


def large_output_warning_hook(block, output) -> None:
    """
    大输出警告 Hook
    
    当工具输出过大时发出警告
    """
    if len(str(output)) > 100000:
        print(f"[WARNING] Large output from {block.name}: {len(str(output))} chars")


def session_summary_hook(messages: List[Any]) -> Optional[str]:
    """
    会话摘要 Hook
    
    在会话结束时打印摘要
    """
    tool_count = sum(
        1 for m in messages
        for b in (m.get("content") if isinstance(m.get("content"), list) else [])
        if isinstance(b, dict) and b.get("type") == "tool_result"
    )
    
    print(f"\n{'='*50}")
    print(f"Session Summary")
    print(f"{'='*50}")
    print(f"Messages: {len(messages)}")
    print(f"Tool calls: {tool_count}")
    print(f"{'='*50}\n")
    
    return None


def auto_git_add_hook(block, output) -> None:
    """
    自动 Git Add Hook
    
    在文件写入后自动执行 git add
    """
    if block.name in ("write_file", "edit_file"):
        path = block.input.get("path", "")
        if path:
            import subprocess
            try:
                subprocess.run(
                    ["git", "add", path],
                    capture_output=True,
                    timeout=10
                )
                print(f"[HOOK] git add {path}")
            except Exception:
                pass  # 忽略 git 错误
