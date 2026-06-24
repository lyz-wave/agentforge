"""
AgentForge - 使用小米 MiMo Anthropic API 的完整示例
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("尝试安装 anthropic...")
    os.system("pip install anthropic")
    try:
        import anthropic
        HAS_ANTHROPIC = True
    except:
        print("无法安装 anthropic")


# 配置
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "sk-ck...ycr9")
MIMO_BASE_URL = "https://api.xiaomimimo.com/anthropic"
MIMO_MODEL = "claude-3-5-sonnet-20241022"

# 工具定义
TOOLS = [
    {
        "name": "bash",
        "description": "Execute a shell command and return the output",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to execute"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_file",
        "description": "Read the contents of a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to read"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file to write"},
                "content": {"type": "string", "description": "Content to write to the file"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "glob",
        "description": "Find files by glob pattern",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Glob pattern (e.g., '*.py')"}
            },
            "required": ["pattern"]
        }
    }
]

# 工具执行器
def execute_bash(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
        output = []
        if result.stdout: output.append(result.stdout)
        if result.stderr: output.append(f"STDERR: {result.stderr}")
        if result.returncode != 0: output.append(f"Exit code: {result.returncode}")
        return "\n".join(output) if output else "(no output)"
    except Exception as e:
        return f"Error: {e}"

def execute_read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            return content[:5000] + "\n... (truncated)" if len(content) > 5000 else content
    except Exception as e:
        return f"Error: {e}"

def execute_write_file(path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"

def execute_glob(pattern: str) -> str:
    import glob
    try:
        matches = glob.glob(pattern, recursive=True)
        return "\n".join(matches[:20]) if matches else "No files found"
    except Exception as e:
        return f"Error: {e}"

TOOL_HANDLERS = {
    "bash": execute_bash,
    "read_file": execute_read_file,
    "write_file": execute_write_file,
    "glob": execute_glob,
}

# Agent 核心
class Agent:
    def __init__(self):
        self.model = MIMO_MODEL
        self.api_key = MIMO_API_KEY
        self.base_url = MIMO_BASE_URL
        
        if HAS_ANTHROPIC:
            self.client = anthropic.Anthropic(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None
        
        self.messages = []
        self.turn_count = 0
        self.tool_calls = 0
    
    def run(self, query: str, verbose: bool = True) -> str:
        print(f"\n{'='*60}")
        print(f"Agent 开始处理: {query}")
        print(f"{'='*60}")
        
        self.messages = [{"role": "user", "content": query}]
        self.turn_count = 0
        self.tool_calls = 0
        
        system = "你是一个有用的 AI 助手，可以执行 shell 命令、读写文件、搜索文件。请用中文回复。"
        
        while self.turn_count < 10:
            self.turn_count += 1
            
            if verbose:
                print(f"\n轮次 {self.turn_count}:")
            
            response = self._call_llm(system)
            if not response:
                return "Error: LLM 调用失败"
            
            # 处理响应
            has_tool_use = False
            tool_uses = []
            text_content = ""
            
            for block in response.content:
                if block.type == "tool_use":
                    has_tool_use = True
                    tool_uses.append(block)
                elif block.type == "text":
                    text_content += block.text
            
            # 添加助手消息
            self.messages.append({"role": "assistant", "content": response.content})
            
            if not has_tool_use:
                if verbose:
                    print(f"\n最终响应:\n{text_content}")
                return text_content
            
            # 执行工具
            if verbose:
                print(f"工具调用:")
            
            tool_results = []
            for tool_use in tool_uses:
                if verbose:
                    print(f"  - {tool_use.name}({tool_use.input})")
                
                handler = TOOL_HANDLERS.get(tool_use.name)
                if handler:
                    result = handler(**tool_use.input)
                    self.tool_calls += 1
                else:
                    result = f"Error: Unknown tool {tool_use.name}"
                
                if verbose:
                    print(f"    -> {result[:100]}...")
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                })
            
            self.messages.append({"role": "user", "content": tool_results})
        
        return "Error: 超过最大轮次"
    
    def _call_llm(self, system: str):
        if not self.client:
            print("  Anthropic 客户端未初始化")
            return None
        
        try:
            return self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system,
                messages=self.messages,
                tools=TOOLS
            )
        except Exception as e:
            print(f"  LLM 调用失败: {e}")
            return None

# 主程序
def main():
    print("\n" + "=" * 60)
    print("AgentForge - 小米 MiMo Anthropic API 示例")
    print("=" * 60)
    
    agent = Agent()
    
    print(f"\n配置信息:")
    print(f"  API: {agent.base_url}")
    print(f"  Model: {agent.model}")
    print(f"  Anthropic 库: {'已安装' if HAS_ANTHROPIC else '未安装'}")
    
    if not HAS_ANTHROPIC:
        print("\n需要安装 anthropic 库: pip install anthropic")
        return
    
    tasks = [
        "列出当前目录的文件",
        "当前目录有哪些 Python 文件？",
    ]
    
    for task in tasks:
        try:
            result = agent.run(task)
            print(f"\n统计: {agent.turn_count} 轮, {agent.tool_calls} 次工具调用")
        except Exception as e:
            print(f"\n错误: {e}")
        
        print("\n" + "-" * 60)

if __name__ == "__main__":
    main()
