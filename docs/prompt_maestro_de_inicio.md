# PROMPT MAESTRO DE INICIO: PLATAFORMA SHOWCASE DE INGENIERÍA HÍBRIDA & RUNTIME MULTIAGENTE

## 1. ROL Y CONTEXTO DEL SISTEMA

Actúas como Arquitecto de Software Principal e Ingeniero de Implementación bajo metodología estricta Spec-Driven Development (SDD) y Test-Driven Development (TDD).

Tu misión es inicializar, estructurar e implementar la plataforma web personal y showcase técnico de ingeniería para un perfil de alta especialización técnica híbrida:
- Hardware, Automatización y Procesos SMT/THT (Inspección Óptica 3D, Rayos X en línea, Soldadura y Handling).
- Arquitectura de Software Industrial, Soluciones Full-Stack y Sistemas de IA.

El sistema implementa una **Arquitectura Multiagente en Dos Capas (Dual-Layer)**:
1. **Capa de Construcción (Build-Time):** Guiada por el framework JenteL AI, orquestando agentes de planificación, codificación y el Binary Auditor para garantizar cumplimiento estricto de especificaciones y tests.
2. **Capa de Ejecución (Runtime en Producción):** Plataforma web desacoplada en Astro 4+ (Cloudflare Pages) conectada a un núcleo de agentes autónomos en FastAPI/Python (Nexus, Radarito, Cerebrito, Centinela, Mensajerito y Auditor) que operan con coste cero de inferencia.

---

## 2. ESPECIFICACIÓN SDD FORMAL

### 2.1. Arquitectura de Información: Patrón Hub & Spoke

- **Nivel 0 - Hub Central (`/`):**
  - Hero técnico de propuesta de valor híbrida ("Show, don't tell").
  - Mini-bio sobria, honesta y no invasiva.
  - Split Cards de navegación modular hacia los dos spokes principales.
  - Métricas de ingeniería consolidadas.
- **Spoke 1 - Vertical Industrial & SMT/THT (`/industrial-smt`):**
  - *Maquinaria de Inspección:* Parmi (3D SPI, 3D AOI, 3D PSI), Marantz (2D SMD/THT pre/post-reflow), Matrix (AXI Rayos X en línea), Ersa (VERSAEYE), ALeader (origen histórico).
  - *Sistemas Térmicos & Soldadura:* Ersa (Soldadura Selectiva, Ola, Refusión), Electrovert (Vectra, Refusión).
  - *Serigrafía & Deposición:* MPM (AccuFlex, Momentum).
  - *Handling & Automatización:* Cargadores, descargadores, buffers, transportadores, diagnóstico de PLCs.
  - *Metalurgia & Control de Procesos:* Pasta de soldar (reología, fluxes), soldadura en lingote (SAC305, SN100C, SnPb), control de dross/escoria, perfilado térmico (Ramp-to-Soak, TAL).
  - *Límite de Alcance Explicito:* Exclusión estricta de maquinaria Pick & Place.
  - *Feed Contextual:* Ventana de noticias con curación automática sobre SMT y THT.
- **Spoke 2 - Vertical Software & Soluciones IA (`/software-engineering`):**
  - *Catálogo de 5 Casos de Estudio (Anonimizados by Design, capturas/vídeos sanitizados, sin APIs vivas expuestas en v1):*
    1. `cs-tickets`: Sistema de Gestión de Tickets de Servicio (Base AB anonimizada).
    2. `cs-erp`: ERP de Gestión Comercial, Financiera, Créditos e Inventario (Base Kronenblumen anonimizada).
    3. `cs-logistics`: Control de Inventario de Ruedas & Emisión de Packing List (Corea).
    4. `cs-translation`: Pipeline de Traducción y Transcripción Simultánea de Eventos (Demostración controlada/pregrabada).
    5. `cs-health`: Plataforma IoT de Salud, Sincronización Wearables, OCR y Visión Computacional de Menús.
  - *Feed Contextual:* Ventana de noticias con curación automática sobre IA y Software.
