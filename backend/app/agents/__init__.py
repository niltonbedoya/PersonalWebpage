"""Multi-Agent Framework for Showcase Platform

Six-agent runtime (see docs/prompt_maestro_de_inicio.md §3.1 and
docs/plan_de_fases_verificacion.md F2):

- Nexus:      Orquestador central & Router (FSM)
- Radarito:   Subagente A - Curación Contextual de Noticias
- Cerebrito:  Subagente B - Motor RAG Técnico
- Centinela:  Subagente C - Guardrail & Seguridad
- Mensajerito:Subagente D - Triage & Despacho de Oportunidades
- Auditor:    Agente Auditor / QA - Binary Gatekeeper

One module per agent; this package re-exports every class so that
``from backend.app.agents import Nexus`` keeps working. Edit surfaces for
phase F2 are the per-agent modules — never grow this __init__ beyond the
re-export list unless the agent set itself changes.
"""

from backend.app.agents.auditor import Auditor
from backend.app.agents.cerebrito import Cerebrito
from backend.app.agents.centinela import Centinela
from backend.app.agents.mensajerito import Mensajerito
from backend.app.agents.nexus import Nexus
from backend.app.agents.radarito import Radarito

__all__ = [
    "Auditor",
    "Cerebrito",
    "Centinela",
    "Mensajerito",
    "Nexus",
    "Radarito",
]
