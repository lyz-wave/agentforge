"""
记忆存储 - 持久化记忆管理
"""

import json
import os
import sqlite3
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path


class MemoryEntry(BaseModel):
    """记忆条目"""
    id: str
    key: str
    value: str
    category: str = "general"
    importance: float = 0.5  # 0-1，越高越重要
    created_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryStore:
    """
    记忆存储
    
    使用 SQLite 持久化存储记忆
    """
    
    def __init__(self, db_path: str = None):
        self._db_path = db_path or ".agentforge/memory.db"
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def _init_db(self) -> None:
        """初始化数据库"""
        # 创建目录
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 连接数据库
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        
        # 创建表
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                category TEXT DEFAULT 'general',
                importance REAL DEFAULT 0.5,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL,
                access_count INTEGER DEFAULT 0,
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # 创建索引
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_key ON memories(key)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_category ON memories(category)
        """)
        
        self._conn.commit()
    
    def add(
        self, 
        key: str, 
        value: str, 
        category: str = "general",
        importance: float = 0.5,
        metadata: Dict[str, Any] = None
    ) -> MemoryEntry:
        """
        添加记忆
        
        Args:
            key: 记忆键
            value: 记忆值
            category: 分类
            importance: 重要性
            metadata: 元数据
        
        Returns:
            新创建的记忆条目
        """
        import uuid
        
        entry = MemoryEntry(
            id=str(uuid.uuid4())[:8],
            key=key,
            value=value,
            category=category,
            importance=importance,
            metadata=metadata or {}
        )
        
        self._conn.execute("""
            INSERT INTO memories (id, key, value, category, importance, created_at, last_accessed, access_count, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.key,
            entry.value,
            entry.category,
            entry.importance,
            entry.created_at.isoformat(),
            entry.last_accessed.isoformat(),
            entry.access_count,
            json.dumps(entry.metadata)
        ))
        
        self._conn.commit()
        return entry
    
    def get(self, key: str) -> Optional[MemoryEntry]:
        """获取记忆"""
        cursor = self._conn.execute(
            "SELECT * FROM memories WHERE key = ?",
            (key,)
        )
        row = cursor.fetchone()
        
        if row:
            # 更新访问信息
            self._conn.execute("""
                UPDATE memories 
                SET last_accessed = ?, access_count = access_count + 1
                WHERE id = ?
            """, (datetime.now().isoformat(), row["id"]))
            self._conn.commit()
            
            return self._row_to_entry(row)
        
        return None
    
    def search(
        self, 
        query: str = None,
        category: str = None,
        min_importance: float = None,
        limit: int = 50
    ) -> List[MemoryEntry]:
        """
        搜索记忆
        
        Args:
            query: 搜索查询（模糊匹配 key 和 value）
            category: 分类过滤
            min_importance: 最小重要性
            limit: 返回数量限制
        
        Returns:
            匹配的记忆列表
        """
        sql = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (key LIKE ? OR value LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if min_importance is not None:
            sql += " AND importance >= ?"
            params.append(min_importance)
        
        sql += " ORDER BY importance DESC, last_accessed DESC LIMIT ?"
        params.append(limit)
        
        cursor = self._conn.execute(sql, params)
        return [self._row_to_entry(row) for row in cursor.fetchall()]
    
    def update(self, key: str, value: str = None, importance: float = None) -> Optional[MemoryEntry]:
        """更新记忆"""
        entry = self.get(key)
        if not entry:
            return None
        
        if value is not None:
            self._conn.execute(
                "UPDATE memories SET value = ? WHERE key = ?",
                (value, key)
            )
        
        if importance is not None:
            self._conn.execute(
                "UPDATE memories SET importance = ? WHERE key = ?",
                (importance, key)
            )
        
        self._conn.commit()
        return self.get(key)
    
    def delete(self, key: str) -> bool:
        """删除记忆"""
        cursor = self._conn.execute(
            "DELETE FROM memories WHERE key = ?",
            (key,)
        )
        self._conn.commit()
        return cursor.rowcount > 0
    
    def list_categories(self) -> List[str]:
        """列出所有分类"""
        cursor = self._conn.execute(
            "SELECT DISTINCT category FROM memories"
        )
        return [row["category"] for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        cursor = self._conn.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT category) as categories,
                AVG(importance) as avg_importance,
                SUM(access_count) as total_accesses
            FROM memories
        """)
        row = cursor.fetchone()
        
        return {
            "total": row["total"],
            "categories": row["categories"],
            "avg_importance": row["avg_importance"],
            "total_accesses": row["total_accesses"],
        }
    
    def consolidate(self, category: str = None) -> int:
        """
        合并记忆
        
        删除低重要性且长期未访问的记忆
        
        Returns:
            删除的记忆数量
        """
        # 删除 30 天未访问且重要性低于 0.3 的记忆
        cursor = self._conn.execute("""
            DELETE FROM memories 
            WHERE importance < 0.3 
            AND last_accessed < datetime('now', '-30 days')
            AND (category = ? OR ? IS NULL)
        """, (category, category))
        
        self._conn.commit()
        return cursor.rowcount
    
    def _row_to_entry(self, row: sqlite3.Row) -> MemoryEntry:
        """将数据库行转换为 MemoryEntry"""
        return MemoryEntry(
            id=row["id"],
            key=row["key"],
            value=row["value"],
            category=row["category"],
            importance=row["importance"],
            created_at=datetime.fromisoformat(row["created_at"]),
            last_accessed=datetime.fromisoformat(row["last_accessed"]),
            access_count=row["access_count"],
            metadata=json.loads(row["metadata"])
        )
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def __del__(self):
        self.close()


class MemoryTool:
    """
    Memory 工具
    
    用于管理记忆的工具
    """
    
    def __init__(self, store: MemoryStore):
        self.store = store
    
    @property
    def name(self) -> str:
        return "memory"
    
    @property
    def description(self) -> str:
        return """Manage persistent memory across sessions.

Operations:
- save: Save a memory entry
- recall: Recall a memory by key
- search: Search memories
- list: List all categories
- stats: Get memory statistics
"""
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["save", "recall", "search", "list", "stats"],
                    "description": "Operation to perform",
                },
                "key": {
                    "type": "string",
                    "description": "Memory key (for save/recall)",
                },
                "value": {
                    "type": "string",
                    "description": "Memory value (for save)",
                },
                "query": {
                    "type": "string",
                    "description": "Search query (for search)",
                },
                "category": {
                    "type": "string",
                    "description": "Memory category",
                },
                "importance": {
                    "type": "number",
                    "description": "Importance (0-1)",
                },
            },
            "required": ["operation"],
        }
    
    def execute(self, operation: str, **kwargs) -> str:
        """执行记忆操作"""
        if operation == "save":
            key = kwargs.get("key")
            value = kwargs.get("value")
            if not key or not value:
                return "Error: key and value are required for save"
            
            entry = self.store.add(
                key=key,
                value=value,
                category=kwargs.get("category", "general"),
                importance=kwargs.get("importance", 0.5)
            )
            return f"Saved memory: {entry.id} ({key})"
        
        elif operation == "recall":
            key = kwargs.get("key")
            if not key:
                return "Error: key is required for recall"
            
            entry = self.store.get(key)
            if entry:
                return f"[{entry.category}] {entry.key}: {entry.value}"
            return f"Memory not found: {key}"
        
        elif operation == "search":
            results = self.store.search(
                query=kwargs.get("query"),
                category=kwargs.get("category"),
                limit=10
            )
            
            if not results:
                return "No memories found"
            
            lines = [f"Found {len(results)} memories:"]
            for entry in results:
                lines.append(f"- [{entry.category}] {entry.key}: {entry.value[:100]}...")
            
            return "\n".join(lines)
        
        elif operation == "list":
            categories = self.store.list_categories()
            return "Categories: " + ", ".join(categories)
        
        elif operation == "stats":
            stats = self.store.get_stats()
            return json.dumps(stats, indent=2)
        
        else:
            return f"Error: Unknown operation: {operation}"
