# AGENTS.md — Guía para agentes de código que trabajen en este repositorio

Contexto mínimo para trabajar en este proyecto sin re-explorar todo. La fuente
de verdad funcional son `docs/prompt_maestro_de_inicio.md` (SDD/TDD),
`docs/especificaci_n_y_resumen_de_arquitectura.md` (visión y fases) y
`docs/plan_de_fases_verificacion.md` (matriz de fases F1–F7 con tests y
auditorías por fase, y criterios de salida). Los planes de trabajo viven en
`odd/` (Organic Driven Development, ODD).

El proyecto arranca desde cero bajo la metodología **Gentle-AI** como método de
programación: orquestación ODD + TDD estricto. Los documentos describen el
objeto a construir, no un estado completado.

## Qué es este proyecto

**Showcase Platform — Living Technical Portfolio**: portfolio web híbrido
(SMT/THT industrial + Software/IA) con backend FastAPI multiagente, frontend
Astro (SSG) e inferencia LLM de costo cero. Objetivo: certificar autoridad
técnica ante reclutadores, colegas y oportunidades de colaboración.

## REGLA CRÍTICA — Dos jerarquías de agentes, nunca mezclarlas

Este repositorio contiene **dos estructuras de agentes completamente
distintas**. Confundirlas es el error más grave que un agente puede cometer
aquí.

### Capa 1 — Metodología (BUILD-TIME): Gentle-AI sobre el desarrollo

Es **cómo se programa este repositorio**, no código del producto. Vive solo en
la sesión de desarrollo (la conversación con el agente orquestador y sus
delegados). Nada de esta capa se implementa dentro de `backend/`, y sus nombres
nunca aparecen como agentes del producto.

Componentes de la orquestación Gentle-AI (ODD):

| Rol | Qué hace | Dónde existe |
|---|---|---|
| Orquestador ODD | Autoriza, explora, clasifica tamaño de tarea, escribe inline o delega, verifica, cierra, actualiza feature docs | Sesión de desarrollo (hilo principal) |
| Agente explorador | Mapea código/flujo y devuelve handoff de ~2k tokens con evidencia `path:line`. Solo lectura | Sub-sesión delegada |
| Agente worker (writer) | Implementa una unidad acotada con edit surfaces mínimas autorizadas, tests y docs juntos | Sub-sesión delegada |
| Agente verificador | Verificación independiente de cambios de riesgo alto (junta de verificación), contra specs S# | Sub-sesión delegada |

**Modelos LLM de los subagentes de Gentle-AI (build-time)** — definidos en
`config/gentle-ai/subagent-models.json`, integrado con el plugin
`gentle-ai.model-variants` ya registrado en `cli.json`. Todos los proveedores
son zero-cost (matriz de arquitectura §4.2). Cada subagente tiene primario y
fallback:

| Subagente | Proveedor | Modelo primario | Fallback | Temperatura | Rol |
|---|---|---|---|---|---|
| gentle-orchestrator | Google AI Studio | gemini-2.0-flash | gemini-1.5-flash | 0.1 | ODD orchestration: authorize, explore, classify, delegate, verify, close |
| gentle-ai-explore | Groq | llama-3.1-8b-instant | qwen-2.5-7b | 0.0 | Read-only code exploration + mapping, bounded handoffs |
| gentle-ai-worker | Google AI Studio | gemini-1.5-flash | llama-3.1-70b-instant | 0.1 | Bounded implementation unit, code+tests+docs |
| gentle-ai-verify | Google AI Studio | gemini-1.5-flash | llama-3.1-8b-instant | 0.0 | Independent verification of named high-risk items |

Fallback strategy: on provider unavailability or rate limit, switch to the
declared `fallback_model` for that subagent. Never fall back to a paid provider.
Validated by `tests/test_gentle_ai_subagent_models.py` (19 assertions).

1. **Planificación en `odd/`**: todo trabajo significativo se planifica en un
   feature document `odd/<feature>.md` con Specs (`S1..Sn`, citas textuales del
   pedido), Tasks y Log. Se lee el documento antes de tocar código y se reporta
   qué `S#` se cubrieron.
2. **TDD obligatorio**: Red → Green → Refactor. Prohibido implementar sin test
   previo. En v1 no hay APIs vivas expuestas; los tests funcionan offline con
   **mocks deterministas de LLM** (Groq / Google AI Studio / Cloudflare).
3. **Commits como work units**: slices revisables (~400 líneas), Conventional
   Commits, tests y docs junto al código. Push/PR/merge: decisión humana.
4. **Delegación con superficie mínima**: cada worker recibe solo los archivos
   exactos que puede editar ("Allowed edit surfaces"). Un worker jamás decide
   producto; devuelve gaps al orquestador.
