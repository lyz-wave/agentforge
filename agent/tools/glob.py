"""
Glob 工具 - 文件搜索
"""

import os
import glob
from pathlib import Path
from typing import Dict, Any, List

from agent.tools.registry import Tool


class GlobTool(Tool):
    """
    Glob 工具
    
    使用通配符模式搜索文件
    """
    
    @property
    def name(self) -> str:
        return "glob"
    
    @property
    def description(self) -> str:
        return "Find files by glob pattern"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern (e.g., '*.py', '**/*.js', 'src/**/*.ts')",
                },
                "path": {
                    "type": "string",
                    "description": "Directory to search in (default: current directory)",
                    "default": ".",
                },
            },
            "required": ["pattern"],
        }
    
    def execute(self, pattern: str, path: str = ".", **kwargs) -> str:
        """
        搜索文件
        
        Args:
            pattern: Glob 模式
            path: 搜索目录
        
        Returns:
            匹配的文件列表
        """
        try:
            search_path = Path(path)
            
            # 检查目录是否存在
            if not search_path.exists():
                return f"Error: Directory not found: {path}"
            
            if not search_path.is_dir():
                return f"Error: Not a directory: {path}"
            
            # 执行搜索
            full_pattern = str(search_path / pattern)
            matches = glob.glob(full_pattern, recursive=True)
            
            # 排序结果
            matches.sort()
            
            # 格式化输出
            if not matches:
                return f"No files found matching pattern: {pattern}"
            
            # 只显示相对路径
            output_lines = []
            for match in matches:
                try:
                    rel_path = os.path.relpath(match, path)
                    output_lines.append(rel_path)
                except ValueError:
                    output_lines.append(match)
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"Error searching files: {str(e)}"


class GrepTool(Tool):
    """
    Grep 工具
    
    在文件中搜索文本
    """
    
    @property
    def name(self) -> str:
        return "grep"
    
    @property
    def description(self) -> str:
        return "Search for text patterns in files"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Text pattern to search for (regex supported)",
                },
                "path": {
                    "type": "string",
                    "description": "File or directory to search in",
                    "default": ".",
                },
                "file_glob": {
                    "type": "string",
                    "description": "Filter files by glob pattern (e.g., '*.py')",
                },
                "ignore_case": {
                    "type": "boolean",
                    "description": "Case insensitive search",
                    "default": False,
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 50,
                },
            },
            "required": ["pattern"],
        }
    
    def execute(
        self, 
        pattern: str, 
        path: str = ".", 
        file_glob: str = None,
        ignore_case: bool = False,
        max_results: int = 50,
        **kwargs
    ) -> str:
        """
        搜索文本
        
        Args:
            pattern: 搜索模式（支持正则）
            path: 搜索路径
            file_glob: 文件过滤模式
            ignore_case: 是否忽略大小写
            max_results: 最大结果数
        
        Returns:
            匹配结果
        """
        import re
        
        try:
            search_path = Path(path)
            
            # 检查路径是否存在
            if not search_path.exists():
                return f"Error: Path not found: {path}"
            
            # 编译正则表达式
            flags = re.IGNORECASE if ignore_case else 0
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return f"Error: Invalid regex pattern: {e}"
            
            # 收集要搜索的文件
            if search_path.is_file():
                files = [search_path]
            else:
                # 使用 glob 过滤文件
                if file_glob:
                    files = list(search_path.rglob(file_glob))
                else:
                    files = [f for f in search_path.rglob("*") if f.is_file()]
            
            # 搜索文件内容
            results = []
            for file_path in files:
                try:
                    # 跳过二进制文件
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                rel_path = os.path.relpath(file_path, path)
                                results.append(f"{rel_path}:{line_num}: {line.rstrip()}")
                                
                                if len(results) >= max_results:
                                    break
                    
                    if len(results) >= max_results:
                        break
                        
                except (UnicodeDecodeError, PermissionError):
                    continue
            
            if not results:
                return f"No matches found for pattern: {pattern}"
            
            output = "\n".join(results)
            if len(results) >= max_results:
                output += f"\n\n(Results truncated at {max_results} matches)"
            
            return output
            
        except Exception as e:
            return f"Error searching: {str(e)}"
