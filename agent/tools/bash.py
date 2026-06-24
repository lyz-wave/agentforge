"""
Bash 工具 - 执行 Shell 命令
"""

import subprocess
import os
from typing import Dict, Any

from agent.tools.registry import Tool


class BashTool(Tool):
    """
    Bash 工具
    
    执行 Shell 命令并返回输出
    """
    
    @property
    def name(self) -> str:
        return "bash"
    
    @property
    def description(self) -> str:
        return "Execute a shell command and return the output"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to execute",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 60)",
                    "default": 60,
                },
            },
            "required": ["command"],
        }
    
    def execute(
        self, 
        command: str, 
        timeout: int = 60,
        **kwargs
    ) -> str:
        """
        执行 Shell 命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
        
        Returns:
            命令输出
        """
        try:
            # 执行命令
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd(),
            )
            
            # 构建输出
            output_parts = []
            
            if result.stdout:
                output_parts.append(result.stdout)
            
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")
            
            if result.returncode != 0:
                output_parts.append(f"\nExit code: {result.returncode}")
            
            return "\n".join(output_parts) if output_parts else "(no output)"
            
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"
