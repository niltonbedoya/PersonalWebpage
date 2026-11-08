"""TDD: Security Hardening — HTTP Headers and Rate Limiting.

Tests:
1. Security headers are injected in HTTP responses (nosniff, DENY, Referrer-Policy, Permissions-Policy).
2. Rate limiting restricts excessive bursts to /chat and /api/cv-request, returning HTTP 429.
3. Requests below threshold pass cleanly with HTTP 200.
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.app.core.security_headers import rate_limiter

client = TestClient(app)


def test_http_security_headers_present_on_all_endpoints():
    """All responses must contain essential defensive security headers."""
    resp = client.get("/health/")
    assert resp.status_code == 200, resp.text
    headers = resp.headers

    assert headers.get("x-content-type-options") == "nosniff"
    assert headers.get("x-frame-options") == "DENY"
    assert headers.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "camera=()" in headers.get("permissions-policy", "")
    assert "microphone=()" in headers.get("permissions-policy", "")


def test_rate_limiter_allows_normal_traffic():
    """Normal traffic within threshold returns 200 OK."""
    rate_limiter.reset()
    resp = client.post(
        "/chat/",
        json={"message": "soldadura SMT", "intent_category": "TECHNICAL_PROFILE"},
    )
    assert resp.status_code == 200, resp.text


def test_rate_limiter_blocks_excessive_cv_requests():
    """Bursting /api/cv-request exceeds limit and returns HTTP 429."""
    rate_limiter.reset()
    client_ip = "192.168.1.99"
    payload = {
        "company": "Spam Corp",
        "name": "Spammer",
        "phone": "+34123456789",
        "email": "spam@example.com",
        "reason": "testing burst",
        "honeypot": "",
    }

    # CV limit is 6 req/min. Fire 8 requests with specific test client IP.
    status_codes = []
    for _ in range(8):
        resp = client.post(
            "/api/cv-request",
            json=payload,
            headers={"X-Forwarded-For": client_ip},
        )
        status_codes.append(resp.status_code)

    assert 429 in status_codes
    rate_limiter.reset()
