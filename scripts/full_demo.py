#!/usr/bin/env python
"""
AgentForge CLI 完整演示脚本
用于录制 GIF 展示所有核心功能
"""

import time
import sys

def print_slow(text, delay=0.03):
    """逐字打印，模拟真实输入"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def wait(seconds):
    """等待"""
    time.sleep(seconds)

def demo():
    """完整演示流程"""
    
    print("\n" + "="*60)
    print("🎬 AgentForge CLI 完整演示")
    print("="*60 + "\n")
    
    # ========== 场景 1: 启动 ==========
    print_slow("🚀 启动 AgentForge CLI...", 0.05)
    wait(1)
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║   AgentForge CLI v0.1.0 - 智能任务自动化框架                  ║
║   输入 /help 查看帮助，/exit 退出                            ║
╚══════════════════════════════════════════════════════════════╝
""")
    wait(2)
    
    # ========== 场景 2: 列出文件 ==========
    print_slow("❯ 列出当前目录的文件", 0.05)
    wait(0.5)
    print_slow("  🔧 bash({'command': 'ls -la'})", 0.02)
    wait(0.3)
    print_slow("  → agent/  agentforge/  examples/  docs/", 0.02)
    print_slow("  → README.md  setup.py  requirements.txt", 0.02)
    wait(0.5)
    print_slow("📊 2 轮, 1 次工具调用", 0.03)
    wait(1.5)
    
    # ========== 场景 3: 读取文件 ==========
    print_slow("❯ 读取 README.md 的前 3 行", 0.05)
    wait(0.5)
    print_slow("  🔧 read_file({'path': 'README.md'})", 0.02)
    wait(0.3)
    print_slow("  → # AgentForge", 0.02)
    print_slow("  → > 智能任务自动化框架", 0.02)
    print_slow("  → 基于 Claude Code 架构的现代 Agent 框架", 0.02)
    wait(0.5)
    print_slow("📊 2 轮, 1 次工具调用", 0.03)
    wait(1.5)
    
    # ========== 场景 4: 搜索文件 ==========
    print_slow("❯ 搜索所有 Python 文件", 0.05)
    wait(0.5)
    print_slow("  🔧 glob({'pattern': '**/*.py'})", 0.02)
    wait(0.3)
    print_slow("  → agent/__init__.py", 0.02)
    print_slow("  → agent/core/loop.py", 0.02)
    print_slow("  → agentforge/cli.py", 0.02)
    print_slow("  → examples/agent_final.py", 0.02)
    wait(0.5)
    print_slow("📊 2 轮, 1 次工具调用", 0.03)
    wait(1.5)
    
    # ========== 场景 5: 创建文件 ==========
    print_slow("❯ 创建一个 hello.py 文件，内容是打印 Hello AgentForge", 0.05)
    wait(0.5)
    print_slow("  🔧 write_file({'path': 'hello.py', 'content': 'print(\"Hello AgentForge\")'})", 0.02)
    wait(0.3)
    print_slow("  → 写入成功: hello.py", 0.02)
    wait(0.5)
    print_slow("📊 2 轮, 1 次工具调用", 0.03)
    wait(1.5)
    
    # ========== 场景 6: 执行文件 ==========
    print_slow("❯ 运行 hello.py", 0.05)
    wait(0.5)
    print_slow("  🔧 bash({'command': 'python hello.py'})", 0.02)
    wait(0.3)
    print_slow("  → Hello AgentForge", 0.02)
    wait(0.5)
    print_slow("📊 2 轮, 1 次工具调用", 0.03)
    wait(1.5)
    
    # ========== 场景 7: 帮助命令 ==========
    print_slow("❯ /help", 0.05)
    wait(0.5)
    print_slow("  AgentForge CLI 帮助", 0.03)
    print_slow("  /help, /h          显示帮助信息", 0.02)
    print_slow("  /exit, /q          退出程序", 0.02)
    print_slow("  /clear, /c         清屏", 0.02)
    print_slow("  /status, /s        显示状态信息", 0.02)
    print_slow("  /tools             列出可用工具", 0.02)
    wait(1.5)
    
    # ========== 场景 8: 退出 ==========
    print_slow("❯ /exit", 0.05)
    wait(0.5)
    print_slow("再见！", 0.03)
    wait(1)
    
    print("\n" + "="*60)
    print("✅ 演示完成！")
    print("="*60 + "\n")

if __name__ == "__main__":
    demo()
