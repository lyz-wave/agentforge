"""
AgentForge - 简化演示（无需外部依赖）

展示框架核心功能
"""

import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


# ============================================================
# 1. 工具系统演示
# ============================================================

print("\n" + "=" * 60)
print("🔧 1. 工具系统演示")
print("=" * 60)

@dataclass
class Tool:
    """工具定义"""
    name: str
    description: str
    handler: Any
    
    def execute(self, **kwargs) -> str:
        return self.handler(**kwargs)

# 创建工具注册表
tool_registry: Dict[str, Tool] = {}

def register_tool(name: str, description: str, handler):
    """注册工具"""
    tool_registry[name] = Tool(name, description, handler)
    print(f"   ✅ 注册工具: {name}")

def run_bash(command: str, **kwargs) -> str:
    """执行 bash 命令"""
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
    return result.stdout.strip() if result.stdout else "(no output)"

def run_echo(text: str, **kwargs) -> str:
    """回显文本"""
    return text

def run_calculate(expression: str, **kwargs) -> str:
    """计算表达式"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

# 注册工具
register_tool("bash", "执行 Shell 命令", run_bash)
register_tool("echo", "回显文本", run_echo)
register_tool("calculate", "计算数学表达式", run_calculate)

# 执行工具
print("\n▶️ 执行工具演示:")
print(f"   bash('echo Hello'): {tool_registry['bash'].execute(command='echo Hello')}")
print(f"   echo('World'): {tool_registry['echo'].execute(text='World')}")
print(f"   calculate('2+3*4'): {tool_registry['calculate'].execute(expression='2+3*4')}")


# ============================================================
# 2. 任务规划演示
# ============================================================

print("\n" + "=" * 60)
print("📝 2. 任务规划演示")
print("=" * 60)

class TodoStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@dataclass
class TodoItem:
    id: str
    content: str
    status: TodoStatus = TodoStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)

class TodoManager:
    def __init__(self):
        self._todos: Dict[str, TodoItem] = {}
        self._counter = 0
    
    def add(self, content: str) -> TodoItem:
        self._counter += 1
        todo = TodoItem(id=f"todo_{self._counter}", content=content)
        self._todos[todo.id] = todo
        return todo
    
    def complete(self, todo_id: str) -> Optional[TodoItem]:
        todo = self._todos.get(todo_id)
        if todo:
            todo.status = TodoStatus.COMPLETED
        return todo
    
    def list_all(self) -> List[TodoItem]:
        return list(self._todos.values())

# 创建 Todo 管理器
todo_manager = TodoManager()

# 添加任务
print("\n▶️ 添加任务:")
tasks = [
    "设计 Agent 架构",
    "实现核心循环",
    "添加工具系统",
    "实现权限检查",
    "编写文档"
]

for task in tasks:
    todo = todo_manager.add(task)
    print(f"   + {todo.id}: {todo.content}")

# 完成任务
print("\n▶️ 完成任务:")
todo_manager.complete("todo_1")
todo_manager.complete("todo_2")
print("   ✓ todo_1: 设计 Agent 架构")
print("   ✓ todo_2: 实现核心循环")

# 显示状态
print("\n▶️ 当前状态:")
for todo in todo_manager.list_all():
    status = "✅" if todo.status == TodoStatus.COMPLETED else "⏳"
    print(f"   {status} {todo.id}: {todo.content}")


# ============================================================
# 3. 记忆系统演示
# ============================================================

print("\n" + "=" * 60)
print("💾 3. 记忆系统演示")
print("=" * 60)

class MemoryStore:
    def __init__(self):
        self._memories: Dict[str, Dict] = {}
    
    def add(self, key: str, value: str, category: str = "general", importance: float = 0.5):
        self._memories[key] = {
            "key": key,
            "value": value,
            "category": category,
            "importance": importance,
            "created_at": datetime.now().isoformat(),
            "access_count": 0
        }
    
    def get(self, key: str) -> Optional[Dict]:
        entry = self._memories.get(key)
        if entry:
            entry["access_count"] += 1
        return entry
    
    def search(self, query: str = None, category: str = None) -> List[Dict]:
        results = []
        for entry in self._memories.values():
            if category and entry["category"] != category:
                continue
            if query and query.lower() not in entry["value"].lower():
                continue
            results.append(entry)
        return results
    
    def stats(self) -> Dict:
        return {
            "total": len(self._memories),
            "categories": len(set(e["category"] for e in self._memories.values()))
        }

# 创建记忆存储
memory_store = MemoryStore()

# 保存记忆
print("\n▶️ 保存记忆:")
memories = [
    ("user_name", "AgentForge 用户", "user", 0.9),
    ("project_type", "AI Agent 框架", "project", 0.8),
    ("favorite_lang", "Python", "preferences", 0.7),
    ("last_task", "演示记忆系统", "task", 0.5),
]

for key, value, category, importance in memories:
    memory_store.add(key, value, category, importance)
    print(f"   + [{category}] {key}: {value}")

# 回忆记忆
print("\n▶️ 回忆记忆:")
entry = memory_store.get("user_name")
print(f"   user_name = {entry['value']}")

# 搜索记忆
print("\n▶️ 搜索 'Agent':")
results = memory_store.search(query="Agent")
for entry in results:
    print(f"   • [{entry['category']}] {entry['key']}: {entry['value']}")

# 统计
stats = memory_store.stats()
print(f"\n▶️ 统计: {stats['total']} 条记忆, {stats['categories']} 个分类")


# ============================================================
# 4. 权限系统演示
# ============================================================

print("\n" + "=" * 60)
print("🔐 4. 权限系统演示")
print("=" * 60)

class PermissionResult(Enum):
    ALLOW = "allow"
    DENY = "deny"
    ASK = "ask"

class PermissionPipeline:
    def __init__(self):
        self._deny_patterns = [
            "rm -rf /",
            "sudo",
            "shutdown",
            "reboot",
            "mkfs",
            "dd if=",
            "> /dev/sda",
        ]
    
    def check(self, tool_name: str, tool_input: Dict) -> tuple:
        # 闸门 1: 拒绝列表
        if tool_name == "bash":
            command = tool_input.get("command", "")
            for pattern in self._deny_patterns:
                if pattern in command:
                    return (PermissionResult.DENY, f"拒绝: 命令包含 '{pattern}'")
        
        # 默认允许
        return (PermissionResult.ALLOW, "允许执行")

# 创建权限管线
permission_pipeline = PermissionPipeline()

# 测试权限
print("\n▶️ 权限检查测试:")
test_cases = [
    ("bash", {"command": "ls -la"}, "安全命令"),
    ("bash", {"command": "rm -rf /"}, "删除根目录"),
    ("bash", {"command": "sudo apt install python"}, "提权命令"),
    ("bash", {"command": "echo hello"}, "普通命令"),
    ("read_file", {"path": "README.md"}, "读取文件"),
]

for tool_name, tool_input, desc in test_cases:
    result, reason = permission_pipeline.check(tool_name, tool_input)
    status = "✅" if result == PermissionResult.ALLOW else "❌"
    print(f"   {status} {desc}: {reason}")


# ============================================================
# 5. Hook 系统演示
# ============================================================

print("\n" + "=" * 60)
print("🎣 5. Hook 系统演示")
print("=" * 60)

class HookRegistry:
    def __init__(self):
        self._hooks: Dict[str, List] = {
            "PreToolUse": [],
            "PostToolUse": [],
            "Stop": [],
        }
    
    def register(self, event: str, callback, name: str = None):
        self._hooks[event].append({
            "name": name or callback.__name__,
            "callback": callback
        })
    
    def trigger(self, event: str, *args) -> Optional[str]:
        for hook in self._hooks.get(event, []):
            result = hook["callback"](*args)
            if result is not None:
                return result
        return None

# 创建 Hook 注册表
hook_registry = HookRegistry()

# 定义 Hook
def log_hook(*args):
    print(f"   [HOOK] 日志: 工具调用")
    return None

def block_hook(*args):
    return "被 Hook 阻止"

# 注册 Hook
hook_registry.register("PreToolUse", log_hook, name="logger")
hook_registry.register("PreToolUse", block_hook, name="blocker")

print("\n▶️ 触发 Hook:")
result = hook_registry.trigger("PreToolUse", {"name": "bash"})
print(f"   结果: {result}")


# ============================================================
# 6. 消息系统演示
# ============================================================

print("\n" + "=" * 60)
print("💬 6. 消息系统演示")
print("=" * 60)

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

class MessageHistory:
    def __init__(self):
        self.messages: List[Message] = []
    
    def add(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
    
    def get_api_format(self) -> List[Dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

# 创建消息历史
history = MessageHistory()

# 添加消息
history.add("user", "帮我写一个 Python 函数")
history.add("assistant", "好的，我来帮你写一个计算斐波那契数列的函数：")
history.add("user", "谢谢！再加一个参数可以限制最大值")

print("\n▶️ 消息历史:")
for i, msg in enumerate(history.messages):
    role = "👤 用户" if msg.role == "user" else "🤖 助手"
    content = msg.content[:40] + "..." if len(msg.content) > 40 else msg.content
    print(f"   {i+1}. {role}: {content}")

print(f"\n▶️ API 格式: {len(history.get_api_format())} 条消息")


# ============================================================
# 7. Agent Loop 演示（模拟）
# ============================================================

print("\n" + "=" * 60)
print("🔄 7. Agent Loop 演示（模拟）")
print("=" * 60)

def simulate_agent_loop(query: str, max_turns: int = 5):
    """模拟 Agent Loop（不调用真实 LLM）"""
    print(f"\n▶️ 用户输入: {query}")
    print("-" * 40)
    
    messages = [{"role": "user", "content": query}]
    turn = 0
    
    while turn < max_turns:
        turn += 1
        print(f"\n   📍 轮次 {turn}:")
        
        # 模拟 LLM 响应
        if turn == 1:
            # 第一轮：调用工具
            print("   🤖 LLM: 我来帮你执行命令")
            print("   🔧 调用工具: bash(command='echo Hello AgentForge')")
            
            # 执行工具
            result = tool_registry["bash"].execute(command="echo Hello AgentForge")
            print(f"   📤 工具结果: {result}")
            
            messages.append({"role": "assistant", "content": "调用工具"})
            messages.append({"role": "user", "content": f"工具结果: {result}"})
        else:
            # 第二轮：返回结果
            print("   🤖 LLM: 命令执行成功！输出是: Hello AgentForge")
            break
    
    print(f"\n   ✅ 完成! 共 {turn} 轮")

# 运行模拟
simulate_agent_loop("执行 echo 命令输出 Hello AgentForge")


# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 60)
print("✅ 演示完成！")
print("=" * 60)

print("""
📊 框架统计:
   • 工具系统: {} 个工具
   • 任务规划: {} 个任务
   • 记忆系统: {} 条记忆
   • 权限系统: 3 道闸门
   • Hook 系统: 3 个事件
   • 消息系统: {} 条消息

📚 下一步:
   1. 配置 API Key 运行真实 Agent
   2. 查看 examples/basic_agent.py
   3. 阅读 docs/ 目录的详细文档

🔧 配置 API Key:
   cp .env.example .env
   # 编辑 .env 填入你的 API Key
   
   # 支持: Anthropic, OpenAI, DeepSeek, OpenRouter, 本地模型
""".format(
    len(tool_registry),
    len(todo_manager.list_all()),
    len(memory_store._memories),
    len(history.messages)
))
