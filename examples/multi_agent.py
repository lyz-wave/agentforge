"""
多 Agent 协作示例

演示如何使用团队协作功能
"""

import asyncio
from agent.teams import TeamCoordinator


async def worker_agent(name: str, coordinator: TeamCoordinator):
    """工作 Agent"""
    print(f"[{name}] Started")
    
    mailbox = coordinator.get_mailbox(name)
    
    while True:
        message = await mailbox.receive(timeout=5)
        
        if message:
            print(f"[{name}] Received task: {message.subject}")
            
            # 模拟任务执行
            await asyncio.sleep(1)
            
            # 更新状态
            coordinator.update_status(name, "idle")
            
            print(f"[{name}] Task completed")
        else:
            # 没有消息，继续等待
            await asyncio.sleep(0.1)


async def main():
    """主函数"""
    print("=" * 50)
    print("AgentForge - 多 Agent 协作示例")
    print("=" * 50)
    
    # 创建团队协调器
    coordinator = TeamCoordinator("demo_team")
    
    # 添加团队成员
    coordinator.add_member("worker_1", "Worker 1", capabilities=["code", "analysis"])
    coordinator.add_member("worker_2", "Worker 2", capabilities=["design", "writing"])
    coordinator.add_member("worker_3", "Worker 3", capabilities=["testing", "review"])
    
    print("\nTeam created:")
    for member in coordinator.list_members():
        print(f"  - {member.name} ({member.role}): {member.capabilities}")
    
    # 启动工作 Agent
    tasks = [
        asyncio.create_task(worker_agent("worker_1", coordinator)),
        asyncio.create_task(worker_agent("worker_2", coordinator)),
        asyncio.create_task(worker_agent("worker_3", coordinator)),
    ]
    
    # 分配任务
    print("\nAssigning tasks...")
    
    coordinator.assign_task(
        {"title": "Write code", "description": "Implement feature X", "priority": 1},
        capability_required="code"
    )
    
    coordinator.assign_task(
        {"title": "Write docs", "description": "Create documentation", "priority": 0},
        capability_required="writing"
    )
    
    coordinator.assign_task(
        {"title": "Test code", "description": "Run test suite", "priority": 2},
        capability_required="testing"
    )
    
    # 等待任务完成
    await asyncio.sleep(3)
    
    # 打印统计
    stats = coordinator.get_team_stats()
    print("\nTeam Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 取消任务
    for task in tasks:
        task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
