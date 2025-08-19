"""Database service layer for parts.

Provides simple functions to list, get, create, update and delete parts.
"""
import os
from typing import List, Optional, Dict, Any


def get_conn():
    # Use PyMySQL to connect to MySQL configured via env vars.
    import pymysql
    host = os.getenv('DB_HOST', os.getenv('DATABASE_HOST', 'db'))
    user = os.getenv('DB_USER', os.getenv('DATABASE_USER', 'app'))
    password = os.getenv('DB_PASSWORD', os.getenv('DATABASE_PASSWORD', 'appsecret'))
    db = os.getenv('DB_NAME', os.getenv('DATABASE_NAME', 'appdb'))
    port = int(os.getenv('DB_PORT', os.getenv('DATABASE_PORT', 3306)))
    try:
        return pymysql.connect(host=host, user=user, password=password, database=db, port=port, cursorclass=pymysql.cursors.Cursor)
    except Exception:
        return None


def init_db(seed: bool = True) -> bool:
    conn = get_conn()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                price INTEGER,
                location TEXT,
                image_url TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                validation_token VARCHAR(128),
                is_validated TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Ensure migrations for older DBs: add columns if they are missing
        try:
            cur.execute("ALTER TABLE parts ADD COLUMN IF NOT EXISTS validation_token VARCHAR(128)")
            cur.execute("ALTER TABLE parts ADD COLUMN IF NOT EXISTS is_validated TINYINT(1) DEFAULT 0")
        except Exception:
            # Some MySQL versions may not support IF NOT EXISTS; fallback to safe checks
            try:
                cur.execute("SELECT validation_token FROM parts LIMIT 1")
            except Exception:
                try:
                    cur.execute("ALTER TABLE parts ADD COLUMN validation_token VARCHAR(128)")
                except Exception:
                    pass
            try:
                cur.execute("SELECT is_validated FROM parts LIMIT 1")
            except Exception:
                try:
                    cur.execute("ALTER TABLE parts ADD COLUMN is_validated TINYINT(1) DEFAULT 0")
                except Exception:
                    pass
        conn.commit()

        # Seeding via SQL migrations is handled by the seed job (app/migrations/db_data.sql).      
        return True
    except Exception:
        return False
    finally:
        conn.close()


def list_parts(limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_conn()
    out: List[Dict[str, Any]] = []
    if not conn:
        return out
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, description, price, location, image_url, contact_email, contact_phone, created_at FROM parts WHERE is_validated=1 ORDER BY created_at DESC LIMIT %s",
            (limit,),
        )
        for r in cur.fetchall():
            out.append(
                {
                    "id": r[0],
                    "title": r[1],
                    "description": r[2],
                    "price": r[3],
                    "location": r[4],
                    "image_url": r[5],
                    "contact_email": r[6],
                    "contact_phone": r[7],
                    "created_at": r[8].isoformat() if r[8] else None,
                }
            )
        return out
    finally:
        conn.close()


def get_part(part_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, title, description, price, location, image_url, contact_email, contact_phone, created_at, is_validated, validation_token FROM parts WHERE id = %s",
            (part_id,),
        )
        r = cur.fetchone()
        if not r:
            return None
        return {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "price": r[3],
            "location": r[4],
            "image_url": r[5],
            "contact_email": r[6],
            "contact_phone": r[7],
            "created_at": r[8].isoformat() if r[8] else None,
            "is_validated": bool(r[9]),
            "validation_token": r[10],
        }
    finally:
        conn.close()


def create_part(data: Dict[str, Any]) -> Optional[int]:
    conn = get_conn()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO parts (title, description, price, location, image_url, contact_email, contact_phone, validation_token, is_validated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (
                data.get("title"),
                data.get("description"),
                data.get("price"),
                data.get("location"),
                data.get("image_url"),
                data.get("contact_email"),
                data.get("contact_phone"),
                data.get("validation_token"),
                1 if data.get("is_validated") else 0,
            ),
        )
        new_id = cur.lastrowid
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_part(part_id: int, data: Dict[str, Any]) -> bool:
    # Build a dynamic update statement for provided fields
    allowed = ["title", "description", "price", "location", "image_url", "contact_email", "contact_phone", "is_validated", "validation_token"]
    set_parts = []
    params = []
    for k in allowed:
        if k in data:
            set_parts.append(f"{k} = %s")
            params.append(data[k])
    if not set_parts:
        return False
    params.append(part_id)
    sql = f"UPDATE parts SET {', '.join(set_parts)} WHERE id = %s"
    conn = get_conn()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(sql, tuple(params))
        if cur.rowcount == 0:
            return False
        conn.commit()
        return True
    finally:
        conn.close()


def delete_part(part_id: int) -> bool:
    conn = get_conn()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM parts WHERE id = %s", (part_id,))
        if cur.rowcount == 0:
            return False
        conn.commit()
        return True
    finally:
        conn.close()


def validate_token(token: str) -> bool:
    """Mark a part as validated by token. Returns True if a row was updated."""
    if not token:
        return False
    conn = get_conn()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("UPDATE parts SET is_validated=1, validation_token=NULL WHERE validation_token = %s", (token,))
        if cur.rowcount == 0:
            return False
        conn.commit()
        return True
    finally:
        conn.close()
