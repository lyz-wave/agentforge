# 🎬 AgentForge CLI 录制指南

## 📋 推荐录制内容

### 场景列表

| # | 场景 | 时长 | 展示内容 |
|---|------|------|----------|
| 1 | 启动 CLI | 3-5秒 | 彩色 Banner、版本号 |
| 2 | 列出文件 | 5-8秒 | bash 工具、文件列表 |
| 3 | 读取文件 | 5-8秒 | read_file 工具、内容预览 |
| 4 | 搜索文件 | 5-8秒 | glob 工具、搜索结果 |
| 5 | 创建文件 | 5-8秒 | write_file 工具、自然语言理解 |
| 6 | 执行文件 | 5-8秒 | bash 工具、脚本执行 |
| 7 | 帮助命令 | 3-5秒 | 命令列表、使用说明 |
| 8 | 退出 | 2-3秒 | 友好退出 |

**总时长：约 35-55 秒**

---

## 🎯 核心亮点

### 必须展示的功能

1. **工具自动调用** - Agent 自动选择合适的工具
2. **自然语言理解** - 用中文描述任务
3. **多轮对话** - 上下文理解
4. **彩色输出** - 美观的终端界面
5. **命令系统** - /help, /exit 等命令

### 展示顺序

```
启动 → 基本工具 → 文件操作 → 搜索 → 创建 → 执行 → 帮助 → 退出
```

---

## 🛠️ 录制方法

### 方法 1: ScreenToGif (Windows 推荐)

1. 下载安装 [ScreenToGif](https://www.screentogif.com/)
2. 打开软件，点击"录制"
3. 调整录制区域覆盖终端窗口
4. 运行真实 CLI：
   ```bash
   cd C:\Users\Admin\Desktop\MyAgent
   python run_cli.py
   ```
5. 按照场景列表输入命令
6. 停止录制，编辑并导出为 GIF
7. 保存到 `docs/assets/demo.gif`

### 方法 2: 使用演示脚本录制

```bash
# 运行完整演示脚本
python scripts/full_demo.py

# 或者运行快速演示
python scripts/demo_gif.py
```

### 方法 3: Python 生成 GIF

```bash
# 安装依赖
pip install Pillow

# 生成 GIF
python scripts/generate_gif.py
```

---

## 📝 录制脚本

### 快速演示（15秒）

```bash
python scripts/demo_gif.py
```

### 完整演示（55秒）

```bash
python scripts/full_demo.py
```

### 自定义演示

```bash
python run_cli.py

# 手动输入以下命令
❯ 列出当前目录的文件
❯ 读取 README.md 的前 3 行
❯ 搜索所有 Python 文件
❯ 创建一个 hello.py 文件
❯ 运行 hello.py
❯ /help
❯ /exit
```

---

## 💡 录制技巧

### 终端设置

| 设置 | 推荐值 |
|------|--------|
| 窗口大小 | 80x24 或更小 |
| 字体大小 | 14-16px |
| 配色方案 | One Dark / Dracula |
| 背景 | 深色（#282c34） |

### 录制技巧

1. **输入速度** - 适中，不要太快
2. **等待时间** - 工具执行后等 0.5-1 秒
3. **清晰度** - 确保文字清晰可见
4. **时长控制** - 30-60 秒最佳
5. **文件大小** - 控制在 5MB 以内

### 后期编辑

1. 删除多余等待时间
2. 调整播放速度（1x 或 1.5x）
3. 裁剪空白区域
4. 添加标题（可选）

---

## 📁 文件位置

```
agentforge/
├── docs/
│   └── assets/
│       └── demo.gif          # 录制的 GIF
│
├── scripts/
│   ├── demo_gif.py           # 快速演示脚本
│   ├── full_demo.py          # 完整演示脚本
│   └── generate_gif.py       # Python 生成 GIF
│
└── README.md                 # 引用 GIF
```

---

## 🔗 在 README 中引用

```markdown
<p align="center">
  <img src="docs/assets/demo.gif" alt="AgentForge Demo" width="600">
</p>

<p align="center">
  <em>AgentForge CLI 交互演示</em>
</p>
```

---

## ✅ 录制检查清单

- [ ] 启动画面清晰
- [ ] 工具调用展示完整
- [ ] 自然语言理解准确
- [ ] 输出结果正确
- [ ] 命令系统正常
- [ ] 时长控制在 60 秒内
- [ ] 文件大小 < 5MB
- [ ] 文字清晰可读

---

**录制完成后，替换 `docs/assets/demo.gif` 并推送到 GitHub！** 🎉
