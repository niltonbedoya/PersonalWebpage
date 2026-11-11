# DOCUMENTO DE ESPECIFICACIÓN Y ARQUITECTURA TÉCNICA DEL PROYECTO

**Metodología:** Spec-Driven Development (SDD) & Test-Driven Development (TDD)
**Proyecto:** Plataforma Showcase de Ingeniería Híbrida & Runtime Multiagente
**Estado:** Consolidado y Aprobado

---

## 1. VISIÓN DEL PRODUCTO Y DOMINIO (FASE 1)

### 1.1. Propósito y Posicionamiento

El proyecto no es una web comercial convencional ni un portafolio estático de capturas, sino un **Living Technical Portfolio (Showcase Platform)** diseñado para certificar autoridad técnica y solvencia de ingeniería a largo plazo ante colegas, reclutadores de alto nivel y oportunidades de colaboración técnica u orgánica.

El perfil proyectado es híbrido y de alta especialización:
* **Ingeniería de Hardware, Sistemas Industriales y Calidad SMT/THT.**
* **Arquitectura de Software Industrial, Sistemas Distribuidos y Soluciones Full-Stack.**

### 1.2. Principio Rector: "Show, Don't Tell" & Divulgación Progresiva

Para evitar sobrecarga cognitiva entre audiencias industriales y de software, se adopta el patrón de diseño **Hub & Spoke**:

```
                       ┌─────────────────────────────────────┐
                       │     Nivel 0: Hub Central (Landing)  │
                       │    (Bio, Visión Dual, Métricas)     │
                       └──────────────────┬──────────────────┘
                                          │
      ┌─────────────────────────────┴─────────────────────────────┐
      │                                                           │
      ▼                                                           ▼
┌──────────────────────────────────────┐    ┌──────────────────────────────────────┐
│  Spoke 1: Vertical Industrial SMT    │    │  Spoke 2: Software & Soluciones IA   │
│  (/industrial-smt)                   │    │  (/software-engineering)             │
│  • Maquinaria de Inspección 3D/RayosX│    │  • 5 Casos de Estudio Reales         │
│  • Procesos Térmicos y Soldadura     │    │  • Arquitecturas y Demostraciones    │
│  • Feed de Noticias SMT/THT          │    │  • Feed de Noticias IA/Software      │
└──────────────────────────────────────┘    └──────────────────────────────────────┘
      ▲                                                           ▲
      │                                                           │
      └─────────────────────────────┬─────────────────────────────┘
                                      │
                       ┌──────────────────┴──────────────────┐
                       │    Capa Transversal de Interacción  │
                       │  • Asistente RAG & Guardrails       │
                       │  • Formulario Seguro / Contacto     │
                       └─────────────────────────────────────┘
```

---

## 2. DETALLE DE CONTENIDOS Y ALCANCE FUNCIONAL

### 2.1. Spoke Industrial: Taxonomía de Maquinaria y Procesos

* **Sistemas de Inspección Óptica & Dimensional:**
  * **Parmi:** 3D SPI (inspección de pasta), 3D AOI (inspección de componentes/soldadura), PCI (inspección de barnizado conformal).
  * **Marantz:** Inspección 2D pre-reflow y post-reflow (componentes SMD y THT).
  * **Ersa:** *VERSAEYE* (inspección óptica de soldadura).
  * **ALeader:** Equipos 2D fundacionales (mención histórica contenida).
* **Inspección Avanzada No Destructiva:**
  * **Matrix:** Inspección por Rayos X en línea (AXI) para soldaduras ocultas (BGA, QFN, voiding).
* **Sistemas de Impresión & Serigrafía:**
  * **MPM (ITW EAE):** Impresoras de alta precisión (*AccuFlex*, *Momentum*), alineación por visión y control reológico.
* **Procesos Térmicos y Soldadura:**
  * **Ersa:** Soldadura selectiva (mini-wave / multi-dip), soldadura por ola (Wave Soldering) y hornos de refusión por convección.
  * **Electrovert (ITW EAE):** Soldadura por ola (serie *Vectra*) y hornos de refusión.
* **Metalurgia y Materiales:**
  * Pasta de soldar (reología, fluxes no-clean/solubles, granulometría tipo 3/4/5).
  * Soldadura en lingote para crisoles de ola y selectiva (SAC305, SN100C, SnPb), control de escoria (*dross*) y atmósfera inerte ($N_2$).
  * Perfilado térmico de hornos de refusión (Ramp-to-Soak, Time Above Liquidus - TAL, enfriamiento controlado).
