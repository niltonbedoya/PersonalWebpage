# Showcase Platform — Living Technical Portfolio

Portfolio técnico híbrido en vivo para un perfil de doble especialización:
**Ingeniería SMT/THT (Inspección Óptica 3D, Rayos X, Soldadura, Handling)** y
**Arquitectura de Software Industrial & Soluciones IA**.

Características clave:

- **Hub & Spoke**: Hub Central (`/`) + Spoke Industrial (`/static/pages/industrial-smt.html`) + Spoke Software (`/static/pages/software-engineering.html`).
- **Runtime multiagente** FastAPI con 6 agentes autónomos y **routing LLM de costo cero** (Groq / Google AI Studio / Cloudflare / OpenRouter free tier).
- **WebSockets en tiempo real** por agente (`/ws/{agent_name}`).
- Documentos fuente de especificación en `docs/`.

> Estado actual: datos de ejemplo (placeholders). Falta reemplazarlos por datos reales: fotos, casos de estudio sanitizados, LinkedIn, GitHub y CV en PDF.

## Arranque rápido

```powershell
cd D:\PersonalAIFolder\PersonalWabePage
python -m backend.main
```

- Backend: http://localhost:8000
- Hub: http://localhost:8000/static/pages/index.html
- Spoke Industrial: http://localhost:8000/static/pages/industrial-smt.html
- Spoke Software: http://localhost:8000/static/pages/software-engineering.html
- Swagger: http://localhost:8000/api/docs

> Nota Windows: la consola es cp1252 — los logs del servidor usan ASCII solamente.

## Estructura

```
backend/
  main.py                 # Entrada FastAPI: mount estático + routers + WebSockets
  websockets.py           # ConnectionManager y handlers por agente
  agent_ops_router.py     # /api/v1/agents/* (pendiente de integrar en main.py)
  app/
    models.py             # 5 contratos Pydantic v2 (NewsItem, RAGResponse, Guardrail, LeadAlert, Audit)
    agents/__init__.py    # Nexus, Radarito, Cerebrito, Centinela, Mensajerito, Auditor
    mcp/adapters.py       # 6 adaptadores MCP (Context7, Engram, news, knowledge, security, notifier)
    routers/__init__.py   # /chat /news /contact /health
web/
  public/pages/           # HTML servidos en /static/pages/ (HTML plano; Astro falló con esbuild)
  dist/pages/             # Salida de `npx astro build`
docs/                     # Especificaciones fuente (SDD/TDD)
odd/                      # Planes de trabajo de la sesión (feature docs)
data/                     # Corpus técnico y datasets de prueba
```

## Matriz de agentes (runtime)

| Agente       | Rol                              | Modelo (costo cero)                          |
|--------------|----------------------------------|----------------------------------------------|
| Nexus        | Orquestador central & router     | FSM + selección de proveedor gratuito        |
| Radarito     | Curación de noticias (3 canales) | Cloudflare Workers AI / OpenRouter Free      |
| Cerebrito    | Motor RAG técnico (SQLite-vec)   | Google AI Studio (`gemini-1.5-flash`)        |
| Centinela    | Guardrail & seguridad (<150 ms)  | Groq (`llama-3.1-8b-instant`)                |
| Mensajerito  | Triage & despacho de leads       | Groq (`llama-3.1-8b-instant`)                |
| Auditor      | QA binaria Pass/Fail             | Google AI Studio (grounding ≥ 0.85)          |

## Endpoints principales

- `GET  /health` — estado global + agentes activos
- `POST /chat` — chat orquestado por Nexus
- `GET  /news` — feed curado por Radarito
- `POST /contact` — formulario seguro (honeypot + antispam)
- `WS   /ws/{agent_name}` — canal en tiempo real por agente
- `/api/v1/agents/*` — operaciones avanzadas por agente (integración pendiente)

## Stack

Astro 4 + Tailwind (frontend SSG) · Python 3.12 + FastAPI + Pydantic v2 (backend) ·
SQLite + SQLite-vec (RAG local) · Engram MCP (memoria de agentes) · Context7 MCP (docs dinámica)

## Referencias

- `docs/prompt_maestro_de_inicio.md` — specs SDD/TDD y topología multiagente
- `docs/especificaci_n_y_resumen_de_arquitectura.md` — visión del producto y fases
