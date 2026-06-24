"""
AgentForge - 完整 Agent 示例（修复版）
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 配置
API_KEY=os.getenv... "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.xiaomimimo.com/v1")
MODEL = "mimo-v2.5-pro"

# 工具定义
TOOLS = [
    {"type": "function", "function": {"name": "bash", "description": "Execute shell command", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "Read file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write file", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "glob", "description": "Find files", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}}
]

def run_bash(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
        return result.stdout[:2000] if result.stdout else "(no output)"
    except Exception as e:
        return f"Error: {e}"

def run_read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()[:2000]
    except Exception as e:
        return f"Error: {e}"

def run_write(path: str, content: str) -> str:
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"写入成功: {path}"
    except Exception as e:
        return f"Error: {e}"

def run_glob(pattern: str) -> str:
    import glob
    try:
        matches = glob.glob(pattern, recursive=True)
        return "\n".join(matches[:10]) if matches else "未找到文件"
    except Exception as e:
        return f"Error: {e}"

HANDLERS = {"bash": run_bash, "read_file": run_read, "write_file": run_write, "glob": run_glob}

class Agent:
    def __init__(self):
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.messages = []
        self.turns = 0
        self.tools = 0
    
    def run(self, query: str) -> str:
        print(f"\n{'='*50}")
        print(f"🤖 {query}")
        print(f"{'='*50}")
        
        self.messages = [
            {"role": "system", "content": "你是 AI 助手，可以用工具执行任务。用中文回复。"},
            {"role": "user", "content": query}
        ]
        self.turns = 0
        self.tools = 0
        
        while self.turns < 10:
            self.turns += 1
            print(f"\n轮次 {self.turns}:")
            
            try:
                resp = self.client.chat.completions.create(model=MODEL, messages=self.messages, tools=TOOLS, max_tokens=2000)
            except Exception as e:
                print(f"❌ {e}")
                return f"Error: {e}"
            
            msg = resp.choices[0].message
            assistant = {"role": "assistant", "content": msg.content or ""}
            
            if msg.tool_calls:
                assistant["tool_calls"] = [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in msg.tool_calls]
                self.messages.append(assistant)
                
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    print(f"  🔧 {name}({args})")
                    
                    result = HANDLERS.get(name, lambda **k: "Unknown tool")(**args)
                    self.tools += 1
                    print(f"     → {result[:80]}...")
                    
                    self.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                self.messages.append(assistant)
                print(f"\n🤖 {msg.content}")
                return msg.content or ""
        
        return "超过最大轮次"

def main():
    print("\n🚀 AgentForge - MiMo Agent")
    print(f"API: {BASE_URL}")
    print(f"Model: {MODEL}")
    
    agent = Agent()
    
    # 测试
    agent.run("列出当前目录的文件")
    print(f"\n📊 {agent.turns} 轮, {agent.tools} 次工具调用")
    
    print("\n" + "-" * 50)
    
    agent.run("有哪些 Python 文件？")
    print(f"\n📊 {agent.turns} 轮, {agent.tools} 次工具调用")

if __name__ == "__main__":
    main()
