"""TDD: Health router integration — active agents, Pydantic contracts, WS status (F3, T5/S4).

Offline, deterministic, no network. FastAPI TestClient against the real
health_router. Logs ASCII-only.

Covers S4: /health — estado global + agentes activos, contratos Pydantic listados.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.routers.health import health_router


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(health_router)
    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(_build_app())


EXPECTED_AGENTS = [
    "Nexus",
    "Radarito",
    "Cerebrito",
    "Centinela",
    "Mensajerito",
    "Auditor",
]

EXPECTED_CONTRACTS = [
    "NewsItemPayload",
    "RAGResponsePayload",
    "GuardrailVerdict",
    "LeadAlertPayload",
    "AuditVerdict",
]


def test_health_status_http_200(client: TestClient):
    response = client.get("/health/status")
    assert response.status_code == 200


def test_health_status_shape(client: TestClient):
    response = client.get("/health/status")
    data = response.json()
    assert data["status"] == "healthy"
    assert data["active_agents"] == EXPECTED_AGENTS
    assert data["contracts"] == EXPECTED_CONTRACTS
    assert data["zero_cost_routing"] is True
    ws = data["websocket_connections"]
    assert "total_connections" in ws
    assert isinstance(ws["total_connections"], int)
    assert "agents" in ws
    assert isinstance(ws["agents"], dict)


def test_health_status_lists_all_six_agents(client: TestClient):
    data = client.get("/health/status").json()
    assert set(data["active_agents"]) == set(EXPECTED_AGENTS)
    assert len(data["active_agents"]) == 6


def test_health_status_lists_all_five_contracts(client: TestClient):
    data = client.get("/health/status").json()
    assert set(data["contracts"]) == set(EXPECTED_CONTRACTS)
    assert len(data["contracts"]) == 5


def test_health_status_zero_cost_routing_true(client: TestClient):
    data = client.get("/health/status").json()
    assert data["zero_cost_routing"] is True


def test_health_status_websocket_connections_shape(client: TestClient):
    data = client.get("/health/status").json()
    ws = data["websocket_connections"]
    assert ws["total_connections"] == 0
    assert set(ws["agents"].keys()) == set(EXPECTED_AGENTS)
    assert all(count == 0 for count in ws["agents"].values())