* **Handling & Automatización:**
  * Cargadores, descargadores, buffers, cintas transportadoras, diagnóstico y programación de PLCs.
* **Límite de Alcance (Scope Boundary):** Exclusión explícita de máquinas de inserción Pick & Place.

### 2.2. Spoke Software: Catálogo de Casos de Estudio (Anonimizados by Design)

Todos los proyectos se presentan como *Case Studies* técnicos estructurados (Problema $\to$ Reto de Ingeniería $\to$ Solución Arquitectónica $\to$ Stack $\to$ Vídeo/Media Demostrativo). **Cero APIs en vivo expuestas en v1** para eliminar costes y riesgos de seguridad.

1. **Sistema de Tickets de Servicio (Base AB):** Ticketing técnico, seguimiento de incidencias, trazabilidad y SLAs sobre datos 100% sintéticos e interfaces sanitizadas.
2. **ERP de Gestión Comercial & Financiera (Base Kronenblumen):** Facturación, créditos, cuentas por cobrar/pagar, control de inventario y ventas con entidades ficticias.
3. **Control Logístico & Packing List (Corea):** Conteo y trazabilidad de entrada/salida de ruedas, asignación de contenedores y generación de Packing List de exportación (PDF/Excel).
4. **Motor de Traducción & Transcripción Simultánea:** Pipeline de baja latencia para eventos técnicos. Demostración en vídeo con audio pregrabado sincronizado y métricas de latencia.
5. **Plataforma de Salud & Wearable Sync:** Ingesta de métricas IoT (ritmo cardíaco, hidratación), OCR de informes médicos y visión computacional sobre fotografías de menús.

### 2.3. Módulos Dinámicos y de Captación

* **Ventanas de Noticias Contextuales:** 3 feeds independientes actualizados automáticamente:
  1. `THT_SOLDERING`: Novedades sobre Ersa, Electrovert, aleaciones y normativas IPC.
  2. `SMD_INSPECTION`: Innovaciones en Parmi, Marantz, Matrix, Rayos X y AOI/SPI 3D.
  3. `AI_SOFTWARE`: Arquitecturas de software, LLMs, sistemas multiagente e IoT.
* **Asistente Conversacional RAG:** Chatbot interactivo indexado sobre tu trayectoria real con guardrails contra desvíos de tema y prompt injection.
* **Lead Triage & Notificación Silenciosa:** Detección de propuestas serias y datos de contacto, despachando alertas cifradas a tu email personal sin exponerlo.
* **Formulario y Salidas:** Formulario de contacto con honeypot, links a GitHub y LinkedIn, y descarga de CV en PDF.

---

## 3. ARQUITECTURA MULTIAGENTE DUAL Y RUNTIME (FASE 2)

### 3.1. Dualidad Arquitectónica

* **Nivel Build-Time (JenteL AI):** Meta-orquestación para desarrollo de código. JenteL AI selecciona modelos según la tarea de programación y ejecuta el *Binary Auditor* para verificar compilación, tests y buenas prácticas antes de confirmar cambios.
* **Nivel Runtime (Producción):** Núcleo embebido en FastAPI que gestiona las funciones autónomas de la web desplegada.

### 3.2. Tabla Maestra de Agentes en Runtime

| Agente Oficial | Rol Arquitectónico | Responsabilidad | Entrada | Salida | Control / Auditoría |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Nexus** | Orquestador Central & Router | FSM, enrutamiento dinámico a modelos gratuitos, balanceo de carga y gestión de estado. | Eventos web, cron triggers o peticiones de chat. | Despacho tipado a subagentes; respuesta consolidada. | Trazabilidad y logs auditados por **Auditor**. |
| **Radarito** | Subagente A (Curación Feeds) | Ingesta RSS/scraping de noticias THT, SMD e IA; eliminación de duplicados y resumen de 2-3 líneas. | Feeds RSS / XML / HTML de fuentes técnicas. | `NewsItemPayload` validado. | **Auditor** verifica esquema Pydantic, URLs vivas y fidelidad. |
| **Cerebrito** | Subagente B (Motor RAG) | Respuestas técnicas fundamentadas en corpus indexado (maquinaria, procesos y software). | Query de usuario + chunks vectoriales relevantes. | `RAGResponsePayload` con citas de fuentes. | **Auditor** exige Grounding Score $\ge 0.85$; cero alucinación. |
| **Centinela** | Subagente C (Guardrail & Filtro) | Intercepción perimetral (<150 ms), bloqueo de inyecciones y redirección educada de off-topic. | Prompt crudo del visitante. | `GuardrailVerdict` (`is_allowed`, riesgo, redirección). | **Auditor** comprueba que ninguna petición inválida penetre. |
| **Mensajerito** | Subagente D (Triage & Despacho) | Detección asíncrona de oportunidades y datos de contacto; envío de alerta cifrada por email. | Historial conversacional o payload del formulario. | `LeadAlertPayload` estructurado. | **Auditor** valida integridad y verifica cero fuga de email propio. |
| **Auditor** | Agente Auditor / QA | Compuerta de calidad binaria (Pass/Fail) sobre contratos JSON, fidelidad y prevención de fuga de datos. | Salidas generadas por los subagentes. | `AuditVerdict` (`APPROVED` o `REJECTED`). | Auto-verificación de schemas, umbrales y regex de seguridad. |

