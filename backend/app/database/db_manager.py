"""Database operations and management."""

from typing import Optional, Dict, Any
from psycopg2.extras import Json
from .connection import db_pool


def setup_database(conn) -> None:
    """Set up database tables and indexes."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS search_log (
                id SERIAL PRIMARY KEY,
                user_input TEXT NOT NULL UNIQUE,
                verdict TEXT,
                source_link TEXT,
                explanation TEXT,
                evidence_json JSONB,
                searched_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS search_log_user_input_norm_idx
            ON search_log ((lower(btrim(user_input))));
        """)
        conn.commit()


def get_conn():
    """Get a database connection from the pool."""
    return db_pool.get_connection()


def put_conn(conn):
    """Return a database connection to the pool."""
    db_pool.put_connection(conn)


def check_cache(conn, claim_norm: str) -> Optional[Dict[str, Any]]:
    """Check if a claim result exists in cache."""
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT verdict, source_link, explanation, evidence_json
                FROM search_log
                WHERE lower(btrim(user_input)) = lower(btrim(%s));
            """, (claim_norm,))
            row = cur.fetchone()
            if row:
                return {
                    "verdict": row[0],
                    "link": row[1],
                    "explanation": row[2],
                    "evidence": row[3],
                }
    except Exception as e:
        print(f"[Cache] check error: {e}")
    return None


def upsert_result(conn, claim_norm: str, verdict: str, source_link: str, 
                  explanation: Optional[str] = None, evidence_json: Optional[Dict] = None) -> None:
    """Insert or update a fact-check result in the database."""
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO search_log (user_input, verdict, source_link, explanation, evidence_json)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_input) DO UPDATE SET
                    verdict = EXCLUDED.verdict,
                    source_link = EXCLUDED.source_link,
                    explanation = EXCLUDED.explanation,
                    evidence_json = EXCLUDED.evidence_json,
                    searched_at = CURRENT_TIMESTAMP;
            """, (
                claim_norm,
                verdict,
                source_link,
                explanation,
                Json(evidence_json) if evidence_json is not None else None,
            ))
            conn.commit()
    except Exception as e:
        print(f"[DB] upsert error: {e}")
        conn.rollback()