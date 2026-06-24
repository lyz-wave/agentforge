#!/usr/bin/env python
"""
AgentForge 演示脚本 - 用于录制 GIF
"""

import time
import sys

def print_slow(text, delay=0.03):
    """逐字打印"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def demo():
    """演示流程"""
    print("\n" + "="*60)
    print("🚀 AgentForge CLI 演示")
    print("="*60 + "\n")
    
    time.sleep(1)
    
    # 演示 1: 列出文件
    print_slow("❯ 列出当前目录的文件", 0.05)
    time.sleep(0.5)
    print_slow("  🔧 bash({'command': 'ls -la'})", 0.02)
    time.sleep(0.3)
    print_slow("  → agent/  examples/  README.md  setup.py", 0.02)
    time.sleep(0.5)
    print_slow("📊 2 轮, 1 次工具调用\n", 0.03)
    
    time.sleep(1)
    
    # 演示 2: 读取文件
    print_slow("❯ 读取 README.md 的前 3 行", 0.05)
    time.sleep(0.5)
    print_slow("  🔧 read_file({'path': 'README.md'})", 0.02)
    time.sleep(0.3)
    print_slow("  → # AgentForge", 0.02)
    print_slow("  → > 智能任务自动化框架", 0.02)
    time.sleep(0.5)
    print_slow("📊 2 轮, 1 次工具调用\n", 0.03)
    
    time.sleep(1)
    
    # 演示 3: 搜索文件
    print_slow("❯ 搜索所有 Python 文件", 0.05)
    time.sleep(0.5)
    print_slow("  🔧 glob({'pattern': '*.py'})", 0.02)
    time.sleep(0.3)
    print_slow("  → agent/__init__.py", 0.02)
    print_slow("  → agent/cli.py", 0.02)
    print_slow("  → examples/demo.py", 0.02)
    time.sleep(0.5)
    print_slow("📊 2 轮, 1 次工具调用\n", 0.03)
    
    time.sleep(1)
    
    # 演示 4: 帮助命令
    print_slow("❯ /help", 0.05)
    time.sleep(0.5)
    print_slow("  AgentForge CLI 帮助", 0.03)
    print_slow("  /help, /h          显示帮助信息", 0.02)
    print_slow("  /exit, /q          退出程序", 0.02)
    print_slow("  /clear, /c         清屏", 0.02)
    print_slow("  /status, /s        显示状态信息", 0.02)
    time.sleep(1)
    
    print_slow("\n❯ /exit", 0.05)
    time.sleep(0.3)
    print_slow("再见！\n", 0.03)

if __name__ == "__main__":
    demo()
