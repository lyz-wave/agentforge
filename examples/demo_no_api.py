"""
AgentForge - 本地演示示例

不需要 API Key，展示框架功能
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import registry
from agent.core.message import Message, MessageHistory
from agent.core.state import AgentState
from agent.planning.todo import TodoManager, TodoTool
from agent.planning.task import TaskManager, TaskPriority
from agent.memory.store import MemoryStore
from agent.permissions.pipeline import PermissionPipeline
from agent.hooks.registry import HookRegistry


def demo_tools():
    """演示工具系统"""
    print("\n" + "=" * 60)
    print("🔧 工具系统演示")
    print("=" * 60)
    
    # 列出所有工具
    print("\n📋 已注册的工具:")
    for tool_name in registry.list_tools():
        tool = registry.get_tool(tool_name)
        print(f"   • {tool_name}: {tool.description}")
    
    # 执行 bash 命令
    print("\n▶️ 执行 bash 命令: echo 'Hello AgentForge!'")
    result = registry.execute("bash", command="echo 'Hello AgentForge!'")
    print(f"   结果: {result.strip()}")
    
    # 执行 glob 搜索
    print("\n▶️ 搜索 Python 文件: *.py")
    result = registry.execute("glob", pattern="*.py", path=".")
    files = result.strip().split("\n")
    print(f"   找到 {len(files)} 个文件")
    for f in files[:5]:
        print(f"   • {f}")


def demo_todo():
    """演示任务规划"""
    print("\n" + "=" * 60)
    print("📝 任务规划演示")
    print("=" * 60)
    
    # 创建 Todo 管理器
    manager = TodoManager()
    todo_tool = TodoTool(manager)
    
    # 添加任务
    print("\n▶️ 添加任务:")
    result = todo_tool.execute("add", todos=[
        {"content": "实现 Agent Loop 核心", "priority": 3},
        {"content": "添加工具系统", "priority": 2},
        {"content": "实现权限检查", "priority": 2},
        {"content": "编写文档", "priority": 1},
    ])
    print(result)
    
    # 完成任务
    print("\n▶️ 完成任务:")
    result = todo_tool.execute("complete", todos=[
        {"id": "todo_1"},
        {"id": "todo_2"},
    ])
    print(result)
    
    # 查看任务列表
    print("\n▶️ 当前任务列表:")
    result = todo_tool.execute("list")
    print(result)


def demo_memory():
    """演示记忆系统"""
    print("\n" + "=" * 60)
    print("💾 记忆系统演示")
    print("=" * 60)
    
    # 创建记忆存储（使用临时数据库）
    store = MemoryStore(":memory:")
    
    # 保存记忆
    print("\n▶️ 保存记忆:")
    store.add("user_name", "AgentForge 用户", category="user", importance=0.9)
    store.add("project_type", "AI Agent 框架", category="project", importance=0.8)
    store.add("favorite_language", "Python", category="preferences", importance=0.7)
    store.add("last_task", "演示记忆系统", category="task", importance=0.5)
    print("   已保存 4 条记忆")
    
    # 回忆记忆
    print("\n▶️ 回忆记忆:")
    entry = store.get("user_name")
    if entry:
        print(f"   用户名: {entry.value}")
    
    # 搜索记忆
    print("\n▶️ 搜索包含 'Agent' 的记忆:")
    results = store.search(query="Agent")
    for entry in results:
        print(f"   • [{entry.category}] {entry.key}: {entry.value}")
    
    # 统计信息
    print("\n▶️ 记忆统计:")
    stats = store.get_stats()
    print(f"   总记忆数: {stats['total']}")
    print(f"   分类数: {stats['categories']}")


def demo_permissions():
    """演示权限系统"""
    print("\n" + "=" * 60)
    print("🔐 权限系统演示")
    print("=" * 60)
    
    # 创建权限管线
    pipeline = PermissionPipeline()
    
    # 测试拒绝列表
    print("\n▶️ 测试拒绝列表:")
    test_cases = [
        ("bash", {"command": "ls -la"}, "安全命令"),
        ("bash", {"command": "rm -rf /"}, "危险命令"),
        ("bash", {"command": "sudo apt install python"}, "提权命令"),
        ("read_file", {"path": "README.md"}, "读取文件"),
    ]
    
    for tool_name, tool_input, desc in test_cases:
        decision = pipeline.check(tool_name, tool_input)
        status = "✅ 允许" if decision.result.value == "allow" else "❌ 拒绝"
        print(f"   {status} {desc}: {tool_name}({tool_input})")


def demo_hooks():
    """演示 Hook 系统"""
    print("\n" + "=" * 60)
    print("🎣 Hook 系统演示")
    print("=" * 60)
    
    # 创建 Hook 注册表
    registry = HookRegistry()
    
    # 定义 Hook
    def log_hook(*args, **kwargs):
        print(f"   [HOOK] 日志: {args}")
        return None
    
    def block_hook(*args, **kwargs):
        return "被 Hook 阻止"
    
    # 注册 Hook
    registry.register("PreToolUse", log_hook, name="logger", priority=10)
    registry.register("PreToolUse", block_hook, name="blocker", priority=5)
    
    print("\n▶️ 触发 Hook (会被 blocker 阻止):")
    result = registry.trigger("PreToolUse", {"name": "bash", "command": "ls"})
    print(f"   结果: {result}")


def demo_tasks():
    """演示任务管理"""
    print("\n" + "=" * 60)
    print("📋 任务管理演示")
    print("=" * 60)
    
    # 创建任务管理器
    manager = TaskManager()
    
    # 创建任务
    print("\n▶️ 创建任务 (带依赖关系):")
    task1 = manager.create("设计架构", priority=TaskPriority.HIGH)
    task2 = manager.create("实现核心", blocked_by=[task1.id])
    task3 = manager.create("编写测试", blocked_by=[task2.id])
    task4 = manager.create("编写文档", blocked_by=[task1.id])
    
    print(f"   任务 1: {task1.title} (状态: {task1.status})")
    print(f"   任务 2: {task2.title} (状态: {task2.status}, 依赖: {task2.blocked_by})")
    print(f"   任务 3: {task3.title} (状态: {task3.status}, 依赖: {task3.blocked_by})")
    print(f"   任务 4: {task4.title} (状态: {task4.status}, 依赖: {task4.blocked_by})")
    
    # 执行任务
    print("\n▶️ 执行任务流程:")
    
    # 获取下一个任务
    next_task = manager.get_next_task()
    print(f"   下一个任务: {next_task.title}")
    
    # 完成任务 1
    manager.start(task1.id)
    manager.complete(task1.id, "架构设计完成")
    print(f"   完成: {task1.title}")
    
    # 检查任务 2 是否解锁
    next_task = manager.get_next_task()
    print(f"   下一个任务: {next_task.title} (状态: {next_task.status})")
    
    # 显示依赖图
    print("\n▶️ 任务依赖图:")
    print(manager.to_dependency_graph())


def demo_message():
    """演示消息系统"""
    print("\n" + "=" * 60)
    print("💬 消息系统演示")
    print("=" * 60)
    
    # 创建消息历史
    history = MessageHistory()
    
    # 添加消息
    history.add_user("帮我写一个 Python 函数")
    history.add_assistant("好的，我来帮你写一个计算斐波那契数列的函数：")
    history.add_user("谢谢！再加一个参数可以限制最大值")
    
    # 显示消息
    print("\n▶️ 消息历史:")
    for i, msg in enumerate(history):
        role = "👤 用户" if msg.role == "user" else "🤖 助手"
        content = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
        print(f"   {i+1}. {role}: {content}")
    
    # 获取 API 格式
    print("\n▶️ API 格式:")
    api_messages = history.get_messages()
    print(f"   消息数量: {len(api_messages)}")


def main():
    """主演示函数"""
    print("\n" + "🚀" * 30)
    print("\n   AgentForge 框架功能演示")
    print("\n" + "🚀" * 30)
    
    # 运行各个演示
    demo_tools()
    demo_todo()
    demo_memory()
    demo_permissions()
    demo_hooks()
    demo_tasks()
    demo_message()
    
    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)
    
    print("""
    
📚 下一步:
   1. 配置 API Key 运行完整 Agent
   2. 查看 examples/basic_agent.py 了解完整用法
   3. 查看 examples/multi_agent.py 了解多 Agent 协作
   4. 阅读 docs/ 目录的详细文档

🔧 配置 API Key:
   cp .env.example .env
   # 编辑 .env 填入你的 API Key
   
   # 支持的提供商:
   # - Anthropic (Claude)
   # - OpenAI (GPT-4)
   # - DeepSeek
   # - OpenRouter
   # - 本地模型 (Ollama)
""")


if __name__ == "__main__":
    main()
