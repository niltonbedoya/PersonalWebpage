# AGENTS.md — Guía para agentes de código que trabajen en este repositorio

Contexto mínimo para trabajar en este proyecto sin re-explorar todo. La fuente
de verdad funcional son `docs/prompt_maestro_de_inicio.md` (SDD/TDD) y
`docs/especificaci_n_y_resumen_de_arquitectura.md` (visión y fases). Los planes
de trabajo viven en `odd/` (Organic Driven Development).

## Qué es este proyecto

**Showcase Platform — Living Technical Portfolio**: portfolio web híbrido
(SMT/THT industrial + Software/IA) con backend FastAPI multiagente y frontend Astro.

## Comandos esenciales

```powershell
# Arrancar el backend (SIEMPRE desde la raíz del proyecto, nunca python backend/main.py)
python -m backend.main

# Build del frontend (Astro)
cd web && npx astro build

# Tests de contratos (TDD)
python -m pytest backend/tests/ -v
```

El backend queda en `http://localhost:8000`; las páginas HTML en
`/static/pages/{index,industrial-smt,software-engineering}.html`.

## Jerarquía de agentes del runtime

El sistema es una **arquitectura multiagente en dos capas**: en build-time la
orquestación de código corre bajo el framework JenteL AI (fuera del produto),
y en runtime la web ejecuta este núcleo FastAPI. Dentro del runtime hay
**un orquestador, cuatro subagentes especializados y un auditor transversal**.

### Orquestador — Nexus

| Campo | Detalle |
|---|---|
| Rol | Orquestador Central & Router (FSM asíncrona) |
| Responsabilidad | Ciclo de vida de sesiones, enrutamiento dinámico del tráfico hacia los subagentes, balanceo de carga y selección del proveedor LLM gratuito idóneo |
| Entrada | Eventos web, cron triggers, peticiones de chat |
| Salida | Despacho tipado a subagentes; respuesta consolidada |
| Memoria | Sincroniza estado de agentes vía `Engram MCP` (SQLite) |
| Auditoría | Todos sus logs son auditados por el Auditor |

**Flujo de despacho**: toda petición entrante la recibe primero el guardrail
(Centinela); las preguntas técnicas van al motor RAG (Cerebrito); el contexto de
noticias lo cura Radarito (programado); los leads los triá Mensajerito; y toda
salida pasa por la compuerta del Auditor antes de exponerse.

### Subagentes especializados

**Radarito — Subagente A (Curación Contextual de Noticias)**
- Entrada: feeds RSS/XML/APIs en 3 canales: `THT_SOLDERING`, `SMD_INSPECTION`, `AI_SOFTWARE`
- Salida: `NewsItemPayload` validado (deduplicado, filtrado de ruido comercial, síntesis neutral 2-3 líneas)
- Inferencia: Cloudflare Workers AI / OpenRouter Free (`qwen-2.5-7b`, `deepseek-chat`)
- Herramientas MCP: `mcp-server-news` (`fetch_rss`, `parse_article`, `cache_news`)

**Cerebrito — Subagente B (Motor RAG Técnico)**
- Entrada: query del usuario + chunks vectoriales de `SQLite-vec`
- Salida: `RAGResponsePayload` (grounding_score ≥ 0.85, citas de fuentes)
- Dominio: maquinaria, procesos térmicos y case studies de software (exclusivamente el corpus indexado)
- Inferencia: Google AI Studio (`gemini-1.5-flash` / `gemini-2.0-flash`)
- Herramientas MCP: `mcp-server-knowledge` (`query_sqlite_vec`, `get_equipment_spec`, `get_software_case_study`)

**Centinela — Subagente C (Guardrail & Seguridad)**
- Entrada: prompt crudo del visitante (intercepción perimetral < 150 ms)
- Salida: `GuardrailVerdict` (`is_allowed`, `risk_level`, `intent_category`, `redirect_message`)
- Bloqueos: jailbreak, prompt injection, off-topic (reconducción educada)
- Inferencia: Groq Cloud (`llama-3.1-8b-instant`)
- Herramientas MCP: `mcp-server-security` (`evaluate_prompt_safety`, `classify_intent`)