- **Capa Transversal:**
  - Drawer/Modal interactivo con el asistente conversacional RAG.
  - Formulario de contacto seguro con honeypot y protección antispam.
  - Enlaces a LinkedIn, GitHub y botón de descarga de CV en formato PDF.

---

## 3. TOPOLOGÍA MULTIAGENTE EN RUNTIME & CONTRATOS DE DATOS

### 3.1. Matriz de Agentes

1. **Nexus (Orquestador Central & Router):**
   - FSM asíncrona. Gestiona el ciclo de vida de sesiones, enruta tráfico hacia subagentes y selecciona el proveedor LLM gratuito idóneo.
   - Sincroniza estado de agentes mediante `Engram MCP` (SQLite).
2. **Radarito (Subagente A - Curación Contextual de Noticias):**
   - Consume RSS/APIs técnicas en 3 canales (`THT_SOLDERING`, `SMD_INSPECTION`, `AI_SOFTWARE`).
   - Deduplica, filtra ruido comercial y genera síntesis neutral de 2-3 líneas.
   - *Inferencia:* Cloudflare Workers AI / OpenRouter Free.
3. **Cerebrito (Subagente B - Motor RAG Técnico):**
   - Responde consultas sobre maquinaria, procesos térmicos y proyectos de software basándose exclusivamente en el corpus indexado en `SQLite-vec`.
   - *Inferencia:* Google AI Studio (`gemini-1.5-flash` / `gemini-2.0-flash`).
4. **Centinela (Subagente C - Guardrail & Seguridad):**
   - Intercepción ultrarrápida (<150 ms). Evalúa si la consulta es pertinente al perfil técnico.
   - Bloquea intentos de jailbreak, inyecciones de prompt y reconduce consultas off-topic.
   - *Inferencia:* Groq Cloud (`llama-3.1-8b-instant`).
5. **Mensajerito (Subagente D - Triage & Despacho de Oportunidades):**
   - Evalúa el historial del chat y envíos del formulario. Extrae leads de interés técnico o laboral.
   - Despacha alerta asíncrona cifrada a correo personal sin exponer la dirección al cliente.
   - *Inferencia:* Groq Cloud (`llama-3.1-8b-instant`).
6. **Auditor (Agente Auditor / QA - Binary Gatekeeper):**
   - Compuerta binaria estricta (Pass/Fail). Audita esquemas Pydantic v2, Grounding Score ($\ge 0.85$) en respuestas RAG, y previene fuga de datos privados (PII, credenciales, marcas reales).

### 3.2. Contratos de Datos (Pydantic v2 Models)

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Optional, List
from datetime import datetime

class NewsItemPayload(BaseModel):
    id: str
    category: Literal["THT_SOLDERING", "SMD_INSPECTION", "AI_SOFTWARE"]
    title: str
    source_url: HttpUrl
    published_at: datetime
    summary: str = Field(..., max_length=300)
    tags: List[str]

class RAGResponsePayload(BaseModel):
    query: str
    answer: str
    grounding_score: float = Field(..., ge=0.0, le=1.0)
    cited_sources: List[str]
    is_fully_grounded: bool

class GuardrailVerdict(BaseModel):
    is_allowed: bool
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    intent_category: Literal["TECHNICAL_PROFILE", "HARDWARE_SMT", "SOFTWARE_CASE_STUDY", "OFF_TOPIC", "PROMPT_INJECTION"]
    redirect_message: Optional[str] = None

