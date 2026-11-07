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

T1. Create directory structure (completed in Step 1)
T2. Generate backend/tests/test_agent_contracts.py with Pydantic model validation tests
T3. Implement Pydantic models in backend/app/models/
T4. Write focused tests for each model (RED → GREEN → REFACTOR)
T5. Create initial Astro 4+ page skeleton for hub and spokes
T6. Set up FastAPI backend with router stubs
T7. Configure MCP server adapters (Context7, Engram, news, knowledge, security, notifier)
T8. Implement multi-agent framework (Nexus, Radarito, Cerebrito, Centinela, Mensajerito, Auditor)

## Log

L1. 2026-11-06: Feature document created - showcase-platform.md
L2. 2026-11-06: Directory structure initialized per specification
L3. 2026-11-06: First TDD test file to be generated

## Delivery Strategy

Organic Driven Development with feature document tracking. First commit will initialize the directory structure. Subsequent work units will follow the Red-Green-Refactor cycle with contract testing.

Risk: none (initial setup task, contained scope)