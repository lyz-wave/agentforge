# AgentForge

> **智能任务自动化框架** - 基于 Claude Code 架构的现代 Agent 框架

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-0.1.0-orange.svg)](https://github.com/lyz-wave/agentforge)

---

## 📖 项目简介

AgentForge 是一个基于 Claude Code 架构设计的智能 Agent 框架，实现了完整的 **Harness Engineering** 模式。它将 Agent 的核心能力（感知、推理、行动）与运行环境（工具、知识、权限）分离，提供了高度可扩展的 Agent 开发框架。

**核心理念：** Agency 来自模型，Harness 给 Agency 一个落脚点。

### 🎯 项目亮点

- ✅ **完整的 Agent Loop 核心循环** - 基于 `while True` 的最小可运行内核
- ✅ **8 个核心模块** - 工具系统、权限系统、Hook 扩展、任务规划、记忆系统、团队协作、MCP 集成
- ✅ **三道闸门安全机制** - 拒绝列表 → 规则匹配 → 用户审批
- ✅ **跨会话记忆系统** - SQLite 持久化 + 上下文压缩
- ✅ **多 Agent 协作** - 消息总线 + 异步邮箱 + 权限冒泡
- ✅ **MCP 协议支持** - 可扩展外部工具
- ✅ **CLI 交互界面** - 像 Claude Code 一样在命令行里启动并交互
- ✅ **4,600+ 行代码** - 完整的框架实现

---

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/lyz-wave/agentforge.git
cd agentforge

# 安装依赖
pip install -r requirements.txt

# 或者以开发模式安装
pip install -e .
```

### 配置

创建 `.env` 文件：

```bash
# 小米 MiMo API
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.xiaomimimo.com/v1

# 或者使用 OpenAI
# OPENAI_API_KEY=your_openai_key
# OPENAI_BASE_URL=https://api.openai.com/v1
```

### 运行

```bash
# 方式 1: 启动 CLI
python run_cli.py

# 方式 2: 使用模块
python -m agentforge

# 方式 3: 安装后使用命令
pip install -e .
agentforge
```

---

## 🏗️ 架构设计

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      AgentForge 架构                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   用户 ──→ Agent Loop ──→ LLM API                          │
│                │                                            │
│                ├──→ 工具系统 (bash, read_file, write_file)  │
│                │                                            │
│                ├──→ 权限系统 (三道闸门)                      │
│                │                                            │
│                ├──→ Hook 系统 (扩展点)                      │
│                │                                            │
│                ├──→ 任务规划 (TodoWrite, TaskManager)       │
│                │                                            │
│                ├──→ 记忆系统 (SQLite, 上下文压缩)           │
│                │                                            │
│                ├──→ 团队协作 (消息总线, 异步邮箱)           │
│                │                                            │
│                └──→ MCP 集成 (外部工具扩展)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 核心模块

| 模块 | 文件 | 功能 | 亮点 |
|------|------|------|------|
| **Agent Loop** | `agent/core/loop.py` | 核心循环 | while True + stop_reason |
| **工具系统** | `agent/tools/` | 工具注册与执行 | 5 个内置工具 + 注册表模式 |
| **权限系统** | `agent/permissions/` | 三道闸门安全机制 | 拒绝列表 + 规则匹配 + 用户审批 |
| **Hook 系统** | `agent/hooks/` | 扩展点机制 | 4 个核心事件 + 可插拔扩展 |
| **任务规划** | `agent/planning/` | 任务分解与追踪 | TodoWrite + 依赖关系图 |
| **记忆系统** | `agent/memory/` | 跨会话记忆 | SQLite 持久化 + 上下文压缩 |
| **团队协作** | `agent/teams/` | 多 Agent 协作 | 消息总线 + 异步邮箱 |
| **MCP 集成** | `agent/mcp/` | 外部工具扩展 | 协议标准 + 多传输层 |

---

## 📚 模块详解

### 1. Agent Loop (核心循环)

```python
def agent_loop(messages):
    while True:
        # 调用 LLM
        response = client.messages.create(
            model=MODEL, system=SYSTEM,
            messages=messages, tools=TOOLS,
        )
        messages.append({"role": "assistant", "content": response.content})
        
        # 检查是否需要工具调用
        if response.stop_reason != "tool_use":
            return
        
        # 执行工具
        results = []
        for block in response.content:
            if block.type == "tool_use":
                output = TOOL_HANDLERS[block.name](**block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                })
        messages.append({"role": "user", "content": results})
