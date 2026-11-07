# Feature Document: F3 — API Routers + WebSockets

**Objective:** connect the API routers (/chat, /news, /contact, /health) and the
agent_ops_router (/api/v1/agents/*) to the real agents implemented in F2, and
integrate agent_ops_router into main.py. Per `docs/plan_de_fases_verificacion.md`
(F3) and prompt maestro §5 (TDD).
**Branch:** main. **Test runner:** `python -m pytest backend/tests/ -v`
**Test approach:** FastAPI TestClient integration tests against real agents
(Nexus FSM, Centinela, Cerebrito, Radarito, Mensajerito, Auditor) — offline,
deterministic, no network.

## Specs

S1. `/chat` (POST) — chat orquestado por Nexus: recibe mensaje + intent, ejecuta
guardrail (Centinela) primero, si es allowed enruta al agente destino y devuelve
respuesta auditada (Auditor). Respuesta debe pasar por el gate del Auditor.
S2. `/news` (GET) — feed curado por Radarito: devuelve NewsItemPayload válidos,
sin PII, categoría filtrada.
S3. `/contact` (POST) — formulario seguro con honeypot: honeypot llenado → éxito
falso + cero alerta despachada; envío válido → LeadAlertPayload despachado
(notifier mocked).
S4. `/health` (GET) — estado global + agentes activos, contratos Pydantic listados.
S5. `/ws/{agent_name}` — WebSocket por agente, routing vía `websocket_route` en
`backend/websockets.py` (ya existe).
S6. `agent_ops_router` integrado en `main.py` bajo `/api/v1/agents/*`:
endpoints cerebrito/query, centinela/evaluate, radarito/fetch-news,
mensajerito/evaluate-lead, audit/verify — operando contra agentes reales.
S7. `audit/verify` debe usar gate binario estricto (APPROVED/REJECTED solo) —
no `APPROVED_WITH_SANITIZATION` (defecto corregido en F2 T4; replicar aquí).
S8. Todos los tests offline, deterministas, sin red; logs ASCII-only (cp1252).

## Tasks

T1. Create feature doc + integration test plan (this document).
T2. Chat router (`backend/app/routers/__init__.py` chat endpoint): connect to
real Nexus + Centinela + Cerebrito + Auditor chain. Tests: happy path,
blocked prompt returns guardrail redirect, audit verdict attached.
Delegated worker (gentle-ai-worker).
T3. News router (GET /news): return real NewsItemPayload from Radarito channels.
Tests: valid payload, category filtering, no PII. Delegated worker.
T4. Contact router (POST /contact): honeypot detection, lead dispatch to
Mensajerito + notifier mock. Tests: honeypot → no dispatch, valid → dispatch.
Delegated worker.
T5. Health router: list active agents + Pydantic contracts + WebSocket status.
Tests: all 6 agents listed, contracts present. Delegated worker.
T6. Integrate agent_ops_router into main.py; fix APPROVED_WITH_SANITIZATION in
audit_verify_endpoint to strict binary gate. Tests: each /api/v1/agents/*
endpoint returns real agent output, audit endpoint binary only.
Delegated worker.
T7. WebSocket /ws/{agent_name}: verify routing to correct agent handler,
connection status via /ws/status. Tests: route exists per agent, status shape.
Delegated worker (read-only against existing websockets.py).

## Allowed edit surfaces (per task — passed to workers)
T2: backend/app/routers/__init__.py (chat endpoint only), backend/tests/test_api_chat.py (new)
T3: backend/app/routers/__init__.py (news endpoint only), backend/tests/test_api_news.py (new)
T4: backend/app/routers/__init__.py (contact endpoint only), backend/tests/test_api_contact.py (new)
T5: backend/app/routers/__init__.py (health endpoint only), backend/tests/test_api_health.py (new)
T6: backend/main.py (include agent_ops_router), backend/agent_ops_router.py (audit binary fix), backend/tests/test_api_agent_ops.py (new)
T7: backend/tests/test_api_websockets.py (new) — read-only against websockets.py

## Log

L1. 2026-11-07: Feature doc created. F2 complete (131 tests green). F3 stubs exist
in backend/app/routers/__init__.py (hardcoded responses, not connected to agents)
and backend/agent_ops_router.py (detailed endpoints, audit endpoint has
APPROVED_WITH_SANITIZATION defect to fix). main.py does NOT include agent_ops_router.
