"""LLM model routing per sub-agent with zero-cost fallback.

Defines which provider+model each runtime agent uses, plus a zero-cost
fallback per agent. Integrates with the gentle-ai.model-variants plugin
already registered in cli.json (cache of provider model variants).

Zero-cost provider matrix (docs/especificaci_n_y_resumen_de_arquitectura.md §4.2):
- Centinela & Mensajerito: Groq Cloud llama-3.1-8b-instant
- Cerebrito & Auditor: Google AI Studio gemini-1.5-flash / 2.0-flash
- Radarito: Cloudflare Workers AI / OpenRouter Free (qwen-2.5-7b or deepseek-chat)
- Nexus: dynamic provider selection by task intent
"""

from pydantic import BaseModel, Field, model_validator
from typing import Literal

ProviderType = Literal[
    "groq",
    "google_ai_studio",
    "cloudflare_workers_ai",
    "openrouter",
]

ZERO_COST_PROVIDERS: frozenset[str] = frozenset({
    "groq",
    "google_ai_studio",
    "cloudflare_workers_ai",
    "openrouter",
})


def is_zero_cost_provider(provider: str) -> bool:
    """Return True only for providers in the zero-cost matrix."""
    return provider in ZERO_COST_PROVIDERS


class AgentModelConfig(BaseModel):
    """Model assignment for one runtime sub-agent."""

    agent_name: str = Field(..., description="Unique agent name (Nexus, Radarito, …)")
    provider: str = Field(..., description="LLM provider (zero-cost only, or 'dynamic' for Nexus)")
    primary_model: str = Field(..., min_length=1, description="Primary model id")
    fallback_model: str = Field(..., min_length=1, description="Fallback model id (differs from primary)")
    temperature: float = Field(0.0, ge=0.0, le=2.0)
    max_tokens: int | None = Field(None, ge=1, description="Optional max output tokens")

    @model_validator(mode="after")
    def _fallback_differs_from_primary(self) -> "AgentModelConfig":
        # Nexus uses "intent-based" dynamic routing; primary and fallback are
        # intentionally identical because the provider is selected at runtime.
        if self.provider != "dynamic" and self.fallback_model == self.primary_model:
            raise ValueError("fallback must differ from primary")
        return self

    @model_validator(mode="after")
    def _provider_is_zero_cost_or_dynamic(self) -> "AgentModelConfig":
        if self.provider != "dynamic" and not is_zero_cost_provider(self.provider):
            raise ValueError("provider must be zero-cost")
        return self


class ModelSelectionResult(BaseModel):
    """Result of selecting a model for an agent."""

    selected_provider: str
    selected_model: str
    is_fallback: bool
    reason: str


class LLMRoutingTable:
    """Immutable routing table for the six runtime agents."""

    def __init__(self, configs: list[AgentModelConfig]) -> None:
        self._by_name: dict[str, AgentModelConfig] = {c.agent_name: c for c in configs}
        self.configs = list(configs)

    def get(self, agent_name: str) -> AgentModelConfig:
        if agent_name not in self._by_name:
            raise KeyError(f"unknown agent: {agent_name}")
        return self._by_name[agent_name]

    def __contains__(self, agent_name: object) -> bool:
        return agent_name in self._by_name

    def __iter__(self):
        return iter(self.configs)


def get_routing_table() -> LLMRoutingTable:
    """Build the canonical routing table for all six runtime agents."""

    configs = [
        AgentModelConfig(
            agent_name="Nexus",
            provider="dynamic",
            primary_model="intent-based",
            fallback_model="intent-based",
            temperature=0.0,
        ),
        AgentModelConfig(
            agent_name="Radarito",
            provider="cloudflare_workers_ai",
            primary_model="qwen-2.5-7b",
            fallback_model="deepseek-chat",
            temperature=0.2,
        ),
        AgentModelConfig(
            agent_name="Cerebrito",
            provider="google_ai_studio",
            primary_model="gemini-1.5-flash",
            fallback_model="gemini-2.0-flash",
            temperature=0.1,
        ),
        AgentModelConfig(
            agent_name="Centinela",
            provider="groq",
            primary_model="llama-3.1-8b-instant",
            fallback_model="llama-3.1-70b-instant",
            temperature=0.0,
        ),
        AgentModelConfig(
            agent_name="Mensajerito",
            provider="groq",
            primary_model="llama-3.1-8b-instant",
            fallback_model="llama-3.1-70b-instant",
            temperature=0.1,
        ),
        AgentModelConfig(
            agent_name="Auditor",
            provider="google_ai_studio",
            primary_model="gemini-1.5-flash",
            fallback_model="gemini-2.0-flash",
            temperature=0.0,
        ),
    ]
    return LLMRoutingTable(configs)


def select_model_for_agent(
    agent_name: str,
    use_fallback: bool = False,
) -> ModelSelectionResult:
    """Select the provider+model for an agent.

    Returns the primary model unless use_fallback=True. The result carries
    a reason string so orchestrators can log why a fallback was chosen.
    """
    table = get_routing_table()
    cfg = table.get(agent_name)

    if use_fallback:
        return ModelSelectionResult(
            selected_provider=cfg.provider,
            selected_model=cfg.fallback_model,
            is_fallback=True,
            reason="fallback requested by orchestrator",
        )

    return ModelSelectionResult(
        selected_provider=cfg.provider,
        selected_model=cfg.primary_model,
        is_fallback=False,
        reason="primary model",
    )
