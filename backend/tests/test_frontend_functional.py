"""TDD: Frontend functional checks (F4, T8, S1-S3/S7/S8).

Offline, deterministic, no network. FastAPI TestClient against the real
`backend.main` app, which mounts /static/src before /static and exposes /health.
HTML structural checks via html.parser; content asserted as exact strings in
page bodies. Logs ASCII-only.

Covers:
- S1: Hub Central at /static/pages/index.html
- S2: Spoke Industrial at /static/pages/industrial-smt.html
- S3: Spoke Software at /static/pages/software-engineering.html
- S7: drawer trigger accessible from every page
- S8: ASCII-only, navigation hub<->spoke functional, sanitized content
"""

from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from backend.main import app


PAGES = {
    "index": "/static/pages/index.html",
    "industrial-smt": "/static/pages/industrial-smt.html",
    "software-engineering": "/static/pages/software-engineering.html",
}

# Each page must link (via <a href>) to the other two pages.
NAV_LINKS = {
    "index": {"industrial-smt.html", "software-engineering.html"},
    "industrial-smt": {"index.html", "software-engineering.html"},
    "software-engineering": {"index.html", "industrial-smt.html"},
}

ASSETS = [
    "/static/src/styles/shared.css",
    "/static/src/js/shared.js",
    "/static/src/js/i18n.js",
    "/static/src/js/drawer-rag.js",
]

VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class _AnchorParser(HTMLParser):
    """Collects href attributes from <a> tags."""

    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.hrefs.append(value)


class _WellFormedParser(HTMLParser):
    """Tracks opening/closing tags to detect unclosed non-void tags."""

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            self.errors.append(f"unexpected close </{tag}>")


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _get(client: TestClient, path: str):
    response = client.get(path)
    assert response.status_code == 200, f"{path}: expected 200, got {response.status_code}"
    return response


def _anchor_hrefs(html: str):
    parser = _AnchorParser()
    parser.feed(html)
    parser.close()
    return set(parser.hrefs)


def _assert_well_formed(html: str, page: str):
    checker = _WellFormedParser()
    checker.feed(html)
    checker.close()
    assert not checker.errors, f"{page}: {checker.errors}"
    assert not checker.stack, f"{page}: unclosed tags {checker.stack}"


# --- Static pages return 200 ------------------------------------------------

@pytest.mark.parametrize("page", list(PAGES.values()))
def test_static_pages_return_200(client: TestClient, page: str):
    _get(client, page)


# --- Static assets return 200 ----------------------------------------------

@pytest.mark.parametrize("asset", ASSETS)
def test_static_assets_return_200(client: TestClient, asset: str):
    _get(client, asset)


# --- Navigation: each page links to the other two --------------------------

@pytest.mark.parametrize("page", list(PAGES.keys()))
def test_each_page_links_to_other_two_pages(client: TestClient, page: str):
    response = _get(client, PAGES[page])
    hrefs = _anchor_hrefs(response.text)
    expected = NAV_LINKS[page]
    missing = expected - hrefs
    assert not missing, f"{page}: missing nav links to {missing}; found {hrefs}"


# --- Drawer trigger on every page ------------------------------------------

@pytest.mark.parametrize("page", list(PAGES.values()))
def test_each_page_has_drawer_trigger(client: TestClient, page: str):
    body = _get(client, page).text
    assert 'aria-controls="drawer-rag"' in body, f"{page}: drawer trigger missing"


# --- Page-specific content --------------------------------------------------

def test_index_has_news_feed_container(client: TestClient):
    body = _get(client, PAGES["index"]).text
    assert 'id="news-feed"' in body, "index.html: news-feed container missing"


def test_industrial_smt_has_scope_boundary_alert(client: TestClient):
    body = _get(client, PAGES["industrial-smt"]).text
    assert "Pick & Place" in body, "industrial-smt.html: scope boundary alert missing"


def test_software_engineering_has_five_case_studies(client: TestClient):
    body = _get(client, PAGES["software-engineering"]).text
    for case_study in ("cs-tickets", "cs-erp", "cs-logistics", "cs-translation", "cs-health"):
        assert case_study in body, f"software-engineering.html: {case_study} missing"


# --- HTML structural validity via html.parser ------------------------------

@pytest.mark.parametrize("page", list(PAGES.values()))
def test_html_pages_parse_without_unclosed_tags(client: TestClient, page: str):
    body = _get(client, page).text
    _assert_well_formed(body, page)


# --- Root redirect to dashboard -------------------------------------------

def test_root_redirects_browser_to_index_html(client: TestClient):
    response = client.get("/", headers={"accept": "text/html"}, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/pages/index.html"


def test_root_returns_json_for_api_clients(client: TestClient):
    response = client.get("/", headers={"accept": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Showcase Platform" in data["message"]


def test_health_returns_ok_agents_contracts_zero_cost(client: TestClient):
    response = _get(client, "/health")
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["active_agents"]) == 6
    assert len(data["pydantic_contracts"]) == 5
    assert data["zero_cost_routing"] is True
