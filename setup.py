"""
AgentForge - 智能任务自动化框架

基于 Claude Code 架构的现代 Agent 框架
"""

from setuptools import setup, find_packages
import os

# 读取 README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()

# 读取依赖
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="agentforge",
    version="0.1.0",
    author="lyz-wave",
    author_email="754861969@qq.com",
    description="智能任务自动化框架 - 基于 Claude Code 架构的现代 Agent 框架",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/lyz-wave/agentforge",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "agentforge=agentforge.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
