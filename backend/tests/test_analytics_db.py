"""TDD: Analytics Database Module.

Tests:
1. DB initialization creates table.
2. record_visit stores visit with IP, path, status.
3. get_recent_visits returns ordered visits.
4. get_analytics_stats computes total visits and unique IPs.
"""

import os
import shutil
import tempfile
from pathlib import Path
from backend.app.db.analytics import AnalyticsDB


def test_analytics_db_lifecycle():
    temp_dir = tempfile.mkdtemp(prefix="analytics_test_")
    try:
        db_file = Path(temp_dir) / "test_analytics.db"
        analytics = AnalyticsDB(db_path=str(db_file))

        # Record 3 visits (2 distinct IPs) with city and region
        analytics.record_visit(
            ip="192.168.1.50",
            country="ES",
            city="Madrid",
            region="Comunidad de Madrid",
            path="/static/pages/index.html",
            user_agent="Mozilla/5.0 (Windows NT 10.0)",
            status_code=200,
            response_time_ms=12.5,
        )
        analytics.record_visit(
            ip="192.168.1.50",
            country="ES",
            city="Madrid",
            region="Comunidad de Madrid",
            path="/chat/",
            user_agent="Mozilla/5.0 (Windows NT 10.0)",
            status_code=200,
            response_time_ms=45.2,
        )
        analytics.record_visit(
            ip="85.20.10.1",
            country="FR",
            city="Paris",
            region="Île-de-France",
            path="/static/pages/industrial-smt.html",
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0)",
            status_code=200,
            response_time_ms=8.0,
        )

        visits = analytics.get_recent_visits(limit=10)
        assert len(visits) == 3
        assert visits[0]["ip"] == "85.20.10.1"  # most recent first
        assert visits[0]["country"] == "FR"
        assert visits[0]["city"] == "Paris"
        assert visits[0]["region"] == "Île-de-France"

        stats = analytics.get_stats()
        assert stats["total_visits"] == 3
        assert stats["unique_ips"] == 2
        assert stats["visits_today"] == 3
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

