# Feature Document: Hardening de Seguridad & RAG (Pre-Publicación)

**Objective:** Implementar defensa en profundidad antes de la exposición pública:
1. Honestidad estricta de Grounding RAG en `/chat` (score < 0.85 nunca se enmascara como general 1.0).
2. Detección en Centinela de técnicas avanzadas de evasión (Base64, delimitadores de sistema, inyección markdown).
3. Middleware de Rate Limiting en memoria para `/chat`, `/contact` y `/api/cv-request`.
4. Cabeceras de seguridad HTTP globales (`nosniff`, `DENY`, `strict-origin-when-cross-origin`, `Permissions-Policy`).

**Branch:** main. **Test runner:** `python -m pytest backend/tests/ -v`

## Specs

S1. En `/chat`, consultas técnicas con `grounding_score < 0.85` deben retornar su score real y mantener `output_type="rag"`; queda prohibido falsear `grounding_score = 1.0` o `agent = "Nexus"`.
S2. Centinela debe interceptar y bloquear con `is_allowed = False` y `risk_level = "CRITICAL"` o `"HIGH"`:
   - Delimitadores inyectados (`---BEGIN SYSTEM---`, `[SYSTEM INSTRUCTION]`, etc.).
   - Cargas útiles ofuscadas en Base64 o leet/espaciadas.
   - Enlaces de exfiltración de datos en markdown (`![exfil](https://...`).
S3. Rate Limiter middleware en FastAPI: limita ráfagas por IP en endpoints de IA (`/chat`: 30 req/min; `/contact` y `/api/cv-request`: 6 req/min) retornando HTTP 429 cuando se sobrepase.
S4. Middleware de cabeceras de seguridad HTTP: inyecta en todas las respuestas `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, y `Permissions-Policy: camera=(), microphone=(), geolocation=()`.
S5. TDD: suite de tests unitarios e integrados cubriendo S1..S4 sin regresiones sobre los 441 tests existentes.

## Tasks

T1. Crear feature doc `odd/hardening-security-rag.md`.
T2. Escribir tests para S1 (grounding honesty en `test_api_chat.py`).
T3. Implementar corrección de grounding honesty en `backend/app/routers/chat.py`.
T4. Escribir tests de Centinela para evasiones avanzadas en `backend/tests/test_agent_centinela_resilience.py`.
T5. Implementar reglas defensivas en `backend/app/agents/centinela.py`.
T6. Escribir tests para Rate Limiter y Security Headers en `backend/tests/test_security_hardening.py`.
T7. Implementar Rate Limiter y Security Headers middleware en `backend/app/core/security_headers.py` y montarlo en `backend/main.py`.
T8. Ejecutar suite completa de tests, verificar 100% verde, registrar memoria en Engram, commit y push a `main`.

## Log

L1. 2026-11-08: Hardening completado con éxito.
- S1: En `/chat`, consultas técnicas sin sustento retornan score real <0.85 de Cerebrito sin enmascarar en Nexus ni 1.0 (`backend/app/routers/chat.py`, `backend/tests/test_api_chat.py`).
- S2: Centinela intercepta vectores avanzados de evasión (Base64, delimitadores de sistema `<|im_start|>`, `<<sys>>`, exfiltración markdown `![...](...)`, scripts, espaciado `i g n o r e`) con `100% rejection rate` (`backend/app/agents/centinela.py`, `backend/tests/test_agent_centinela_resilience.py`).
- S3 & S4: Middleware `SecurityHardeningMiddleware` inyecta cabeceras de seguridad defensivas (`nosniff`, `DENY`, `strict-origin-when-cross-origin`, `Permissions-Policy`) y aplica Rate Limiting en memoria (30 req/min en `/chat`, 6 req/min en `/contact` y `/api/cv-request`) retornando HTTP 429 (`backend/app/core/security_headers.py`, `backend/tests/test_security_hardening.py`, `backend/main.py`).
- S5: Suite completa pasando al 100%: 455 tests en verde en 26.11s. Zero regressions.

