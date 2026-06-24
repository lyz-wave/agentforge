"""
文件工具 - 读取、写入、编辑文件
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from agent.tools.registry import Tool


class ReadFileTool(Tool):
    """
    读取文件工具
    
    读取文件内容并返回
    """
    
    @property
    def name(self) -> str:
        return "read_file"
    
    @property
    def description(self) -> str:
        return "Read the contents of a file"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to read",
                },
                "offset": {
                    "type": "integer",
                    "description": "Line number to start reading from (1-indexed)",
                    "default": 1,
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to read",
                    "default": 500,
                },
            },
            "required": ["path"],
        }
    
    def execute(
        self, 
        path: str, 
        offset: int = 1, 
        limit: int = 500,
        **kwargs
    ) -> str:
        """
        读取文件
        
        Args:
            path: 文件路径
            offset: 起始行号（从 1 开始）
            limit: 最大读取行数
        
        Returns:
            文件内容
        """
        try:
            file_path = Path(path)
            
            # 检查文件是否存在
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            # 检查是否是文件
            if not file_path.is_file():
                return f"Error: Not a file: {path}"
            
            # 读取文件
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 应用偏移和限制
            start = max(0, offset - 1)  # 转换为 0-indexed
            end = min(len(lines), start + limit)
            
            # 格式化输出（带行号）
            output_lines = []
            for i in range(start, end):
                line_num = i + 1
                line = lines[i].rstrip("\n")
                output_lines.append(f"{line_num}|{line}")
            
            return "\n".join(output_lines) if output_lines else "(empty file)"
            
        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileTool(Tool):
    """
    写入文件工具
    
    将内容写入文件（覆盖）
    """
    
    @property
    def name(self) -> str:
        return "write_file"
    
    @property
    def description(self) -> str:
        return "Write content to a file (overwrites existing content)"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to write",
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file",
                },
            },
            "required": ["path", "content"],
        }
    
    def execute(self, path: str, content: str, **kwargs) -> str:
        """
        写入文件
        
        Args:
            path: 文件路径
            content: 要写入的内容
        
        Returns:
            操作结果
        """
        try:
            file_path = Path(path)
            
            # 创建父目录（如果不存在）
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 获取文件信息
            size = file_path.stat().st_size
            lines = content.count("\n") + 1
            
            return f"Successfully wrote {size} bytes ({lines} lines) to {path}"
            
        except Exception as e:
            return f"Error writing file: {str(e)}"


class EditFileTool(Tool):
    """
    编辑文件工具
    
    查找并替换文件中的文本
    """
    
    @property
    def name(self) -> str:
        return "edit_file"
    
    @property
    def description(self) -> str:
        return "Replace text in a file (find and replace)"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to the file to edit",
                },
                "old_text": {
                    "type": "string",
                    "description": "Text to find and replace",
                },
                "new_text": {
                    "type": "string",
                    "description": "New text to replace with",
                },
                "replace_all": {
                    "type": "boolean",
                    "description": "Replace all occurrences (default: false)",
                    "default": False,
                },
            },
            "required": ["path", "old_text", "new_text"],
        }
    
    def execute(
        self, 
        path: str, 
        old_text: str, 
        new_text: str, 
        replace_all: bool = False,
        **kwargs
    ) -> str:
        """
        编辑文件
        
        Args:
            path: 文件路径
            old_text: 要查找的文本
            new_text: 替换后的文本
            replace_all: 是否替换所有匹配项
        
        Returns:
            操作结果
        """
        try:
            file_path = Path(path)
            
            # 检查文件是否存在
            if not file_path.exists():
                return f"Error: File not found: {path}"
            
            # 读取文件
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 检查文本是否存在
            if old_text not in content:
                return f"Error: Text not found in {path}"
            
            # 执行替换
            if replace_all:
                new_content = content.replace(old_text, new_text)
                count = content.count(old_text)
            else:
                new_content = content.replace(old_text, new_text, 1)
                count = 1
            
            # 写入文件
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            return f"Successfully replaced {count} occurrence(s) in {path}"
            
        except Exception as e:
            return f"Error editing file: {str(e)}"


class FileExistsTool(Tool):
    """
    检查文件是否存在工具
    """
    
    @property
    def name(self) -> str:
        return "file_exists"
    
    @property
    def description(self) -> str:
        return "Check if a file or directory exists"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check",
                },
            },
            "required": ["path"],
        }
    
    def execute(self, path: str, **kwargs) -> str:
        """检查文件是否存在"""
        try:
            p = Path(path)
            
            if not p.exists():
                return f"{path} does not exist"
            
            info = []
            info.append(f"{path} exists")
            info.append(f"Type: {'directory' if p.is_dir() else 'file'}")
            
            if p.is_file():
                size = p.stat().st_size
                info.append(f"Size: {size} bytes")
            
            return "\n".join(info)
            
        except Exception as e:
            return f"Error checking path: {str(e)}"
