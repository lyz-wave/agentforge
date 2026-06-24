# 录制 GIF 动图指南

## 📹 推荐工具

### Windows 用户

**ScreenToGif** (推荐)
- 下载: https://www.screentogif.com/
- 优点: 简单易用，支持编辑

**使用步骤:**
1. 下载安装 ScreenToGif
2. 打开软件，点击"录制"
3. 调整录制区域覆盖终端窗口
4. 运行 `python scripts/demo_gif.py` 或 `python run_cli.py`
5. 停止录制
6. 编辑（可选）→ 导出为 GIF
7. 保存到 `docs/assets/demo.gif`

### 跨平台

**asciinema + agg**
```bash
# 安装
pip install asciinema agg

# 录制
asciinema rec demo.cast

# 运行演示
python scripts/demo_gif.py

# 停止录制 (Ctrl+D)

# 转换为 GIF
agg demo.cast demo.gif
```

## 📁 文件位置

```
agentforge/
├── docs/
│   └── assets/
│       ├── demo.gif          # 主演示 GIF
│       ├── cli-demo.gif      # CLI 演示
│       └── agent-loop.gif    # Agent Loop 演示
└── scripts/
    └── demo_gif.py           # 演示脚本
```

## 📝 在 README 中引用

### 基本引用

```markdown
![AgentForge Demo](docs/assets/demo.gif)
```

### 带标题

```markdown
<p align="center">
  <img src="docs/assets/demo.gif" alt="AgentForge Demo" width="600">
</p>

<p align="center">AgentForge CLI 交互演示</p>
```

### 多个 GIF

```markdown
## 演示

### CLI 交互

![CLI Demo](docs/assets/cli-demo.gif)

### Agent Loop

![Agent Loop](docs/assets/agent-loop.gif)
```

## 🎬 演示脚本

### 自动演示

```bash
python scripts/demo_gif.py
```

### 手动演示

```bash
# 启动 CLI
python run_cli.py

# 输入以下命令
❯ 列出当前目录的文件
❯ 读取 README.md 的内容
❯ 搜索所有 Python 文件
❯ /help
❯ /exit
```

## 💡 录制技巧

1. **终端窗口大小** - 建议 80x24 或更小，确保 GIF 不会太大
2. **字体大小** - 使用较大字体，确保在 GIF 中清晰可见
3. **配色方案** - 使用深色背景 + 亮色文字（如 One Dark、Dracula）
4. **录制速度** - 适当放慢输入速度，让观众能看清
5. **GIF 时长** - 建议 10-30 秒，不要太长
6. **文件大小** - 控制在 5MB 以内，GitHub README 支持最大 10MB

## 🔧 优化 GIF

### 使用 ScreenToGif 编辑

1. 删除不必要的等待时间
2. 调整播放速度（建议 1x 或 1.5x）
3. 裁剪空白区域
4. 降低帧率（10-15 FPS 足够）

### 压缩 GIF

```bash
# 使用 gifsicle 压缩
gifsicle -O3 demo.gif -o demo-optimized.gif

# 降低颜色数
gifsicle -O3 --colors 64 demo.gif -o demo-small.gif
```

---

**录制完成后，将 GIF 放到 `docs/assets/` 目录，然后在 README 中引用即可！** 🎉
