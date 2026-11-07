# PLAN DE FASES, TESTS Y AUDITORÍAS (ROADMAP SDD)

**Metodología:** Gentle-AI (ODD + TDD estricto). Plan derivado de la auditoría
2026-11-07 contra `docs/prompt_maestro_de_inicio.md` y
`docs/especificaci_n_y_resumen_de_arquitectura.md`.
**Regla de oro:** ninguna fase se marca cerrada sin tests observados en verde;
toda fase entra como feature doc en `odd/` (Specs `S#`, Tasks, Log).

---

## Cómo leer este plan

Cada fase especifica: **objetivo**, **tests obligatorios** (deben existir antes
de cerrar), **auditorías/gates** (compuertas de calidad — las de producto son
el Auditor; las de build son gates de CI), **estado** y **criterio de salida**.
Los tests negativos y de límite son obligatorios: los tests de happy path no
cierran fases (lección de la auditoría F1: 5 tests de nombre `invalid_missing`
que en realidad solo probaban el caso válido).

---

## F1 — Contratos Pydantic v2

**Objetivo:** los 5 contratos (`NewsItemPayload`, `RAGResponsePayload`,
`GuardrailVerdict`, `LeadAlertPayload`, `AuditVerdict`) validados al 100%:
válido, inválido y límite.

**Tests obligatorios (por modelo):**
1. Serialización round-trip: dump → construct → dump idéntico.
2. Negativo: campo requerido faltante → `ValidationError` (sin try/except
   envolviendo — el Rechazo ES la aserción deseada).
3. `Literal` inválido rechazado (ej: `category="NO_EXISTE"`).
4. `HttpUrl` inválido rechazado (`source_url="no-es-url"`).
5. Límites: `grounding_score` 0.0 y 1.0 válidos; −0.1 y 1.1 rechazados;
   `summary` exactamente 300 OK, 301 rechazado; `failure_reasons`
   default `[]`.

**Auditorías/gates:** suite `pytest backend/tests/ -v` verde; feature doc con
evidencia RED→GREEN observada.

**Estado:** ✅ CERRADA 2026-11-07 — 27 aserciones de hardening en
`backend/tests/test_contracts_hardening.py` (round-trip, negativos por
parametrización, Literals inválidos, HttpUrl/datetime inválidos, límites de
grounding y summary, defaults opcionales); 32 passed en total. Sin RED en
esta ronda: los modelos ya cumplían la spec — los tests pinean el contrato
congelado (RED correspondiente se observó originalmente en S3). Seguimiento:
`odd/showcase-platform.md` T9.

**Criterio de salida:** suite ≥25 aserciones (5 modelos × ~5 verificaciones)
en verde, RED observado antes de escribir los tests nuevos.

---

## F2 — Agentes runtime con mocks deterministas

**Objetivo:** Nexus (FSM) + Radarito, Cerebrito, Centinela, Mensajerito, y el
gate del Auditor operando completamente offline con fixtures.

**Tests obligatorios:**
1. Fixtures LLM probabilístico-deterministas para Groq / Gemini /
   Cloudflare-OpenRouter (grabadas, sin red; usadas por F2–F6).
2. FSM de Nexus: ciclo de vida de sesión (DOING→WAITING-like según despacho),
   ruta inválida, agente no registrado, timeout del subagente.
3. Selección de proveedor: cada agente recibe su proveedor según la matriz
   zero-cost (Groq↔Centinela/Mensajerito, Gemini↔Cerebrito/Auditor,
   CF/OpenRouter↔Radarito).
4. Radarito: dedup por fuente+hash, filtro de ruido comercial, síntesis
   ≤3 líneas que respeta `summary ≤ 300`, `NewsItemPayload` válido.
5. Centinela: latencia de decisión <150 ms medible contra fixture;
   salida `GuardrailVerdict` tipada.
6. Mensajerito: extracción de lead desde transcript sintético;
   `LeadAlertPayload` con contacto NEVER expuesto en salidas del chat.
