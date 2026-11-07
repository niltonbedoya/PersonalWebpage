# AGENTS.md — Guía para agentes de código que trabajen en este repositorio

Contexto mínimo para iniciar a work on this project without re-exploring everything.

## Qué es este proyecto

**Showcase Platform — Living Technical Portfolio**: portfolio web híbrido
(SMT/THT industrial + Software/IA) con backend FastAPI multiagente y frontend Astro.
La fuente de verdad funcional es `docs/prompt_maestro_de_inicio.md` y
`docs/especificaci_n_y_resumen_de_arquitectura.md` (SDD/TDD).

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

## Layout

- `backend/main.py` — entrada FastAPI (mount estático + routers + WebSockets)
- `backend/app/models.py` — 5 contratos Pydantic v2. **No romper sus firmas.**
- `backend/app/agents/__init__.py` — framework de 6 agentes (Nexus, Radarito, Cerebrito, Centinela, Mensajerito, Auditor)
- `backend/app/mcp/adapters.py` — 6 adaptadores MCP
- `backend/app/routers/__init__.py` — `/chat` `/news` `/contact` `/health`
- `backend/websockets.py` — manager de conexiones y handlers `/ws/{agent_name}`
- `backend/agent_ops_router.py` — `/api/v1/agents/*` (pendiente de incluir en main.py)
- `web/public/pages/` — páginas HTML (servidas por FastAPI como `/static/pages/`)
- `docs/` — especificaciones fuente; `odd/` — planes de trabajo de sesión

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

## Gotchas conocidos

- Se sirven las páginas desde `web/public/` vía `app.mount("/static", ...)` con
  `BASE_DIR = Path(__file__).resolve().parent.parent` (paths relativos fallan).
- Astro falla compilando `.astro` en este entorno (esbuild "Expected \";\" but
  found..."); las páginas viven como HTML plano en `web/public/pages/`.
- El 404 repetido de `GET /v1/models` en logs viene de un cliente externo de la
  máquina (no del proyecto); es inofensivo.
- Si tocas `main.py`, evitar literales basura al final (`PYEOF`) y verificar con
  `python -c "import py_compile; py_compile.compile('backend/main.py', doraise=True)"`.

## Pendiente (roadmap corto)

1. Integrar `agent_ops_router` en `main.py`.
2. Probar `/chat`, `/news`, `/contact` y WebSocket con datos reales de request.
3. Reemplazar datos de ejemplo por reales (fotos, casos, LinkedIn/GitHub/CV PDF).
