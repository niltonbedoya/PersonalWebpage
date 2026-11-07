"""TDD: LLM model routing per sub-agent with zero-cost fallback (F2).

Defines which provider+model each runtime agent uses, plus a zero-cost
fallback per agent. Integrates with the gentle-ai.model-variants plugin
already registered in cli.json (cache of provider model variants).

Rules from the architecture spec (docs/especificaci_n_y_resumen_de_arquitectura.md §4.2):
- Centinela & Mensajerito: Groq Cloud llama-3.1-8b-instant
- Cerebrito & Auditor: Google AI Studio gemini-1.5-flash / 2.0-flash
- Radarito: Cloudflare Workers AI / OpenRouter Free (qwen-2.5-7b or deepseek-chat)
- Nexus: dynamic provider selection by task intent
"""

import pytest

from backend.app.core.llm_routing import (
    ProviderType,
    AgentModelConfig,
    LLMRoutingTable,
    ModelSelectionResult,
    get_routing_table,
    select_model_for_agent,
    is_zero_cost_provider,
)


# --- ProviderType ---------------------------------------------------------


def test_provider_type_only_zero_cost_values():
    assert set(ProviderType.__args__) == {
        "groq",
        "google_ai_studio",
        "cloudflare_workers_ai",
        "openrouter",
    }


def test_is_zero_cost_provider_accepts_all_defined():
    for provider in ProviderType.__args__:
        assert is_zero_cost_provider(provider) is True


def test_is_zero_cost_provider_rejects_paid():
    assert is_zero_cost_provider("anthropic") is False  # type: ignore[arg-type]
    assert is_zero_cost_provider("openai") is False  # type: ignore[arg-type]


# --- AgentModelConfig -----------------------------------------------------


def test_agent_model_config_requires_fallback_different_from_primary():
    with pytest.raises(ValueError, match="fallback must differ from primary"):
        AgentModelConfig(
            agent_name="Centinela",
            provider="groq",
            primary_model="llama-3.1-8b-instant",
            fallback_model="llama-3.1-8b-instant",
        )


def test_agent_model_config_requires_zero_cost_provider():
    with pytest.raises(ValueError, match="provider must be zero-cost"):
        AgentModelConfig(
            agent_name="Centinela",
            provider="anthropic",  # type: ignore[arg-type]
            primary_model="claude-3-haiku",
            fallback_model="llama-3.1-8b-instant",
        )


# --- LLMRoutingTable ------------------------------------------------------


def test_routing_table_has_all_six_agents():
    table = get_routing_table()
    agent_names = {c.agent_name for c in table.configs}
    assert agent_names == {
        "Nexus",
        "Radarito",
        "Cerebrito",
        "Centinela",
        "Mensajerito",
        "Auditor",
    }


def test_routing_table_no_duplicate_agents():
    table = get_routing_table()
    names = [c.agent_name for c in table.configs]
    assert len(names) == len(set(names))


def test_centinela_uses_groq():
    table = get_routing_table()
    cfg = table.get("Centinela")
    assert cfg.provider == "groq"
    assert cfg.primary_model == "llama-3.1-8b-instant"


def test_mensajerito_uses_groq():
    table = get_routing_table()
    cfg = table.get("Mensajerito")
    assert cfg.provider == "groq"
    assert cfg.primary_model == "llama-3.1-8b-instant"


def test_cerebrito_uses_google_ai_studio():
    table = get_routing_table()
    cfg = table.get("Cerebrito")
    assert cfg.provider == "google_ai_studio"
    assert cfg.primary_model.startswith("gemini")


def test_auditor_uses_google_ai_studio():
    table = get_routing_table()
    cfg = table.get("Auditor")
    assert cfg.provider == "google_ai_studio"
    assert cfg.primary_model.startswith("gemini")


def test_radarito_uses_cloudflare_or_openrouter():
    table = get_routing_table()
    cfg = table.get("Radarito")
    assert cfg.provider in ("cloudflare_workers_ai", "openrouter")


def test_nexus_is_dynamic_provider():
    table = get_routing_table()
    cfg = table.get("Nexus")
    assert cfg.provider == "dynamic"
    assert cfg.primary_model == "intent-based"


# --- select_model_for_agent ----------------------------------------------


def test_select_model_for_agent_returns_primary_by_default():
    result = select_model_for_agent("Centinela")
    assert result.selected_provider == "groq"
    assert result.selected_model == "llama-3.1-8b-instant"
    assert result.is_fallback is False


def test_select_model_for_agent_can_force_fallback():
    result = select_model_for_agent("Centinela", use_fallback=True)
    assert result.selected_provider == "groq"
    assert result.selected_model != "llama-3.1-8b-instant"
    assert result.is_fallback is True


def test_select_model_for_agent_unknown_agent_raises():
    with pytest.raises(KeyError, match="unknown agent"):
        select_model_for_agent("NoSuchAgent")


def test_select_model_result_is_dataclass_with_expected_fields():
    result = select_model_for_agent("Auditor")
    assert hasattr(result, "selected_provider")
    assert hasattr(result, "selected_model")
    assert hasattr(result, "is_fallback")
    assert hasattr(result, "reason")
