"""
基础 Agent 示例

演示如何使用 Agent 执行简单任务
"""

import os
from dotenv import load_dotenv

from agent import Agent
from agent.tools import registry

# 加载环境变量
load_dotenv()


def main():
    """主函数"""
    print("=" * 50)
    print("AgentForge - 基础示例")
    print("=" * 50)
    
    # 创建 Agent
    agent = Agent(
        model="claude-sonnet-4-20250514",
        tools=registry.get_schemas(),
        tool_handlers=registry.get_handlers(),
        verbose=True
    )
    
    # 执行任务
    queries = [
        "列出当前目录下的所有文件",
        "读取 README.md 文件的前 10 行",
        "当前目录下有哪些 Python 文件？",
    ]
    
    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print("=" * 50)
        
        try:
            result = agent.run(query)
            print(f"\nResult:\n{result}")
        except Exception as e:
            print(f"\nError: {e}")
        
        # 打印摘要
        agent.print_summary()


if __name__ == "__main__":
    main()
