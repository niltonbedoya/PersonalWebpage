"""TDD: /admin router integration — authentication and analytics dashboard.

Tests:
1. /admin without credentials returns 401 Unauthorized.
2. /admin with invalid credentials returns 401 Unauthorized.
3. /admin with valid credentials returns 200 OK and HTML dashboard.
4. /admin/api/stats returns 200 OK with analytics JSON.
5. /admin/api/logs returns 200 OK with recent log lines.
"""

import base64
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.app.routers.admin import admin_router

app = FastAPI()
app.include_router(admin_router)
client = TestClient(app)

VALID_AUTH = "Basic " + base64.b64encode(b"nilton:NiltonPortfolio2026!").decode("ascii")
INVALID_AUTH = "Basic " + base64.b64encode(b"wrong:badpassword").decode("ascii")


def test_admin_requires_authentication():
    resp = client.get("/admin/")
    assert resp.status_code == 401
    assert "www-authenticate" in resp.headers


def test_admin_rejects_invalid_credentials():
    resp = client.get("/admin/", headers={"Authorization": INVALID_AUTH})
    assert resp.status_code == 401


def test_admin_accepts_valid_credentials_and_renders_dashboard():
    resp = client.get("/admin/", headers={"Authorization": VALID_AUTH})
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Panel de Analíticas" in resp.text
    assert "Visitantes Únicos" in resp.text


def test_admin_api_stats():
    resp = client.get("/admin/api/stats", headers={"Authorization": VALID_AUTH})
    assert resp.status_code == 200
    data = resp.json()
    assert "total_visits" in data
    assert "unique_ips" in data
    assert "visits_today" in data


def test_admin_api_logs():
    resp = client.get("/admin/api/logs", headers={"Authorization": VALID_AUTH})
    assert resp.status_code == 200
    data = resp.json()
    assert "logs" in data
    assert isinstance(data["logs"], list)


def test_main_app_records_cloudflare_visitor_ip():
    """Visits with Cloudflare headers are recorded in analytics DB."""
    from backend.main import app as main_app
    from backend.app.db.analytics import analytics_db

    main_client = TestClient(main_app)
    main_client.get(
        "/static/pages/index.html",
        headers={
            "CF-Connecting-IP": "203.0.113.195",
            "CF-IPCountry": "ES",
            "User-Agent": "Mozilla/5.0 TestBrowser",
        },
    )

    visits = analytics_db.get_recent_visits(limit=5)
    matched = [v for v in visits if v["ip"] == "203.0.113.195"]
    assert len(matched) >= 1
    assert matched[0]["country"] == "ES"
    assert "/static/pages/index.html" in matched[0]["path"]