**Mensajerito — Subagente D (Triage & Despacho de Oportunidades)**
- Entrada: historial de chat y envíos del formulario de contacto
- Salida: `LeadAlertPayload` (prioridad P1-P3, tipo de oportunidad, contacto)
- Acción: alerta asíncrona cifrada al correo personal, sin exponer la dirección
- Inferencia: Groq Cloud (`llama-3.1-8b-instant`)
- Herramientas MCP: `mcp-server-notifier` (`dispatch_lead_notification`, `validate_contact`)

### Auditor — compuerta transversal (QA binaria)

No es un subagente de Nexus: es el **gatekeeper Pass/Fail** sobre las salidas de
todos los demás. Audita esquemas Pydantic v2, exige Grounding Score ≥ 0.85 en
respuestas RAG y previene fuga de datos (PII, credenciales, marcas reales).
Salida: `AuditVerdict` (`APPROVED` / `REJECTED` + `failure_reasons`).
Inferencia: Google AI Studio (instrucciones estrictas).

## Layout

- `backend/main.py` — entrada FastAPI (mount estático + routers + WebSockets)
- `backend/app/models.py` — 5 contratos Pydantic v2. **No romper sus firmas.**
- `backend/app/agents/__init__.py` — implementación de los 6 agentes
- `backend/app/mcp/adapters.py` — 6 adaptadores MCP (Context7, Engram, news, knowledge, security, notifier)
- `backend/app/routers/__init__.py` — `/chat` `/news` `/contact` `/health`
- `backend/websockets.py` — manager de conexiones y handlers `/ws/{agent_name}`
- `backend/agent_ops_router.py` — `/api/v1/agents/*` (pendiente de incluir en main.py)
- `backend/tests/test_agent_contracts.py` — suite de contratos (5 tests, en verde)
- `web/public/pages/` — páginas HTML (servidas por FastAPI como `/static/pages/`)
- `docs/` — especificaciones fuente; `odd/` — planes de trabajo SDD/ODD de sesión

## Convenciones obligatorias

1. **Consola Windows cp1252**: los `print()` del backend deben ser solo ASCII
   (nada de emojis ni acentos en logs, o `UnicodeEncodeError`).
2. **Pydantic v2**: contratos estrictos; cualquier payload nuevo debe pasar los
   tests de `backend/tests/`.
3. **TDD (Red → Green → Refactor)**: prohibido implementar sin test previo.
   Mocks deterministas de LLM (Groq / Gemini / Cloudflare) para tests offline.
4. **Arranque del servidor**: `python -m backend.main` desde la raíz del
   repositorio; `__file__`-based absolute paths para recursos estáticos.
5. **Datos de ejemplo**: contenido actual placeholder. Sin PII, credenciales ni
   marcas reales en el repo (el Auditor bloquea fuga de datos).
6. **Alcance del Spoke Industrial**: sin maquinaria Pick & Place (límite explícito
   de la spec).
7. **v1 sin APIs vivas expuestas**: los case studies son sanitizados/by design.
8. **SDD en `odd/`**: todo trabajo significativo se planifica en un feature
   document (`odd/<nombre>.md`) con Specs/Tasks/Log, y se verifica contra sus S#.

## Gotchas conocidos

- Se sirven las páginas desde `web/public/` vía `app.mount("/static", ...)` con
  `BASE_DIR = Path(__file__).resolve().parent.parent` (paths relativos fallan).
- Astro falla compilando `.astro` en este entorno (esbuild "Expected \";\" but
  found..."); las páginas viven como HTML plano en `web/public/pages/`.
- El 404 repetido de `GET /v1/models` en logs viene de un cliente externo de la
  máquina (no del proyecto); es inofensivo.
- El python activo es un venv de `hermes-agent` (siempre `python -m pip`):
  pytest ya instalado; si falta algo, `python -m pip install <paquete>`.

## Pendiente (roadmap corto)

1. Integrar `agent_ops_router` en `main.py`.
2. Probar `/chat`, `/news`, `/contact` y WebSocket con datos reales de request.
3. Reemplazar datos de ejemplo por reales (fotos, casos, LinkedIn/GitHub/CV PDF).