---

## 4. STACK TÉCNICO, MCPS Y ESTRATEGIA DE COSTES (FASE 3)

### 4.1. Matriz de Tecnologías

| Capa | Selección Técnica | Justificación Arquitectónica |
| :--- | :--- | :--- |
| **Frontend Framework** | **Astro 4+** + Tailwind CSS + Lucide | Arquitectura de Islas (*Islands*). SSG puro para contenido estático (Hub/Spokes) y mínima hidratación JS solo en widgets interactivos. Rendimiento Lighthouse cercano a 100. |
| **Hosting & Edge CDN** | **Cloudflare Pages** | Dominio administrado directamente en Cloudflare. Despliegue edge global con SSL automático, caché distribuida y coste cero de ancho de banda. |
| **Backend Runtime** | **Python 3.12+** (FastAPI + Pydantic v2) | Alta velocidad asíncrona, validación estricta de esquemas en submilisegundos y compatibilidad nativa con librerías de IA. |
| **Vector Store & Embeddings** | **SQLite-vec** | Búsqueda vectorial embebida en base de datos local SQLite. Sin microservicios pesados adicionales ni costes en la nube. |
| **Memoria Persistente de Agentes**| **Engram MCP** | Sistema de memoria relacional en SQLite que mantiene sincronizados a los agentes sin penalizar latencia ni incurrir en costes de bases de datos externas. |
| **Contexto & Documentación** | **Context7 MCP** | Suministro estructurado de documentación técnica y directrices de proyectos a la orquestación. |

### 4.2. Estrategia de Modelos LLM Gratuitos (Zero-Cost Routing)

* **Centinela & Mensajerito:** **Groq Cloud** (`llama-3.1-8b-instant`). Velocidad de procesamiento extrema en inferencia LPU (<150 ms) para guardrails y extracción de leads.
* **Cerebrito & Auditor:** **Google AI Studio** (`gemini-1.5-flash` / `gemini-2.0-flash`). Extensa ventana de contexto, gran precisión analítica y estricto seguimiento de instrucciones para grounding y auditoría.
* **Radarito:** **Cloudflare Workers AI** / **OpenRouter Free Tier** (`qwen-2.5-7b` o `deepseek-chat`). Generación estructurada de JSON y síntesis neutral de noticias en tareas programadas.

### 4.3. Servidores MCP de Dominio

* `mcp-server-news` (Radarito): Herramientas para parseo RSS, scraping sanitizado y persistencia de noticias.
* `mcp-server-knowledge` (Cerebrito): Herramientas de consulta sobre `SQLite-vec` para especificaciones de máquinas y casos de estudio.
* `mcp-server-security` (Centinela): Reglas heurísticas, firewall de inyecciones y clasificación de intenciones.
* `mcp-server-notifier` (Mensajerito): Disparador transaccional seguro de correo hacia tu dirección privada.

---

## 5. ESTRATEGIA TDD (TEST-DRIVEN DEVELOPMENT)

El ciclo de desarrollo sigue el mandato estricto **Red $\to$ Green $\to$ Refactor**:

1. **Tests de Contratos de Agentes:** Comprobación unitaria de serialización/deserialización de modelos Pydantic v2.
2. **Fixtures Deterministas de LLM:** Simulación local de llamadas a Groq, Google AI Studio y Cloudflare para tests rápidos y sin conexión a internet.
3. **Batería de Resiliencia de Seguridad:** Pruebas contra 50+ ataques de prompt injection y desvíos de contexto evaluando la respuesta de Centinela.
4. **Tests de Veredicto del Auditor:** Verificación de rechazo binario inmediato ante respuestas con Grounding Score < 0.85 o presencia de variables de entorno/datos privados.
5. **Testing Frontend:** Pruebas unitarias de componentes con `Vitest` y pruebas de navegación e integración E2E con `Playwright`.
