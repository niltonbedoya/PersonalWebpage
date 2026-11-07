# Feature Document: Showcase Platform Initialization

## Specs

S1. Project structure must follow the modular layout specified in the prompt maestro:
- web/src/ with components, layouts, pages (industrial-smt, software-engineering), styles
- backend/app/ with agents, core, db, mcp, models, routers
- data/ for corpus técnico sanitizado
- docs/ for specification documents

S2. First TDD test file must validate all 5 Pydantic v2 models:
- NewsItemPayload
- RAGResponsePayload  
- GuardrailVerdict
- LeadAlertPayload
- AuditVerdict

S3. Test suite must initially fail (Red Phase) before any model implementation.

S4. Directory structure must be created without external dependencies first, then populated.

S5. All code must be compatible with zero-cost LLM routing:
- Groq Cloud for Centinela/Mensajerito
- Google AI Studio for Cerebrito/Auditor
- Cloudflare Workers AI / OpenRouter for Radarito

## Tasks

T1. Create directory structure — CLOSED INCOMPLETE (committed ade990e: agents/, mcp/, routers/, models.py; core/ and db/ were missing vs S1). 2026-11-07: scaffolds backend/app/core/ + backend/app/db/ created (empty packages with docblocks), data/ given placeholder README (population deferred to F5)
T2. Generate backend/tests/test_agent_contracts.py — DONE (5 contract tests)
T3. Implement Pydantic models — DONE (backend/app/models.py)
T4. Write focused tests per model (RED → GREEN → REFACTOR) — DONE (pytest 5 passed)
T5. Create initial pages for hub and spokes — DONE (plain HTML in web/public/pages/, deviation: .astro fails via esbuild in this environment)
T6. Set up FastAPI backend with routers — DONE (`python -m backend.main`, /static/pages serving verified 200)
T7. Configure MCP server adapters — DONE (backend/app/mcp/adapters.py)
T8. Implement multi-agent framework — DONE (backend/app/agents/__init__.py)
T9. F1 hardening: negative/boundary contract tests for all 5 models (round-trip, missing fields, invalid literals, HttpUrl rejection, grounding 0-1 bounds, summary 300 limit) — DONE (2026-11-07: backend/tests/test_contracts_hardening.py, 27 assertions, 32 passed total; no RED step because the models already enforced the spec constraints — tests pin existing frozen behavior; legacy suite docstring corrected to happy-path smoke)

## Log

L1. 2026-11-06: Feature document created - showcase-platform.md
L2. 2026-11-06: Directory structure initialized per specification
L3. 2026-11-06: First TDD test file to be generated
L4. 2026-11-07: Static serving fixed (StaticFiles mount points to web/public via absolute Path); server verified: /health 200, 3 HTML pages 200
L5. 2026-11-07: README.md and AGENTS.md created at repo root; git baseline commit ade990e; CodeGraph + skill-registry initialized
L7. 2026-11-07: F6 complete — resilience suite closed: T2 Centinela battery (57 tests, 100% rejection rate), T3 Auditor battery (9 tests: grounding/PII/credentials/real brands), T4 end-to-end anti-fuga (5 tests, zero leakage). Fixed baseline defects: centinela.py off-topic now blocked (is_allowed=False), auditor.py real-brand detection added. Suite 395 passed, 0 failed.
L7. 2026-11-07: Roadmap audit: existing 5 contract tests are happy-path only (names say "invalid_missing_fields" but no negative/boundary case is asserted; except-ValidationError converts rejection into failure) — F1 REOPENED as T9. Full per-phase test/audit requirements persisted in docs/plan_de_fases_verificacion.md (F1-F7 with exit criteria + cross-cutting rules).

## Delivery Strategy

Organic Driven Development with feature document tracking. First commit will initialize the directory structure. Subsequent work units will follow the Red-Green-Refactor cycle with contract testing.

Risk: none (initial setup task, contained scope)