# Feature Document: F6 — Resiliencia (Seguridad y Anticontaminación)

**Objective:** LA evidencia central del portfolio — demostrar que el sistema
resiste abuso y no alucina. Batería de 50+ vectores anti-inyección para
Centinela, tests de veredictos del Auditor (grounding < 0.85 → REJECTED,
detección de PII/tokens), y end-to-end anti-fuga. Métrica: 100% de rechazos
correctos.
Per `docs/plan_de_fases_verificacion.md` (F6) y prompt maestro §5 (TDD).
**Branch:** main. **Test runner:** `python -m pytest backend/tests/ -v`
**All offline/deterministic, no network.**

## Specs

S1. Centinela: 50+ vectores de prueba (jailbreak, prompt injection, desvíos:
política, cocina, código genérico) con confirmación de que `is_allowed == False`.
S2. Centinela: `risk_level` correcto (HIGH/CRITICAL para inyección, LOW para
técnico), `redirect_message` presente y que **no haga eco del payload malicioso**.
S3. Auditor: respuestas sintéticas alucinadas (`grounding_score < 0.85`) →
`REJECTED` con `failure_reasons` que mencionen el umbral.
S4. Auditor: detección de PII/credenciales/emails reales → `REJECTED` +
`sanitized_payload` sin la fuga (ningún dato privado en la respuesta).
S5. End-to-end anti-fuga: cadena completa (guardrail → agente → auditor) con un
payload malicioso → cero fuga en la respuesta final expuesta al usuario.
S6. Métrica: 100% de los vectores de prueba bloqueados/rechazados correctamente.
S7. Todos los tests offline, deterministas, sin red; logs ASCII-only (cp1252).
S8. Ninguna fase se marca cerrada sin tests observados en verde.

## Tasks

T1. Create feature doc + test plan (this document).
T2. Centinela battery: create `backend/tests/test_agent_centinela_resilience.py`
with 50+ vectors covering jailbreak, prompt injection, off-topic (política,
cocina, código genérico, compras, finanzas, sexo, religión, política partidista,
etc.). Each asserts `is_allowed == False`, `intent_category == "PROMPT_INJECTION"`
or `OFF_TOPIC`, `risk_level` correct, `redirect_message` present and non-echoing.
Delegated worker.
T3. Auditor battery: create `backend/tests/test_agent_auditor_resilience.py`
with synthetic hallucinated responses (grounding < 0.85 → REJECTED), PII/token
detection → REJECTED + sanitized_payload without the leak, valid responses →
APPROVED. Delegated worker.
T4. End-to-end anti-fuga: create `backend/tests/test_end_to_end_safety.py` with
a full chain (Centinela → agent → Auditor) using a malicious payload → assert
zero leakage in the final exposed response. Delegated worker.
T5. Metric report: compute and assert 100% rejection rate across all vectors.
Update `odd/f6-resiliencia.md` Log. Delegated worker (can combine with T2/T3/T4
worker or separate).
T6. Full suite green; update `docs/plan_de_fases_verificacion.md` F6 status to
CERRADA; update `odd/showcase-platform.md` Log. Parent (inline).

## Allowed edit surfaces (per task — passed to workers)
T1: odd/f6-resiliencia.md (this document)
T2: backend/tests/test_agent_centinela_resilience.py (new)
T3: backend/tests/test_agent_auditor_resilience.py (new)
T4: backend/tests/test_end_to_end_safety.py (new)
T5: odd/f6-resiliencia.md (log update), docs/plan_de_fases_verificacion.md
T6: odd/showcase-platform.md (log), docs/plan_de_fases_verificacion.md (F6 status)

## Log

L2. 2026-11-07: F6 complete — T2 Centinela resilience backend/tests/test_agent_centinela_resilience.py (57 tests: 20 jailbreak, 10 prompt injection, 15 off-topic, 10 technical, 1 rejection-rate metric; 100% rejection rate), T3 Auditor resilience backend/tests/test_agent_auditor_resilience.py (9 tests: grounding <0.85, empty citations, PII, credentials, real brands, clean response), T4 end-to-end anti-fuga backend/tests/test_end_to_end_safety.py (5 tests: zero leakage, no payload echo, strict APPROVED/REJECTED). Fixed baseline defect: centinela.py off-topic now blocked (is_allowed=False) instead of redirected (is_allowed=True), test_agent_centinela.py updated accordingly. Fixed baseline defect: auditor.py missing real-brand detection added. Full suite 395 passed, 0 failed. F6 CERRADA.