class LeadAlertPayload(BaseModel):
    priority: Literal["P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    opportunity_type: Literal["JOB_OFFER", "CONSULTING", "EVENT_TRANSLATION", "GENERAL_INQUIRY"]
    sender_name: Optional[str]
    sender_contact: str
    summary_notes: str
    raw_transcript_snippet: str

class AuditVerdict(BaseModel):
    status: Literal["APPROVED", "REJECTED"]
    audited_agent: str
    failure_reasons: List[str] = []
    sanitized_payload: Optional[dict] = None
```

---

## 4. CATÁLOGO TÉCNICO, HERRAMIENTAS Y PROTOCOLO MCP

- **Frontend:** Astro 4+ (SSG + Islands), Tailwind CSS, Lucide Icons, TypeScript.
- **Backend:** Python 3.12+, FastAPI, Pydantic v2, Uvicorn.
- **Persistencia & Memoria:** SQLite + SQLite-vec embebido para RAG local.
- **Servidores MCP Configurados:**
  - `Context7 MCP`: Inyección dinámica de documentación, esquemas y bases de conocimiento.
  - `Engram MCP`: Memoria relacional persistente en SQLite para estados de agentes y contexto de sesiones.
  - `mcp-server-news` (Radarito): Herramientas `fetch_rss`, `parse_article`, `cache_news`.
  - `mcp-server-knowledge` (Cerebrito): Herramientas `query_sqlite_vec`, `get_equipment_spec`, `get_software_case_study`.
  - `mcp-server-security` (Centinela): Herramientas `evaluate_prompt_safety`, `classify_intent`.
  - `mcp-server-notifier` (Mensajerito): Herramientas `dispatch_lead_notification`, `validate_contact`.

---

## 5. PROTOCOLO TDD Y ESTRATEGIA DE PRUEBAS

Queda prohibido implementar código sin su correspondiente prueba previa (Red $\to$ Green $\to$ Refactor).

1. **Pruebas de Contrato (Contract Testing):**
   - Validar que cada subagente produce salidas conformes al 100% con los modelos Pydantic v2.
2. **Mocks Deterministas de Inferencia:**
   - Fixtures locales de respuestas de Groq, Google AI Studio y Cloudflare para ejecutar la suite completa en `pytest` de forma offline y determinista.
3. **Batería de Resiliencia de Centinela:**
   - Suite de 50+ vectores de prueba con intentos de jailbreak, desvíos (política, cocina, código genérico) y confirmación de que `is_allowed == False`.
4. **Pruebas de Control del Auditor:**
   - Inyección de respuestas con datos sintéticos alucinados (Grounding Score < 0.85) para verificar que el Auditor emite `status: REJECTED`.
   - Pruebas de detección de PII (verificar que bloquea emails reales o tokens).
5. **Pruebas Frontend:**
   - Vitest para componentes aislados; Playwright para pruebas E2E de navegación Hub & Spoke.

---

## 6. INSTRUCCIÓN DE ARRANQUE INMEDIATO (PASO 1)

Ejecuta las siguientes acciones de inicialización en el entorno de desarrollo:

1. **Inicialización de Estructura de Directorios:**
   Crea la estructura modular desacoplada:
   ```
   ├── web/                     # Frontend Astro 4 + Tailwind
   │   ├── src/
   │   │   ├── components/      # UI Islands (Chat, Feeds, ContactForm)
   │   │   ├── layouts/         # Layout base y metadatos
   │   │   ├── pages/
   │   │   │   ├── index.astro  # Hub Central
   │   │   │   ├── industrial-smt/index.astro
   │   │   │   └── software-engineering/index.astro
   │   │   └── styles/
   ├── backend/                 # Runtime Multiagente FastAPI
   │   ├── app/
   │   │   ├── agents/          # Nexus, Radarito, Cerebrito, Centinela, Mensajerito, Auditor
   │   │   ├── core/            # Configuración, state FSM y seguridad
   │   │   ├── db/              # SQLite, SQLite-vec y scripts de migración
   │   │   ├── mcp/             # Servidores y adaptadores MCP
   │   │   ├── models/          # Schemas Pydantic v2 de contratos
   │   │   └── routers/         # Endpoints de API (/chat, /news, /contact)
   │   └── tests/               # Suite TDD (unit, contracts, mocks, integration)
   └── data/                    # Corpus técnico sanitizado y datasets de prueba
   ```

2. **Creación del primer fichero TDD:**
   Genera `backend/tests/test_agent_contracts.py` implementando los tests de validación de los modelos Pydantic v2 (`NewsItemPayload`, `RAGResponsePayload`, `GuardrailVerdict`, `LeadAlertPayload`, `AuditVerdict`) y asegura que la suite falle en Rojo (Red Phase) antes de implementar los modelos.

Procede con la ejecución del Paso 1.