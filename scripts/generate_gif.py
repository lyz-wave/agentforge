"""
生成 AgentForge CLI 演示 GIF
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # 配置
    WIDTH = 800
    HEIGHT = 500
    BG_COLOR = (40, 44, 52)  # 深色背景
    TEXT_COLOR = (171, 178, 191)  # 浅色文字
    GREEN = (152, 195, 121)  # 绿色
    YELLOW = (229, 192, 123)  # 黄色
    CYAN = (86, 182, 194)  # 青色
    
    # 创建帧
    frames = []
    
    def create_frame(lines, cursor_line=-1):
        """创建一帧"""
        img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)
        
        # 绘制标题栏
        draw.rectangle([0, 0, WIDTH, 30], fill=(30, 33, 39))
        draw.text((10, 8), "AgentForge CLI", fill=CYAN)
        draw.text((WIDTH-100, 8), "bash", fill=TEXT_COLOR)
        
        # 绘制内容
        y = 40
        for i, line in enumerate(lines):
            color = TEXT_COLOR
            if line.startswith("❯"):
                color = GREEN
            elif line.startswith("  🔧"):
                color = YELLOW
            elif line.startswith("  →"):
                color = CYAN
            elif "AgentForge" in line:
                color = CYAN
            
            draw.text((20, y), line, fill=color)
            y += 20
        
        # 绘制光标
        if cursor_line >= 0:
            y = 40 + cursor_line * 20
            draw.rectangle([15, y, 18, y+15], fill=GREEN)
        
        return img
    
    # 场景 1: 启动画面
    lines1 = [
        "╔══════════════════════════════════════════╗",
        "║   AgentForge CLI v0.1.0                  ║",
        "║   智能任务自动化框架                       ║",
        "╚══════════════════════════════════════════╝",
        "",
        "❯ "
    ]
    frames.append(create_frame(lines1, 4))
    frames.append(create_frame(lines1, 4))
    
    # 场景 2: 输入命令
    lines2 = lines1.copy()
    lines2[-1] = "❯ 列出当前目录的文件"
    frames.append(create_frame(lines2))
    frames.append(create_frame(lines2))
    
    # 场景 3: 工具调用
    lines3 = lines2.copy()
    lines3.extend([
        "",
        "  🔧 bash({'command': 'ls -la'})",
        "  → agent/  examples/  README.md"
    ])
    frames.append(create_frame(lines3))
    frames.append(create_frame(lines3))
    
    # 场景 4: 结果
    lines4 = lines3.copy()
    lines4.extend([
        "",
        "📊 2 轮, 1 次工具调用"
    ])
    frames.append(create_frame(lines4))
    frames.append(create_frame(lines4))
    
    # 场景 5: 新命令
    lines5 = [
        "❯ 读取 README.md 的内容",
        "",
        "  🔧 read_file({'path': 'README.md'})",
        "  → # AgentForge",
        "  → > 智能任务自动化框架",
        "",
        "📊 2 轮, 1 次工具调用"
    ]
    frames.append(create_frame(lines5))
    frames.append(create_frame(lines5))
    
    # 场景 6: 帮助命令
    lines6 = [
        "❯ /help",
        "",
        "  AgentForge CLI 帮助",
        "  /help, /h          显示帮助信息",
        "  /exit, /q          退出程序",
        "  /clear, /c         清屏",
        "  /status, /s        显示状态信息"
    ]
    frames.append(create_frame(lines6))
    frames.append(create_frame(lines6))
    
    # 场景 7: 退出
    lines7 = [
        "❯ /exit",
        "",
        "再见！"
    ]
    frames.append(create_frame(lines7))
    frames.append(create_frame(lines7))
    frames.append(create_frame(lines7))
    
    # 保存为 GIF
    output_path = "docs/assets/demo.gif"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=1000,  # 每帧 1 秒
        loop=0
    )
    
    print(f"✅ GIF 已生成: {output_path}")
    print(f"   帧数: {len(frames)}")
    print(f"   大小: {os.path.getsize(output_path) / 1024:.1f} KB")
    
except ImportError:
    print("需要安装 Pillow: pip install Pillow")
except Exception as e:
    print(f"错误: {e}")
