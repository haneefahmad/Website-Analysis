import aiosqlite
import json
import os
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(__file__), "audits.db")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id TEXT PRIMARY KEY,
                target_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                overall_score INTEGER NOT NULL,
                data_json TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT,
                company_name TEXT,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                status TEXT DEFAULT 'new',
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (audit_id) REFERENCES audits (id)
            )
        """)
        await db.commit()

async def save_audit(audit_id: str, target_url: str, overall_score: int, full_data: Dict[str, Any]):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO audits (id, target_url, overall_score, data_json) VALUES (?, ?, ?, ?)",
            (audit_id, target_url, overall_score, json.dumps(full_data, default=str))
        )
        await db.commit()

async def get_audit(audit_id: str) -> Optional[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT data_json FROM audits WHERE id = ?", (audit_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return json.loads(row[0])
    return None

async def list_recent_audits(limit: int = 20) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, target_url, created_at, overall_score FROM audits ORDER BY created_at DESC LIMIT ?", 
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]
