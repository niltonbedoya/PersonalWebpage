# Feature Document: F4 — Frontend Hub & Spoke

**Objective:** Build the frontend (Hub & Spoke pattern) connected to the real
backend APIs implemented in F3. HTML pages served by FastAPI at
`/static/pages/` (Astro build fails in this environment — documented in
AGENTS.md). Offline, deterministic, no network dependency for the frontend
itself; it consumes `/chat`, `/news`, `/contact`, `/health` endpoints.
**Branch:** main. **Test runner:** structural/functional checks + Playwright
E2E if available.

## Specs

S1. "Nivel 0 - Hub Central (/): Hero técnico, mini-bio, Split Cards hacia los
dos spokes, métricas de ingeniería." (prompt maestro §2.1)
S2. "Spoke 1 - Vertical Industrial & SMT/THT (/industrial-smt): maquinaria de
inspección, sistemas térmicos, serigrafía, handling, metalurgia, feed de
noticias SMT/THT. Límite: exclusión de Pick & Place." (§2.1)
S3. "Spoke 2 - Vertical Software & Soluciones IA (/software-engineering): 5
casos de estudio, feed de noticias IA/Software." (§2.1)
S4. "Capa Transversal: Drawer/Modal con asistente conversacional RAG,
formulario de contacto seguro con honeypot, enlaces LinkedIn/GitHub/CV PDF."
(§2.1)
S5. Feeds contextuales dinámicos consumiendo `GET /news` por categoría
(`THT_SOLDERING`, `SMD_INSPECTION`, `AI_SOFTWARE`). (§2.3)
S6. Formulario de contacto enviando a `POST /contact` con honeypot y
protección antispam. (§2.1, §2.3)
S7. Drawer RAG enviando a `POST /chat` y mostrando respuesta del agente.
(§2.1, §3.1)
S8. Todos los archivos HTML/CSS/JS: ASCII-only, sin emojis ni acentos en
código (Windows cp1252 console rule); navegación Hub↔Spoke funcional;
contenido sanitizado (sin PII, sin marcas reales).

## Tasks

T1. Create feature doc + shared layout/CSS/JS module (this document + shared
files). Delegated worker (gentle-ai-worker).
T2. Hub Central (index.html): hero, split cards to both spokes, navigation,
engineering metrics. Delegated worker.
T3. Spoke Industrial (industrial-smt.html): machinery cards, scope boundary
alert, SMT/THT news feed connected to /news. Delegated worker.
T4. Spoke Software (software-engineering.html): 5 case studies, AI/Software
news feed connected to /news. Delegated worker.
T5. Drawer RAG modal: open/close, send query to /chat, display response,
loading state. Delegated worker.
T6. Contact form: POST /contact, honeypot handling, success/error states.
Delegated worker.
T7. Navigation wiring: all pages link to each other, active state, drawer
accessible from every page. Delegated worker.
T8. Functional checks: structural HTML validation, links resolve, feeds render
news from API mock, contact submits and shows result. Delegated worker.

## Allowed edit surfaces (per task — passed to workers)
T1: web/src/styles/shared.css (new), web/src/js/shared.js (new),
    web/src/components/shared-header.html (new snippet)
T2: web/public/pages/index.html
T3: web/public/pages/industrial-smt.html
T4: web/public/pages/software-engineering.html
T5: web/src/components/drawer-rag.html (new snippet), web/src/js/drawer-rag.js (new)
T6: web/src/components/contact-form.html (new snippet), web/src/js/contact-form.js (new)
T7: all three HTML pages (navigation links)
T8: backend/tests/test_frontend_functional.py (new) — FastAPI TestClient
    structural checks + Playwright if available

## Log

L1. 2026-11-07: Feature doc created. F3 complete (183 tests green). Frontend
currently: 3 plain HTML pages with no navigation between them, no feeds, no
drawer RAG, no contact form connected. web/src/pages/index.astro exists but
Astro build fails in this environment (documented). Pages served by FastAPI at
/static/pages/.