5. Los agentes de esta capa NO tienen memoria del producto ni contratos
   Pydantic; su "producto" son commits testeados.

### Capa 2 — Producto (RUNTIME): la app funcional desplegada

Es **lo que la web ejecuta en producción** dentro del núcleo FastAPI. Sus
agentes viven en `backend/app/agents/` y responden a los usuarios reales del
portfolio. Detalle abajo en "Arquitectura multiagente del runtime".

| | Capa 1 (Gentle-AI, build-time) | Capa 2 (runtime del producto) |
|---|---|---|
| Propósito | Construir/verificar el código | Operar la web desplegada |
| Agentes | Orquestador, explorador, worker, verificador | Nexus, Radarito, Cerebrito, Centinela, Mensajerito, Auditor |
| Vida | Solo durante el desarrollo | En producción, tráfico de usuarios |
| Código | Fuera del repo (framework de trabajo) | `backend/app/agents/`, `backend/app/mcp/` |
| Enrutamiento LLM | N/A (programan con modelos del harness) | Zero-cost routing (Groq/Gemini/Cloudflare/OpenRouter) |

**Nunca** implementes un "agente worker" o "verificador" dentro del backend,
ni nombres un agente del runtime con nombres de la capa de construcción
(viceversa incluido).

## Arquitectura multiagente del runtime (el producto)

Sistema multiagente en FastAPI: **un orquestador, cuatro subagentes
especializados y un auditor transversal**.

**Flujo de despacho**: toda petición entra primero por el guardrail
(Centinela); lo técnico va al motor RAG (Cerebrito); las noticias las cura
Radarito (programado); los leads los triá Mensajerito; toda salida pasa por la
compuerta del Auditor antes de exponerse.

| Agente | Rol | Responsabilidad | Inferencia (costo cero) |
|---|---|---|---|
| **Nexus** | Orquestador central & router | FSM asíncrona, ciclo de vida de sesiones, enrutado dinámico a subagentes, selección de proveedor LLM gratuito, estado vía Engram | Selección de proveedor por tarea |
| **Radarito** | Subagente A — curación de noticias | Feeds RSS/APIs en 3 canales (`THT_SOLDERING`, `SMD_INSPECTION`, `AI_SOFTWARE`), dedupe, síntesis neutral 2-3 líneas | Cloudflare Workers AI / OpenRouter Free |
| **Cerebrito** | Subagente B — motor RAG | Respuestas técnicas solo sobre el corpus indexado en SQLite-vec, `grounding_score >= 0.85`, citas de fuentes | Google AI Studio (`gemini-flash`) |
| **Centinela** | Subagente C — guardrail | Intercepción perimetral `< 150 ms`, bloqueo de jailbreak/inyecciones, reconducción de off-topic | Groq (`llama-3.1-8b-instant`) |
| **Mensajerito** | Subagente D — triage de leads | Extrae oportunidades del chat/formulario, alerta cifrada a correo personal sin exponerlo | Groq (`llama-3.1-8b-instant`) |
| **Auditor** | Compuerta binaria transversal | QA Pass/Fail sobre TODAS las salidas: esquemas Pydantic, grounding, fuga de PII/credenciales/marcas | Google AI Studio (instrucciones estrictas) |

**Contratos de datos** — 5 modelos Pydantic v2 (`backend/app/models.py`),
firmas congeladas: `NewsItemPayload`, `RAGResponsePayload`, `GuardrailVerdict`,
`LeadAlertPayload`, `AuditVerdict`. Cualquier payload nuevo pasa por los tests.

**Routing de modelos LLM (costo cero)** — `backend/app/core/llm_routing.py`,
integrado con el plugin `gentle-ai.model-variants` ya registrado en `cli.json`.
Cada subagente tiene un modelo primario y un fallback zero-cost:

| Agente | Proveedor | Modelo primario | Fallback | Temperatura |
|---|---|---|---|---|
| Nexus | dynamic (intent-based) | intent-based | intent-based | 0.0 |
| Radarito | Cloudflare Workers AI | qwen-2.5-7b | deepseek-chat | 0.2 |
| Cerebrito | Google AI Studio | gemini-1.5-flash | gemini-2.0-flash | 0.1 |
| Centinela | Groq | llama-3.1-8b-instant | llama-3.1-70b-instant | 0.0 |
| Mensajerito | Groq | llama-3.1-8b-instant | llama-3.1-70b-instant | 0.1 |
| Auditor | Google AI Studio | gemini-1.5-flash | gemini-2.0-flash | 0.0 |

**Adaptadores MCP** (`backend/app/mcp/adapters.py`): Context7, Engram,
`mcp-server-news` (Radarito), `mcp-server-knowledge` (Cerebrito),
`mcp-server-security` (Centinela), `mcp-server-notifier` (Mensajerito).