7. Auditor gates de F2: payload conforme → `APPROVED`; schema violado →
   `REJECTED` con `failure_reasons` no vacío.

**Auditorías/gates:** la salida de CADA subagente en el despacho con mock pasa
por el Auditor (assert `AuditVerdict.status == "APPROVED"` o bloqueo visible).
Coverage sobre `backend/app/agents/` sobre clean import sin red.

**Estado:** 🟡 EN PROGRESO — T2 (Centinela battery), T3 (Radarito), T4 (Auditor binary gate) cerrados 2026-11-07, 67 tests en verde. T5 Cerebrito, T6 Mensajerito, T7 Nexus FSM + full mock dispatch pendientes (wave 2).

**Criterio de salida:** despacho completo (guardrail→agente→auditor) verde en
suite offline; FSM cubre transiciones y errores.

---

## F3 — API + WebSockets

**Objetivo:** `/health`, `/chat`, `/news`, `/contact`, WS `/ws/{agent_name`
operando contra los agentes mockeados de F2; `agent_ops_router` integrado en
`main.py` (gap conocido).

**Tests obligatorios (FastAPI TestClient):**
1. `/health` contrato estable (agents activos listados).
2. `/chat`: happy path mockeado — respuesta pasa por Auditor (APPROVED);
   prompt de inyección simulado → guardrail bloquea (reconducción educada).
3. `/contact`: honeypot llenado → respuesta de éxito falsa + cero alerta
   despachada; envío válido → `LeadAlertPayload` despachado (mock del
   notifier).
4. `/news`: sin PII en respuesta; paginación/limite funcionando.
5. WS: conexión, mensaje tipado según contrato, disconnect limpio, agent
   inexistente → error no 500.
6. Errores: 422 vía Pydantic y 404 coherentes (no stacktrace en body).

**Auditorías/gates:** integration test de `/chat` exige veredicto del Auditor;
CI roja si algún endpoint escapa del gate en mock.

**Estado:** 🔴 routers existen, cero tests de request real.

**Criterio de salida:** suite de integration (TestClient) en verde; WS
testeados; `agent_ops_router` montado y auditado.

---

## F4 — Frontend Hub & Spoke

**Objetivo:** Hub + 2 Spokes + capas transversal (drawer RAG, feeds,
formulario), con la limitación de entorno documentada (HTML plano servido en
`/static/pages/`; Astro islands reintento exige repro — ver AGENTS.md).

**Tests obligatorios:**
1. Vitest sobre el JS de las islas (validación de form de contacto con
   honeypot client-side, render de feed con `NewsItemPayload` sanitizado,
   drawer RAG abre/cierra y envía query).
2. Playwright E2E: hub → spoke industrial → spoke software → formulario;
   navegación completa sin 404.
3. Snapshot de contenido: cero marcas reales/PII en los HTML publicados
   (checklist de sanitización en build).

**Auditorías/gates:** sanitización de contenido expuesto ( Auditor-side en
runtime; checklist manual reproducible en build para v1).

**Estado:** ⚠️ páginas existen, cero tests ni checks.

**Criterio de salida:** Vitest + Playwright en verde sobre las páginas
servidas; caso feliz de formulário cubierto.

---

## F5 — RAG (SQLite-vec)

**Objetivo:** corpus sanitizado en `data/` indexado localmente; Cerebrito
responde con score y citas reales.

**Tests obligatorios:**
1. Chunking y indexado del corpus (idempotente, top-k estable).
2. Recuperación: query conocida → chunks correctos del corpus.
3. Grounding calculado sobre corpus (no de entrada): score ≥0.85 obliga
   `is_fully_grounded=True` con `cited_sources` no vacía y verfiables como
   dentro del corpus.
4. Umbral: score <0.85 → respuesta "no contesto fuera del corpus"
   (`is_allowed=false`-equivalente / guardrail de dominio).
