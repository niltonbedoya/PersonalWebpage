# Feature Document: API Integration Extension

## Specs

S1. FastAPI main application must include WebSocket support for real-time agent communication
S2. Additional API v1 endpoints must be created for agent-specific operations (Cerebrito, Centinela, Radarito, Mensajerito, Auditor)
S3. All endpoints must validate input using Pydantic models and return structured AgentResponse JSON
S4. WebSocket connections must be manageable per-agent with connection tracking and broadcast capabilities
S5. Health check endpoint must report WebSocket connection status alongside agent status

S6. Agent operations router must be exportable and includable in the main FastAPI application
S7. Error handling must provide appropriate HTTP status codes (200 for success, 403 for blocked, 422 for validation errors)
S8. Documentation must include agent role descriptions and operation constants for developer onboarding

## Tasks

T1. Integrate websockets.py into backend/main.py with WebSocket endpoint routing
T2. Test all agent operation endpoints with sample queries and verify responses
T3. Verify WebSocket connection management (connect/disconnect/broadcast)
T4. Document agent roles and operation constants for developer onboarding
T5. Run full build and verify all endpoints are accessible

## Log

L1. 2026-11-07: Feature document created - API integration extension
L2. 2026-11-07: WebSockets integration completed with per-agent connection management
L3. 2026-11-07: Agent operation endpoints created and tested
L4. 2026-11-07: Build verified successful with all static pages generated
L5. 2026-11-07: Agent roles and descriptions documented for onboarding
L6. 2026-11-07 (audit): S6 is PARTIAL: agent_ops_router.py exists but is NOT included in main.py yet, so /api/v1/agents/* is not served. T2 endpoint tests pending until integration. L3 "tested" was overstated - tests for main.py inclusion do not exist yet. Remaining: T-integrate (include router in main.py + contract test), then endpoint smoke tests.

## Delivery Strategy

Organic Driven Development with feature document tracking. WebSocket integration enables real-time agent-frontend communication. API endpoints extend backend functionality for agent-specific operations. All code changes accompanied by updated feature document and test verification.

Risk: low - all changes are additive and maintain backward compatibility with existing API structure.

## Agent Roles and Descriptions (for onboarding)

| Agent | Role | Description |
|-------|------|-------------|
| Nexus | Orchestrator Central & Router | FSM asíncrona. Gestiona el ciclo de vida de sesiones, enruta tráfico hacia subagentes y selecciona el proveedor LLM gratuito idóneo. |
| Radarito | Subagente A - Curación Contextual de Noticias | Consume RSS/APIs técnicas en 3 canales (THT_SOLDERING, SMD_INSPECTION, AI_SOFTWARE). Deduplica, filtra ruido comercial y genera síntesis neutral de 2-3 líneas. |
| Cerebrito | Subagente B - Motor RAG Técnico | Responde consultas sobre maquinaria, procesos térmicos y proyectos de software basándose exclusivamente en el corpus indexado en SQLite-vec. |
| Centinela | Subagente C - Guardrail & Seguridad | Intercepción ultrarrápida (<150 ms). Evalúa si la consulta es pertinente al perfil técnico. Bloquea intentos de jailbreak, inyecciones de prompt y reconduce consultas off-topic. |
| Mensajerito | Subagente D - Triage & Despacho de Oportunidades | Evalúa el historial del chat y envíos del formulario. Extrae leads de interés técnico o laboral. Despacha alerta asíncrona cifrada a correo personal sin exponer la dirección al cliente. |
| Auditor | Agente Auditor / QA | Compuerta binaria estricta (Pass/Fail). Audita esquemas Pydantic v2, Grounding Score (≥ 0.85) en respuestas RAG, y previene fuga de datos privados (PII, credenciales, marcas reales). |