## Layout objetivo

Estructura modular desacoplada (fuente: prompt maestro, sección 6):

```
├── web/                     # Frontend Astro 4 + Tailwind (SSG + Islands)
│   ├── src/
│   │   ├── components/      # UI Islands (Chat, Feeds, ContactForm)
│   │   ├── layouts/
│   │   ├── pages/           # index / industrial-smt / software-engineering
│   │   └── styles/
├── backend/                 # Runtime multiagente FastAPI
│   ├── app/
│   │   ├── agents/          # Nexus, Radarito, Cerebrito, Centinela, Mensajerito, Auditor
│   │   ├── core/            # Configuración, state FSM, seguridad
│   │   ├── db/              # SQLite, SQLite-vec y migraciones
│   │   ├── mcp/             # Servidores y adaptadores MCP
│   │   ├── models/          # 5 contratos Pydantic v2
│   │   └── routers/         # /chat /news /contact /health + WebSockets
│   └── tests/               # Suite TDD (unit, contracts, mocks, integration)
├── data/                    # Corpus técnico sanitizado y datasets de prueba
├── docs/                    # Especificaciones fuente del producto
└── odd/                     # Feature docs ODD (plan, no código)
```

## Comandos esenciales

```powershell
# Arrancar el backend (SIEMPRE desde la raíz del proyecto, nunca python backend/main.py)
python -m backend.main

# Build del frontend (Astro)
cd web && npx astro build

# Tests de contratos (TDD)
python -m pytest backend/tests/ -v
```

El backend queda en `http://localhost:8000`; páginas servidas por FastAPI.

## Convenciones obligatorias

1. **Consola Windows cp1252**: los `print()` del backend usan solo ASCII
   (nada de emojis ni acentos en logs, o `UnicodeEncodeError`).
2. **Pydantic v2 estricto**: contratos congelados; cualquier payload nuevo pasa
   los tests de `backend/tests/`.
3. **TDD (Red → Green → Refactor)**: prohibido implementar sin test previo.
   Mocks deterministas de LLM para corridas offline y deterministas.
4. **Arranque**: `python -m backend.main` desde la raíz; paths absolutos
   basados en `__file__` para recursos estáticos.
5. **Datos sanitizados**: contenido placeholder y case studies anonimizados;
   sin PII, credenciales ni marcas reales (el Auditor bloquea fuga de datos).
6. **Alcance del Spoke Industrial**: sin maquinaria Pick & Place (límite
   explícito de la spec).
7. **v1 sin APIs vivas expuestas**: zero-cost routing, corpus local.
8. **SDD en `odd/`**: todo trabajo significativo se planifica en formato ODD
   (Specs/Tasks/Log) y se verifica contra sus `S#`. Los agentes delegados
   reportan qué specs cubrieron.

## Entorno y gotchas (nivel OS/herramienta)

- Windows: consola cp1252; logs del backend solo ASCII.
- Python activo es un venv de `hermes-agent`: siempre `python -m pip`.
- En este entorno Astro falla compilando `.astro` (esbuild parse error). En
  v1 las páginas viven como **HTML plano** en `web/public/pages/` servidas por
  FastAPI en `/static/pages/`; si se reintenta Astro, se trata como problema de
  entorno y exige un repro reproducible documentado antes de decidir.
- El código usa `BASE_DIR = Path(__file__).resolve().parent.parent`; los paths
  relativos al cwd fallan (se sirve desde `web/public/` vía `app.mount`).
- CodeGraph indexado en la raíz del repo (`.codegraph/`); para consultas
  estructurales usar `codegraph_explore` antes de grep/read loops.

## Roadmap desde cero (fases bajo Gentle-AI)

1. **F1 — Contratos**: tests Pydantic v2 Red primero, luego los 5 modelos.
2. **F2 — Agentes con mocks**: Nexus FSM + 4 subagentes + Auditor contra
   fixtures deterministas (suite offline en verde).
3. **F3 — API**: routers `/chat` `/news` `/contact` `/health` + WebSockets
   `/ws/{agent_name}`, integrados en `main.py`.
4. **F4 — Frontend**: Hub & Spoke (HTML/Islands), feeds dinámicos, drawer RAG.
5. **F5 — RAG**: corpus sanitizado + indexado SQLite-vec + batería de grounding.
6. **F6 — Resiliencia**: 50+ vectores anti-inyección para Centinela; tests de
   veredicto del Auditor (grounding < 0.85 → REJECTED, detección de PII).
7. **F7 — Deploy**: Cloudflare Pages + backend, CI con la suite offline.

Las fases se planifican como feature docs en `odd/`, una por unidad de
entrega, y se marcan contra sus `S#` — nunca "completada" sin evidencia de
tests observados.