```

### 2. 工具系统

```python
# 注册工具
TOOLS = [
    {"name": "bash", "description": "执行 shell 命令", ...},
    {"name": "read_file", "description": "读取文件", ...},
    {"name": "write_file", "description": "写入文件", ...},
    {"name": "glob", "description": "搜索文件", ...},
]

# 工具分发
TOOL_HANDLERS = {
    "bash": run_bash,
    "read_file": run_read,
    "write_file": run_write,
    "glob": run_glob,
}
```

### 3. 权限系统 (三道闸门)

```python
def check_permission(tool_name, tool_input):
    # 闸门 1: 拒绝列表
    if tool_name == "bash":
        command = tool_input.get("command", "")
        for pattern in DENY_LIST:
            if pattern in command:
                return PermissionResult.DENY
    
    # 闸门 2: 规则匹配
    for rule in PERMISSION_RULES:
        if rule.matches(tool_name, tool_input):
            # 闸门 3: 用户审批
            if rule.should_ask():
                return ask_user(tool_name, tool_input, rule.reason)
    
    # 默认允许
    return PermissionResult.ALLOW
```

### 4. Hook 系统

```python
# 注册 Hook
HOOKS = {
    "UserPromptSubmit": [],  # 用户输入后
    "PreToolUse": [],        # 工具执行前
    "PostToolUse": [],       # 工具执行后
    "Stop": [],              # 循环退出前
}

def register_hook(event, callback):
    HOOKS[event].append(callback)

def trigger_hooks(event, *args):
    for callback in HOOKS[event]:
        result = callback(*args)
        if result is not None:
            return result
    return None
```

### 5. 记忆系统

```python
class MemoryStore:
    def add(self, key, value, category, importance):
        # 保存到 SQLite
        self.conn.execute("""
            INSERT INTO memories (key, value, category, importance)
            VALUES (?, ?, ?, ?)
        """, (key, value, category, importance))
    
    def search(self, query, category, min_importance):
        # 搜索记忆
        return self.conn.execute("""
            SELECT * FROM memories 
            WHERE (key LIKE ? OR value LIKE ?)
            AND category = ?
            AND importance >= ?
        """, (f"%{query}%", f"%{query}%", category, min_importance))
```

### 6. 团队协作

```python
class MessageBus:
    def send(self, sender, receiver, content):
        # 发送消息
        message = BusMessage(
            sender=sender,
            receiver=receiver,
            content=content
        )
        self.publish(message)
    
    def broadcast(self, sender, content):
        # 广播消息
        for subscriber in self.subscribers:
            self.send(sender, subscriber, content)
```

---

## 🛠️ CLI 功能

### 启动 CLI

```bash
python run_cli.py
```

### 可用命令

```
/help, /h          显示帮助信息
/exit, /q          退出程序
/clear, /c         清屏
/status, /s        显示状态信息
/history           显示历史记录
/reset             重置会话
/model [name]      显示或切换模型
/api [url]         显示或切换 API 地址
/config            显示当前配置
/tools             列出可用工具
/exec <command>    直接执行 shell 命令
```

### 使用示例

```
❯ 列出当前目录的文件
  🔧 bash({'command': 'ls -la'})
  → total 67...

❯ 读取 README.md 的内容
  🔧 read_file({'path': 'README.md'})
  → # AgentForge...

❯ 创建一个 hello.py 文件
  🔧 write_file({'path': 'hello.py', 'content': '...'})
  → 写入成功: hello.py

