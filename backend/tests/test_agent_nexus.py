"""TDD: Nexus orchestrator FSM — session lifecycle + intent routing map (F2, S7/S8/S9).

Offline, deterministic, no network. Nexus logs ASCII-only (Windows cp1252 console).

Nexus provider is dynamic / intent-based (S9):
    select_model_for_agent("Nexus")  # provider="dynamic", model="intent-based"
    (see backend/app/core/llm_routing.py — Nexus selects its provider at
    runtime per task intent; documented here as required by the spec.)
"""

import asyncio

import pytest

from backend.app.agents import Nexus
from backend.app.core.llm_routing import select_model_for_agent


@pytest.fixture
def nexus() -> Nexus:
    return Nexus()


# --- Session lifecycle ----------------------------------------------------


def test_session_lifecycle_create_enters_active_state(nexus: Nexus):
    result = asyncio.run(nexus.session_lifecycle("create", "sess-1"))

    assert result == {
        "status": "created",
        "session_id": "sess-1",
        "state": "active",
    }
    assert nexus.session_fsm["sess-1"] == "active"


def test_session_lifecycle_update_existing_marks_updated(nexus: Nexus):
    nexus.session_fsm["sess-1"] = "active"

    result = asyncio.run(nexus.session_lifecycle("update", "sess-1"))

    assert result == {"status": "updated", "session_id": "sess-1"}
    assert nexus.session_fsm["sess-1"] == "updated"


def test_session_lifecycle_terminate_removes_session(nexus: Nexus):
    nexus.session_fsm["sess-1"] = "active"

    result = asyncio.run(nexus.session_lifecycle("terminate", "sess-1"))

    assert result == {"status": "terminated", "session_id": "sess-1"}
    assert "sess-1" not in nexus.session_fsm


def test_session_lifecycle_unknown_action_returns_unknown_action(nexus: Nexus):
    result = asyncio.run(nexus.session_lifecycle("despachar", "sess-1"))

    assert result == {"status": "unknown_action", "action": "despachar"}
    assert "sess-1" not in nexus.session_fsm


# --- Intent routing map ---------------------------------------------------


@pytest.mark.parametrize(
    "intent, expected_agent",
    [
        ("TECHNICAL_PROFILE", "Cerebrito"),
        ("SOFTWARE_CASE_STUDY", "Cerebrito"),
        ("HARDWARE_SMT", "Centinela"),
        ("OFF_TOPIC", "Centinela"),
        ("PROMPT_INJECTION", "Centinela"),
    ],
)
def test_route_maps_known_intents_to_correct_agent(
    nexus: Nexus, intent: str, expected_agent: str
):
    result = asyncio.run(nexus.route(intent, {}))

    assert result == expected_agent
    assert nexus.agent_routing[intent] == expected_agent


def test_route_unknown_intent_defaults_to_cerebrito(nexus: Nexus):
    result = asyncio.run(nexus.route("NO_SUCH_INTENT", {}))

    assert result == "Cerebrito"
    assert nexus.agent_routing["NO_SUCH_INTENT"] == "Cerebrito"


# --- Provider documentation (S9) ------------------------------------------


def test_nexus_provider_is_dynamic_intent_based():
    result = select_model_for_agent("Nexus")

    assert result.selected_provider == "dynamic"
    assert result.selected_model == "intent-based"
    assert result.is_fallback is False
