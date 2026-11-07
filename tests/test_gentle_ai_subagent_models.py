"""TDD: Gentle-AI subagent model routing (build-time layer).

Validates the per-subagent model configuration for the Gentle-AI ODD
orchestration layer, per `config/gentle-ai/subagent-models.json`.

This is NOT product runtime code — it governs the development subagents
(gentle-orchestrator, gentle-ai-explore, gentle-ai-worker, gentle-ai-verify)
used by the ODD workflow, per `AGENTS.md` "Capa 1 — Build-time".

Every subagent has a zero-cost primary model and a zero-cost fallback.
Model names resolve against the gentle-ai.model-variants plugin cache
already registered in cli.json.
"""

import json
from pathlib import Path

import pytest

CONFIG_PATH = Path("config/gentle-ai/subagent-models.json")

EXPECTED_SUBAGENTS = {
    "gentle-orchestrator",
    "gentle-ai-explore",
    "gentle-ai-worker",
    "gentle-ai-verify",
}

ZERO_COST_PROVIDERS = {
    "groq",
    "google_ai_studio",
    "cloudflare_workers_ai",
    "openrouter",
}


def _load_config():
    assert CONFIG_PATH.is_file(), f"missing {CONFIG_PATH}"
    with CONFIG_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


# --- file exists and has expected schema -----------------------------------


def test_config_file_exists():
    assert CONFIG_PATH.is_file()


def test_config_has_schema_and_subagents():
    cfg = _load_config()
    assert cfg.get("schema") == "gentle-ai.subagent-models/v1"
    assert "subagents" in cfg and isinstance(cfg["subagents"], dict)


def test_all_expected_subagents_present():
    cfg = _load_config()
    subagents = cfg["subagents"]
    assert EXPECTED_SUBAGENTS.issubset(set(subagents.keys())), (
        f"missing subagents: {EXPECTED_SUBAGENTS - set(subagents.keys())}"
    )


def test_no_extra_subagents():
    cfg = _load_config()
    subagents = cfg["subagents"]
    assert set(subagents.keys()) == EXPECTED_SUBAGENTS, (
        f"unexpected subagents: {set(subagents.keys()) - EXPECTED_SUBAGENTS}"
    )


# --- per-subagent validation ----------------------------------------------


@pytest.mark.parametrize("subagent_name", sorted(EXPECTED_SUBAGENTS))
def test_subagent_has_required_fields(subagent_name):
    cfg = _load_config()
    entry = cfg["subagents"][subagent_name]
    for field in ("provider", "primary_model", "fallback_model", "role"):
        assert field in entry, f"{subagent_name} missing field: {field}"


@pytest.mark.parametrize("subagent_name", sorted(EXPECTED_SUBAGENTS))
def test_subagent_provider_is_zero_cost(subagent_name):
    cfg = _load_config()
    provider = cfg["subagents"][subagent_name]["provider"]
    assert provider in ZERO_COST_PROVIDERS, (
        f"{subagent_name} provider {provider!r} is not zero-cost"
    )


@pytest.mark.parametrize("subagent_name", sorted(EXPECTED_SUBAGENTS))
def test_subagent_fallback_differs_from_primary(subagent_name):
    cfg = _load_config()
    entry = cfg["subagents"][subagent_name]
    assert entry["fallback_model"] != entry["primary_model"], (
        f"{subagent_name} fallback must differ from primary"
    )


def test_subagent_models_are_non_empty_strings():
    cfg = _load_config()
    for name, entry in cfg["subagents"].items():
        assert isinstance(entry["primary_model"], str) and entry["primary_model"]
        assert isinstance(entry["fallback_model"], str) and entry["fallback_model"]
        assert isinstance(entry["role"], str) and entry["role"]


# --- fallback strategy -----------------------------------------------------


def test_config_documents_fallback_strategy():
    cfg = _load_config()
    strategy = cfg.get("fallback_strategy", "")
    assert "unavailable" in strategy.lower() or "rate" in strategy.lower()


# --- providers section (optional but recommended) --------------------------


def test_providers_section_matches_used_providers():
    cfg = _load_config()
    subagents = cfg["subagents"]
    used = {entry["provider"] for entry in subagents.values()}
    providers_section = cfg.get("providers", {})
    if providers_section:
        declared = set(providers_section.keys())
        assert used.issubset(declared), (
            f"subagents use providers not declared in providers section: {used - declared}"
        )
        for provider in declared:
            assert provider in ZERO_COST_PROVIDERS, (
                f"declared provider {provider} is not zero-cost"
            )
