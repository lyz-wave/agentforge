"""
AgentForge - 完整 Agent 示例
"""

import os
import json
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 配置
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url=os.getenv('OPENAI_BASE_URL', 'https://api.xiaomimimo.com/v1')
)
MODEL = 'mimo-v2.5-pro'

# 工具定义
TOOLS = [
    {'type': 'function', 'function': {'name': 'bash', 'description': '执行 shell 命令', 'parameters': {'type': 'object', 'properties': {'command': {'type': 'string'}}, 'required': ['command']}}},
    {'type': 'function', 'function': {'name': 'read_file', 'description': '读取文件', 'parameters': {'type': 'object', 'properties': {'path': {'type': 'string'}}, 'required': ['path']}}},
    {'type': 'function', 'function': {'name': 'glob', 'description': '搜索文件', 'parameters': {'type': 'object', 'properties': {'pattern': {'type': 'string'}}, 'required': ['pattern']}}}
]

def run_bash(command):
    try:
        r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return r.stdout[:2000] if r.stdout else '(no output)'
    except Exception as e:
        return f'Error: {e}'

def run_read(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()[:2000]
    except Exception as e:
        return f'Error: {e}'

def run_glob(pattern):
    import glob
    try:
        matches = glob.glob(pattern, recursive=True)
        return '\n'.join(matches[:20]) if matches else '未找到文件'
    except Exception as e:
        return f'Error: {e}'

HANDLERS = {'bash': run_bash, 'read_file': run_read, 'glob': run_glob}

class Agent:
    def __init__(self):
        self.messages = []
        self.turns = 0
        self.tool_count = 0
    
    def run(self, query, verbose=True):
        print(f'\n{"="*60}')
        print(f'🤖 Agent: {query}')
        print(f'{"="*60}')
        
        self.messages = [
            {'role': 'system', 'content': '你是 AI 助手，可以执行命令、读写文件。用中文回复。'},
            {'role': 'user', 'content': query}
        ]
        self.turns = 0
        self.tool_count = 0
        
        while self.turns < 10:
            self.turns += 1
            if verbose:
                print(f'\n📍 轮次 {self.turns}:')
            
            resp = client.chat.completions.create(model=MODEL, messages=self.messages, tools=TOOLS, max_tokens=2000)
            msg = resp.choices[0].message
            
            assistant = {'role': 'assistant', 'content': msg.content or ''}
            
            if msg.tool_calls:
                assistant['tool_calls'] = [{'id': tc.id, 'type': 'function', 'function': {'name': tc.function.name, 'arguments': tc.function.arguments}} for tc in msg.tool_calls]
                self.messages.append(assistant)
                
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    
                    if verbose:
                        print(f'  🔧 {name}({args})')
                    
                    result = HANDLERS.get(name, lambda **k: 'Unknown')(**args)
                    self.tool_count += 1
                    
                    if verbose:
                        print(f'     → {result[:100]}...')
                    
                    self.messages.append({'role': 'tool', 'tool_call_id': tc.id, 'content': result})
            else:
                self.messages.append(assistant)
                if verbose:
                    print(f'\n🤖 回复:\n{msg.content}')
                return msg.content or ''
        
        return '超过最大轮次'

def main():
    print('\n🚀 AgentForge - MiMo Agent')
    print(f'API: {client.base_url}')
    print(f'Model: {MODEL}')
    
    agent = Agent()
    
    # 测试任务
    tasks = [
        '列出当前目录的文件',
        '有哪些 Python 文件？',
        '读取 README.md 的前 3 行',
    ]
    
    for task in tasks:
        result = agent.run(task)
        print(f'\n📊 统计: {agent.turns} 轮, {agent.tool_count} 次工具调用')
        print('-' * 60)

if __name__ == '__main__':
    main()
