"""
对话记录数据库模块
主要用于维护历史对话记录
"""
import sqlite3
from typing import Dict, List


class ChatHistoryManager:
    def __init__(self, db_name: str = "history.db"):
        """初始化数据库连接并创建表"""
        self.conn = sqlite3.connect(db_name)
        self._create_table()

    def _create_table(self):
        """创建对话记录表"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS chat_history (
            conversation_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.conn.execute(create_table_sql)
        self.conn.commit()

    def add_record(self, conversation_id: str, content: str) -> int:
        """添加新的对话记录"""
        sql = """
        INSERT INTO chat_history 
        (conversation_id, content)
        VALUES (?, ?)
        """
        cursor = self.conn.cursor()
        cursor.execute(sql, (conversation_id, content))
        self.conn.commit()
        return cursor.lastrowid

    def get_conversation(self, conversation_id: str) -> List[Dict]:
        """获取完整对话记录"""
        sql = """
        SELECT content, timestamp
        FROM chat_history
        WHERE conversation_id = ?
        """
        cursor = self.conn.execute(sql, (conversation_id,))
        results = []
        for row in cursor.fetchall():
            results.append({
                "content": row[0],
                "timestamp": row[1]
            })
        return results
    
    def get_all_conversations(self) -> List[Dict]:
        """获取所有对话记录"""
        sql = """
        SELECT conversation_id, content, timestamp
        FROM chat_history
        """
        cursor = self.conn.execute(sql)
        results = []
        for row in cursor.fetchall():
            results.append({
                "conversation_id": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        return results
    
    def get_conversation_by_least_nums(self, start:int, nums:int) -> int:
        """获取最近的对话记录"""
        sql = """
        SELECT conversation_id, content, timestamp
        FROM chat_history
        ORDER BY timestamp DESC
        LIMIT ?, ?
        """
        cursor = self.conn.execute(sql, (start, nums))
        results = []
        for row in cursor.fetchall():
            results.append({
                "conversation_id": row[0],
                "content": row[1],
                "timestamp": row[2]
            })
        return results

    def update_record(self, record_id: int, new_content: str) -> bool:
        """更新记录内容"""
        sql = "UPDATE chat_history SET content = ? WHERE conversation_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (new_content, record_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_record(self, record_id: str) -> bool:
        """删除记录"""
        sql = "DELETE FROM chat_history WHERE conversation_id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (record_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """关闭数据库连接"""
        self.conn.close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()