5. Cero alucinación: pregunta fuera de dominio → máxima apertura sobre el
   corpus (síntesis neutral, no invento).

**Auditorías/gates:** **batería de sanitización del corpus** (regex
PII/credenciales/marcas sobre `data/`) como gate de build — corpus con fuga
NO se indexa; Auditor rechaza respuesta sin citas o con score reportado falsos
por el fixture.

**Estado:** 🔴 corpus vacío por diseño (deferred explicitamente; ver
`data/README.md`).

**Criterio de salida:** corpus indexado, suite RAG verde, gate de
sanitización funcionando (caso trampa bloqueado).

---

## F6 — Resiliencia (la batería de seguridad del spec §5)

**Objetivo:** LA evidencia central del portfolio — demostrar que el sistema
resiste abuso y no alucina.

**Tests obligatorios:**
1. Centinela: 50+ vectores (jailbreak, prompt injection, off-topic: política/
   cocina/código genérico) → `is_allowed == False`, `risk_level` correcto,
   `redirect_message` presente y SIN eco del payload malicioso.
2. Auditor: respuestas sintéticas alucinadas (score <0.85) → `REJECTED`;
   detección de PII/tokens/emails reales → bloqueo + `sanitized_payload`
   sin la fuga.
3. End-to-end anti-fuga: cadena completa con un payload malicioso → cero
   fuga en la respuesta final expuesta.

**Auditorías/gates:** esta fase ES la auditoría; su suite es la compuerta
final. Métrica reportada: % de rechazos correctos (debe ser 100%).

**Estado:** 🔴 cero vectores.

**Criterio de salida:** 100% de los vectores bloqueados en verde; suite corre
sin red.

---

## F7 — Deploy + CI

**Objetivo:** entregables en producción (Cloudflare Pages + backend) y CI
local como gate de calidad permanente.

**Tests/gates obligatorios:**
1. CI offline: suite completa (F1–F6) en verde como requisito de cada push.
2. Smoke post-deploy: `/health` 200 + páginas 200 en dominio real.
3. Anti-secrets: `.env` no trackeado (gitignore ya cubre), check de
   credenciales en el bundle/estructura final (no credenciales client-side).
4. Sanitización de `docs/` y repo: cero datos reales en el publicado.

**Auditorías/gates:** git log limpio; métricas en el README actualizadas solo
con evidencia.

**Estado:** 🔴 no iniciada (última fase, no urgente).

**Criterio de salida:** CI verde en ambiente actualizado; smoke test
verificado manualmente o por script.

---

## Requisitos transversales (todas las fases)

1. Cada fase = **un feature doc `odd/`** con Specs textuales del prompt
   maestro; cada test nace en RED.
2. **Work-unit commits** ~400 líneas con tests y docs; push/PR humanos.
3. **Ningún "DONE"** sin evidencia observada (lección T1 en
   `odd/showcase-platform.md` L6).
4. mocks deterministas únicos reusados — jamás red en tests.
5. Toda regresión detectada se pina con test antes de cerrar la tarea.
6. El plan se actualiza en cada cierre de fase (Log abajo); este doc es la
   fuente de estado del roadmap (el README enlaza aquí).

---

## Log

L1. 2026-11-07: Plan creado desde la auditoría SDD (veredicto: F1 reabierta
    por tests happy-path insuficientes; F2–F7 sin apertura; los tests de
    `test_agent_contracts.py` no validan negativos ni límites). Plan marcado
    como fuente de estado del roadmap; F1 reabierta como T9 en
    `odd/showcase-platform.md`.
L2. 2026-11-07: F1 CERRADA — `test_contracts_hardening.py` (27 aserciones:
    round-trip x2, missing-field x10 parametrizadas, Literal inválido x3,
    HttpUrl + datetime inválidos, límites grounding/summary, defaults
    opcionales x4); suite completa 32 passed; docstring legacy honestado a
    happy-path smoke. F2 abierta como próxima fase.