❯ 搜索所有 Python 文件
  🔧 glob({'pattern': '*.py'})
  → agent/__init__.py
  → agent/cli.py
  → ...
```

---

## 📊 项目统计

| 指标 | 数量 |
|------|------|
| **总文件数** | 32 个 Python 文件 |
| **总代码行数** | 4,600+ 行 |
| **核心模块** | 8 个 |
| **内置工具** | 5 个 |
| **Hook 事件** | 4 个 |
| **权限闸门** | 3 层 |

---

## 🎯 技术栈

| 类别 | 技术 |
|------|------|
| **语言** | Python 3.8+ |
| **LLM API** | OpenAI API, 小米 MiMo API |
| **数据库** | SQLite |
| **协议** | MCP (Model Context Protocol) |
| **架构** | Agent Loop, Hook System, Message Bus |
| **CLI** | 命令行交互界面 |

---

## 📁 项目结构

```
agentforge/
├── agent/                  # 核心框架
│   ├── core/              # 核心循环和状态管理
│   │   ├── loop.py        # Agent Loop 实现
│   │   ├── message.py     # 消息管理
│   │   └── state.py       # 状态管理
│   │
│   ├── tools/             # 工具系统
│   │   ├── registry.py    # 工具注册表
│   │   ├── bash.py        # Shell 工具
│   │   ├── file.py        # 文件工具
│   │   └── glob.py        # 搜索工具
│   │
│   ├── permissions/       # 权限系统
│   │   ├── pipeline.py    # 权限管线
│   │   └── rules.py       # 权限规则
│   │
│   ├── hooks/             # Hook 系统
│   │   ├── registry.py    # Hook 注册表
│   │   └── handlers.py    # Hook 处理器
│   │
│   ├── planning/          # 任务规划
│   │   ├── todo.py        # TodoWrite
│   │   └── task.py        # 任务管理
│   │
│   ├── memory/            # 记忆系统
│   │   ├── store.py       # 记忆存储
│   │   └── compaction.py  # 上下文压缩
│   │
│   ├── teams/             # 团队协作
│   │   ├── bus.py         # 消息总线
│   │   ├── mailbox.py     # 异步邮箱
│   │   └── coordinator.py # 协调器
│   │
│   └── mcp/               # MCP 集成
│       ├── server.py      # MCP 服务器
│       └── client.py      # MCP 客户端
│
├── examples/              # 示例代码
│   ├── agent_final.py     # 完整 Agent 示例
│   └── demo_simple.py     # 本地演示
│
├── tests/                 # 测试文件
│   └── test_core.py       # 核心测试
│
├── cli.py                 # CLI 入口点
├── setup.py               # 打包配置
├── pyproject.toml         # 现代打包配置
├── requirements.txt       # 依赖列表
└── README.md              # 项目文档
```

---

## 🔧 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black agentforge/
ruff check agentforge/
```

---

## 📝 更新日志

### v0.1.0 (2026-06-24)

- ✅ 实现 Agent Loop 核心循环
- ✅ 实现工具系统（5 个内置工具）
- ✅ 实现权限系统（三道闸门）
- ✅ 实现 Hook 系统（4 个核心事件）
- ✅ 实现任务规划（TodoWrite + TaskManager）
- ✅ 实现记忆系统（SQLite 持久化）
- ✅ 实现团队协作（消息总线 + 异步邮箱）
- ✅ 实现 MCP 集成
- ✅ 实现 CLI 交互界面
- ✅ 完成项目文档

---

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [Claude Code](https://claude.ai/code) - 架构设计灵感
- [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) - 教程参考
- [小米 MiMo](https://api.xiaomimimo.com) - 模型支持
- [OpenAI](https://openai.com) - API 兼容

---

## 📞 联系方式

- **GitHub:** [lyz-wave](https://github.com/lyz-wave)
- **Email:** 754861969@qq.com

---

**Agency 来自模型。Harness 给 Agency 一个落脚点。造好 harness，剩下的交给模型。** 🚀
