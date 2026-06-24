"""
AgentForge CLI - 命令行入口点

像 Claude Code 一样在命令行里启动并交互
"""

import os
import sys
import json
import subprocess
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 版本号
__version__ = "0.1.0"

# 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"

# 配置
API_KEY=os.getenv("OPENAI_API_KEY", "")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.xiaomimimo.com/v1")
MODEL = "mimo-v2.5-pro"

# 工具定义
TOOLS = [
    {"type": "function", "function": {"name": "bash", "description": "执行 shell 命令", "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}}},
    {"type": "function", "function": {"name": "read_file", "description": "读取文件", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "写入文件", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "glob", "description": "搜索文件", "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}}
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
        return "\n".join(matches[:20]) if matches else "未找到文件"
    except Exception as e:
        return f"Error: {e}"

HANDLERS = {"bash": run_bash, "read_file": run_read, "write_file": run_write, "glob": run_glob}

@dataclass
class AgentState:
    messages: List[Dict] = field(default_factory=list)
    turns: int = 0
    tool_calls: int = 0

class AgentForgeCLI:
    """AgentForge CLI 主类"""
    
    def __init__(self):
        self.client = None
        self.state = AgentState()
        self.history = []
        
        if HAS_OPENAI and API_KEY:
            self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    
    def print_banner(self):
        """打印启动横幅"""
        banner = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗        ║
║  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝        ║
║  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   █████╗          ║
║  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══╝          ║
║  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████╗        ║
║  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝        ║
║                                                              ║
║  {Colors.YELLOW}AgentForge CLI v{__version__}{Colors.CYAN} - 智能任务自动化框架              ║
║  {Colors.DIM}输入 /help 查看帮助，/exit 退出{Colors.CYAN}                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        print(banner)
    
    def print_help(self):
        """打印帮助信息"""
        help_text = f"""
{Colors.CYAN}AgentForge CLI 帮助{Colors.RESET}

{Colors.YELLOW}基本命令:{Colors.RESET}
  /help, /h          显示此帮助信息
  /exit, /q          退出程序
  /clear, /c         清屏
  /status, /s        显示状态信息
  /history           显示历史记录
  /reset             重置会话

{Colors.YELLOW}配置命令:{Colors.RESET}
  /model [name]      显示或切换模型
  /api [url]         显示或切换 API 地址
  /config            显示当前配置

{Colors.YELLOW}工具命令:{Colors.RESET}
  /tools             列出可用工具
  /exec <command>    直接执行 shell 命令

{Colors.YELLOW}使用技巧:{Colors.RESET}
  • 直接输入问题或任务，Agent 会自动处理
  • Agent 可以执行命令、读写文件、搜索文件
  • 使用 Ctrl+C 中断当前任务
  • 使用上下箭头浏览历史命令

{Colors.YELLOW}示例:{Colors.RESET}
  > 列出当前目录的文件
  > 读取 README.md 的内容
  > 创建一个 hello.py 文件
  > 搜索所有 Python 文件
"""
        print(help_text)
    
    def print_status(self):
        """打印状态信息"""
        status = f"""
{Colors.CYAN}状态信息{Colors.RESET}
  模型: {MODEL}
  API: {BASE_URL}
  API Key: {API_KEY[:20]}...{Colors.RESET if API_KEY else f'{Colors.RED}未配置{Colors.RESET}'}
  OpenAI 库: {'已安装' if HAS_OPENAI else '未安装'}
  轮次: {self.state.turns}
  工具调用: {self.state.tool_calls}
  消息数: {len(self.state.messages)}
"""
        print(status)
    
    def print_config(self):
        """打印配置信息"""
        config = f"""
{Colors.CYAN}当前配置{Colors.RESET}
  OPENAI_API_KEY: {API_KEY[:20]}...{Colors.RESET if API_KEY else f'{Colors.RED}未配置{Colors.RESET}'}
  OPENAI_BASE_URL: {BASE_URL}
  MODEL: {MODEL}
"""
        print(config)
    
    def print_tools(self):
        """打印可用工具"""
        print(f"\n{Colors.CYAN}可用工具:{Colors.RESET}")
        for tool in TOOLS:
            func = tool["function"]
            print(f"  {Colors.GREEN}{func['name']}{Colors.RESET}: {func['description']}")
        print()
    
    def run_agent(self, query: str) -> str:
        """运行 Agent"""
        if not self.client:
            return f"{Colors.RED}错误: 未配置 API Key 或 OpenAI 库未安装{Colors.RESET}"
        
        print(f"\n{Colors.DIM}正在处理...{Colors.RESET}")
        
        # 初始化消息
        self.state.messages = [
            {"role": "system", "content": "你是 AgentForge AI 助手，可以执行命令、读写文件、搜索文件。用中文回复。"},
            {"role": "user", "content": query}
        ]
        self.state.turns = 0
        self.state.tool_calls = 0
        
        while self.state.turns < 10:
            self.state.turns += 1
            
            try:
                resp = self.client.chat.completions.create(
                    model=MODEL,
                    messages=self.state.messages,
                    tools=TOOLS,
                    max_tokens=2000
                )
            except Exception as e:
                return f"{Colors.RED}API 错误: {e}{Colors.RESET}"
            
            msg = resp.choices[0].message
            assistant = {"role": "assistant", "content": msg.content or ""}
            
            if msg.tool_calls:
                assistant["tool_calls"] = [{"id": tc.id, "type": "function", "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in msg.tool_calls]
                self.state.messages.append(assistant)
                
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    
                    print(f"  {Colors.YELLOW}🔧 {name}({args}){Colors.RESET}")
                    
                    result = HANDLERS.get(name, lambda **k: "Unknown tool")(**args)
                    self.state.tool_calls += 1
                    
                    print(f"  {Colors.DIM}→ {result[:100]}...{Colors.RESET}")
                    
                    self.state.messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
            else:
                self.state.messages.append(assistant)
                return msg.content or ""
        
        return f"{Colors.RED}超过最大轮次{Colors.RESET}"
    
    def process_command(self, cmd: str) -> bool:
        """处理命令"""
        cmd = cmd.strip().lower()
        
        if cmd in ("/help", "/h"):
            self.print_help()
            return True
        elif cmd in ("/exit", "/q"):
            print(f"\n{Colors.CYAN}再见！{Colors.RESET}\n")
            return False
        elif cmd in ("/clear", "/c"):
            os.system("cls" if os.name == "nt" else "clear")
            self.print_banner()
            return True
        elif cmd in ("/status", "/s"):
            self.print_status()
            return True
        elif cmd == "/history":
            if self.history:
                print(f"\n{Colors.CYAN}历史记录:{Colors.RESET}")
                for i, h in enumerate(self.history[-10:], 1):
                    print(f"  {i}. {h[:50]}...")
            else:
                print(f"\n{Colors.DIM}暂无历史记录{Colors.RESET}")
            return True
        elif cmd == "/reset":
            self.state = AgentState()
            self.history = []
            print(f"\n{Colors.GREEN}会话已重置{Colors.RESET}")
            return True
        elif cmd == "/model":
            print(f"\n当前模型: {MODEL}")
            return True
        elif cmd == "/api":
            print(f"\n当前 API: {BASE_URL}")
            return True
        elif cmd == "/config":
            self.print_config()
            return True
        elif cmd == "/tools":
            self.print_tools()
            return True
        elif cmd.startswith("/exec "):
            command = cmd[6:]
            result = run_bash(command)
            print(f"\n{result}")
            return True
        
        return None  # 不是命令
    
    def run(self):
        """运行 CLI 主循环"""
        self.print_banner()
        
        if not self.client:
            print(f"{Colors.YELLOW}警告: 未配置 API Key，部分功能不可用{Colors.RESET}")
            print(f"请设置环境变量: OPENAI_API_KEY\n")
        
        while True:
            try:
                # 提示符
                prompt = f"{Colors.GREEN}❯{Colors.RESET} "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # 检查是否是命令
                if user_input.startswith("/"):
                    result = self.process_command(user_input)
                    if result is False:
                        break
                    if result is True:
                        continue
                
                # 保存到历史
                self.history.append(user_input)
                
                # 运行 Agent
                response = self.run_agent(user_input)
                
                # 打印响应
                print(f"\n{Colors.CYAN}{response}{Colors.RESET}\n")
                
                # 打印统计
                if self.state.tool_calls > 0:
                    print(f"{Colors.DIM}📊 {self.state.turns} 轮, {self.state.tool_calls} 次工具调用{Colors.RESET}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}使用 /exit 退出{Colors.RESET}")
            except EOFError:
                print(f"\n\n{Colors.CYAN}再见！{Colors.RESET}\n")
                break

def main():
    """CLI 入口点"""
    cli = AgentForgeCLI()
    cli.run()

if __name__ == "__main__":
    main()
