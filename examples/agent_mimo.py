"""
AgentForge - 使用小米 MiMo API 的完整示例
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
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  openai 未安装，使用简化模式")


# ============================================================
# 配置
# ============================================================

# 小米 MiMo API 配置
MIMO_API_KEY = os.getenv("OPENAI_API_KEY", "sk-cox4rik6sq2t6u6caflb3qqle9jizimrhb3ueku56mywljm0")
MIMO_BASE_URL = "https://api.xiaomimimo.com/v1"
MIMO_MODEL = "mimo-v2.5-pro"  # 小米 MiMo 模型


# ============================================================
# 工具定义
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a shell command and return the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "glob",
            "description": "Find files by glob pattern",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., '*.py', '**/*.js')"
                    }
                },
                "required": ["pattern"]
            }
        }
    }
]


# ============================================================
# 工具执行器
# ============================================================

def execute_bash(command: str) -> str:
    """执行 bash 命令"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(f"STDERR: {result.stderr}")
        if result.returncode != 0:
            output.append(f"Exit code: {result.returncode}")
        return "\n".join(output) if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {e}"

def execute_read_file(path: str) -> str:
    """读取文件"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def execute_write_file(path: str, content: str) -> str:
    """写入文件"""
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error: {e}"

def execute_glob(pattern: str) -> str:
    """搜索文件"""
    import glob
    try:
        matches = glob.glob(pattern, recursive=True)
        return "\n".join(matches) if matches else "No files found"
    except Exception as e:
        return f"Error: {e}"

# 工具分发表
TOOL_HANDLERS = {
    "bash": execute_bash,
    "read_file": execute_read_file,
    "write_file": execute_write_file,
    "glob": execute_glob,
}


# ============================================================
# Agent 核心
# ============================================================

@dataclass
class AgentState:
    """Agent 状态"""
    messages: List[Dict] = field(default_factory=list)
    turn_count: int = 0
    tool_calls: int = 0
    max_turns: int = 10

class Agent:
    """Agent 核心类"""
    
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None):
        self.model = model or MIMO_MODEL
        self.api_key = api_key or MIMO_API_KEY
        self.base_url = base_url or MIMO_BASE_URL
        
        if HAS_OPENAI:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        else:
            self.client = None
        
        self.state = AgentState()
    
    def run(self, query: str, verbose: bool = True) -> str:
        """运行 Agent"""
        print(f"\n{'='*60}")
        print(f"🤖 Agent 开始处理: {query}")
        print(f"{'='*60}")
        
        # 初始化
        self.state = AgentState()
        self.state.messages = [
            {"role": "system", "content": "你是一个有用的 AI 助手，可以执行 shell 命令、读写文件、搜索文件。"},
            {"role": "user", "content": query}
        ]
        
        while self.state.turn_count < self.state.max_turns:
            self.state.turn_count += 1
            
            if verbose:
                print(f"\n📍 轮次 {self.state.turn_count}:")
            
            # 调用 LLM
            response = self._call_llm()
            
            if not response:
                return "Error: 无法获取 LLM 响应"
            
            # 检查是否有工具调用
            choice = response.choices[0]
            message = choice.message
            
            # 添加助手消息（保存 tool_calls）
            assistant_msg = {"role": "assistant", "content": message.content or ""}
            if message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            self.state.messages.append(assistant_msg)
            
            # 如果没有工具调用，返回结果
            if not message.tool_calls:
                final_text = message.content or ""
                if verbose:
                    print(f"\n🤖 最终响应:")
                    print(f"   {final_text}")
                return final_text
            
            # 执行工具调用
            if verbose:
                print(f"🔧 工具调用:")
            
            tool_results = []
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                if verbose:
                    print(f"   • {func_name}({func_args})")
                
                # 执行工具
                handler = TOOL_HANDLERS.get(func_name)
                if handler:
                    result = handler(**func_args)
                    self.state.tool_calls += 1
                else:
                    result = f"Error: Unknown tool {func_name}"
                
                if verbose:
                    print(f"     → {result[:100]}...")
                
                # 添加工具结果（正确格式）
                self.state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        return "Error: 超过最大轮次"
    
    def _call_llm(self):
        """调用 LLM"""
        if not self.client:
            print("   ⚠️  OpenAI 客户端未初始化")
            return None
        
        try:
            # 准备消息（移除 tool_calls 字段）
            messages = []
            for msg in self.state.messages:
                clean_msg = {"role": msg["role"], "content": msg.get("content", "")}
                if msg.get("tool_calls"):
                    clean_msg["tool_calls"] = msg["tool_calls"]
                messages.append(clean_msg)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                max_tokens=2000,
                temperature=0.7
            )
            return response
        except Exception as e:
            print(f"   ❌ LLM 调用失败: {e}")
            return None
    
    def get_summary(self) -> Dict:
        """获取摘要"""
        return {
            "turns": self.state.turn_count,
            "tool_calls": self.state.tool_calls,
            "messages": len(self.state.messages)
        }


# ============================================================
# 主程序
# ============================================================

def main():
    """主函数"""
    print("\n" + "🚀" * 30)
    print("\n   AgentForge - 小米 MiMo API 示例")
    print("\n" + "🚀" * 30)
    
    # 创建 Agent
    agent = Agent()
    
    print(f"\n📡 配置信息:")
    print(f"   API: {agent.base_url}")
    print(f"   Model: {agent.model}")
    print(f"   OpenAI 库: {'✅ 已安装' if HAS_OPENAI else '❌ 未安装'}")
    
    if not HAS_OPENAI:
        print("\n⚠️  需要安装 openai 库:")
        print("   pip install openai")
        return
    
    # 测试任务
    tasks = [
        "列出当前目录的文件",
        "当前目录有哪些 Python 文件？",
        "读取 README.md 文件的前 5 行",
    ]
    
    for task in tasks:
        try:
            result = agent.run(task)
            summary = agent.get_summary()
            
            print(f"\n📊 执行统计:")
            print(f"   轮次: {summary['turns']}")
            print(f"   工具调用: {summary['tool_calls']}")
            print(f"   消息数: {summary['messages']}")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
        
        print("\n" + "-" * 60)


if __name__ == "__main__":
    main()
