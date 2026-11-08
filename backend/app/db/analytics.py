"""Analytics SQLite Database Module.

Lightweight, zero-cost, persistent storage for visitor tracking and metrics.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_ANALYTICS_DB_PATH = REPO_ROOT / "data" / "analytics.db"


class AnalyticsDB:
    """Manages visit tracking and visitor IP logs in local SQLite."""

    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_ANALYTICS_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS visits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip TEXT NOT NULL,
                    country TEXT DEFAULT 'XX',
                    path TEXT NOT NULL,
                    user_agent TEXT DEFAULT '',
                    status_code INTEGER DEFAULT 200,
                    response_time_ms REAL DEFAULT 0.0
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_visits_timestamp ON visits(timestamp DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_visits_ip ON visits(ip)")

    def record_visit(
        self,
        ip: str,
        country: str,
        path: str,
        user_agent: str,
        status_code: int = 200,
        response_time_ms: float = 0.0,
    ) -> None:
        """Insert a new visit record."""
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO visits (ip, country, path, user_agent, status_code, response_time_ms)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (ip, country or "XX", path, user_agent or "", status_code, response_time_ms),
            )

    def get_recent_visits(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent visits ordered newest to oldest."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT id, timestamp, ip, country, path, user_agent, status_code, response_time_ms
                FROM visits
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """Compute aggregate metrics: total visits, unique IPs, and visits today."""
        with self._get_connection() as conn:
            total_cursor = conn.execute("SELECT COUNT(*) FROM visits")
            total_visits = total_cursor.fetchone()[0]

            unique_cursor = conn.execute("SELECT COUNT(DISTINCT ip) FROM visits")
            unique_ips = unique_cursor.fetchone()[0]

            today_cursor = conn.execute(
                "SELECT COUNT(*) FROM visits WHERE date(timestamp) = date('now')"
            )
            visits_today = today_cursor.fetchone()[0]

            top_paths_cursor = conn.execute(
                """
                SELECT path, COUNT(*) as hits
                FROM visits
                GROUP BY path
                ORDER BY hits DESC
                LIMIT 5
                """
            )
            top_paths = [dict(row) for row in top_paths_cursor.fetchall()]

            return {
                "total_visits": total_visits,
                "unique_ips": unique_ips,
                "visits_today": visits_today,
                "top_paths": top_paths,
            }


analytics_db = AnalyticsDB()
