# Feature Document: F2 — Agentes Runtime con Mocks Deterministas

**Objective:** six runtime agents hardened by tests against deterministic
offline fixtures, per `docs/plan_de_fases_verificacion.md` (F2) and the
prompt maestro §5 (TDD test strategy).
**Branch:** main (single-developer repo). **Test runner:** `python -m pytest backend/tests/ -v`

## Specs

S1. "Fixtures Deterministas de Inferencia: Fixtures locales de respuestas de Groq, Google AI Studio y Cloudflare para ejecutar la suite completa en pytest de forma offline y determinista."
S2. "Pruebas de Contrato (Contract Testing): Validar que cada subagente produce salidas conformes al 100% con los modelos Pydantic v2."
S3. Auditor gate: "Compuerta binaria estricta (Pass/Fail). Audita esquemas Pydantic v2, Grounding Score (>= 0.85) en respuestas RAG, y previene fuga de datos privados (PII, credenciales, marcas reales)." AuditVerdict.status only ever "APPROVED" or "REJECTED" (contract Literal).
S4. "Batería de Resiliencia de Centinela: Suite de 50+ vectores de prueba con intentos de jailbreak, desvíos (política, cocina, código genérico) y confirmación de que is_allowed == False." (F2 covers the ≥10-vector battery slice; full 50+ battery is F6.)
S5. Radarito: dedup, noise filtering, neutral synthesis respecting summary <= 300 chars.
S6. Mensajerito: lead extraction from transcript/form, priority by opportunity type, notifier dispatch mocked; sender_contact NEVER leaked into chat-facing output.
S7. Nexus: FSM session lifecycle + intent routing map to the right agent.
S8. All tests offline, deterministic, no network; agent code logs ASCII-only (Windows cp1252 console).
S9. Zero-cost provider assignment honored: Groq -> Centinela/Mensajerito, Google AI Studio -> Cerebrito/Auditor, Cloudflare/OpenRouter -> Radarito.

## Tasks

T1. Split backend/app/agents/__init__.py into one module per agent (nexus, radarito, cerebrito, centinela, mensajerito, auditor) with __init__ re-exporting all classes — inline (parent-owned mechanical refactor), S8.
T2. Centinela: >=10-vector fixture battery (injection/jailbreak -> is_allowed False + PROMPT_INJECTION + CRITICAL/HIGH risk; off-topic -> polite redirect_message without echoing payload; technical prompt -> allowed TECHNICAL_PROFILE LOW; decision latency <150ms measured in-test) — DONE inline 2026-11-07 (subagent wave blocked by runtime free-tier limit; executed parent-inline). backend/tests/test_agent_centinela.py (10 injection vectors parametrized, 4 off-topic, 5 technical, latency assert). Fixes applied to baseline: centinela.py risk_keywords expanded (developer mode, DAN, reveal, configuration, tokens, secrets, environment variables, ignore all, prior rules, filtering). S2-S4, S8.
T3. Radarito: dedup (same title+url rejected, same title different url accepted), commercial-noise filter, category validation, summary truncation <=300, valid NewsItemPayload output — DONE inline 2026-11-07. backend/tests/test_agent_radarito.py. Fix applied to baseline: radarito.py dedup now compares str(source_url) (stored value may be an HttpUrl object vs incoming string). S5.
T4. Auditor: fix invalid "APPROVED_WITH_SANITIZATION" status (binary gate ONLY), valid structured payload -> APPROVED, rag grounding <0.85 -> REJECTED, >=0.85 -> APPROVED, PII/credentials detection -> REJECTED with failure_reasons — DONE inline 2026-11-07. backend/tests/test_agent_auditor.py (7 scenarios). Fixes applied to baseline: auditor.py removed APPROVED_WITH_SANITIZATION (any failure_reason -> REJECTED), rag with empty cited_sources -> REJECTED. S3.
T5. Cerebrito: grounding-score contract vs fixture chunks (no hardcoded 0.9), no-answer outside corpus -> is_fully_grounded False, citations from corpus — wave 2.
T6. Mensajerito: lead classification test battery + mock notifier dispatch — wave 2.
T7. Nexus FSM: session lifecycle + routing-map tests; full mock dispatch integration (guardrail -> agent -> auditor) — wave 2.

## Log

L2. 2026-11-07: F2 wave 1 closed: T2 Centinela battery (10 injection + 4 off-topic + 5 technical + latency), T3 Radarito dedup/noise/truncation, T4 Auditor binary gate (PII/credentials, grounding <0.85, no-citations). All three test modules green; suite total 67 passed. Baseline defects fixed in centinela.py (risk_keywords expanded), radarito.py (dedup str() comparison), auditor.py (removed APPROVED_WITH_SANITIZATION, added rag citation check). Wave 2 (T5 Cerebrito grounding-from-chunks, T6 Mensajerito lead battery, T7 Nexus FSM + full mock dispatch integration) remains pending. Subagent delegation was attempted but blocked by OpenCode free-tier usage limit — wave executed parent-inline instead.
