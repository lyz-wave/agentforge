# AgentForge CLI

> 智能任务自动化框架 - 基于 Claude Code 架构的现代 Agent 框架

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
OPENAI_API_KEY=***
OPENAI_BASE_URL=https://api.xiaomimimo.com/v1

# 或者使用 OpenAI
# OPENAI_API_KEY=sk-xxx
# OPENAI_BASE_URL=https://api.openai.com/v1
```

### 运行

```bash
# 方式 1: 直接运行
python run_cli.py

# 方式 2: 使用模块
python -m agentforge

# 方式 3: 安装后使用命令
pip install -e .
agentforge
```

## 📖 使用指南

### 基本命令

```
/help, /h          显示帮助信息
/exit, /q          退出程序
/clear, /c         清屏
/status, /s        显示状态信息
/history           显示历史记录
/reset             重置会话
```

### 配置命令

```
/model [name]      显示或切换模型
/api [url]         显示或切换 API 地址
/config            显示当前配置
```

### 工具命令

```
/tools             列出可用工具
/exec <command>    直接执行 shell 命令
```

### 使用示例

```
❯ 列出当前目录的文件
❯ 读取 README.md 的内容
❯ 创建一个 hello.py 文件
❯ 搜索所有 Python 文件
❯ 帮我写一个斐波那契函数
```

## 🛠️ 功能特性

- ✅ **交互式命令行** - 像 Claude Code 一样自然对话
- ✅ **工具调用** - 自动执行命令、读写文件、搜索文件
- ✅ **多轮对话** - 支持上下文理解
- ✅ **彩色输出** - 美观的终端界面
- ✅ **命令历史** - 支持历史记录浏览
- ✅ **配置管理** - 灵活的配置选项

## 📦 项目结构

```
agentforge/
├── __init__.py      # 包初始化
├── __main__.py      # 模块入口
├── cli.py           # CLI 主程序
└── ...

setup.py             # 打包配置
pyproject.toml       # 现代打包配置
requirements.txt     # 依赖列表
run_cli.py           # 启动脚本
```

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

## 📝 许可证

MIT License

## 🙏 致谢

- [Claude Code](https://claude.ai/code) - 架构灵感
- [小米 MiMo](https://api.xiaomimimo.com) - 模型支持
- [OpenAI](https://openai.com) - API 兼容

---

**AgentForge - 让 AI 成为你的命令行助手！** 🚀
