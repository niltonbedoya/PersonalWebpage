# Arquitectura de la Plataforma Showcase — Living Technical Portfolio

## Visión General
La plataforma es un portfolio técnico híbrido diseñado bajo la metodología Gentle-AI (Organic Driven Development + TDD estricto), desplegado sobre una arquitectura multiagente en FastAPI y un frontend desacoplado (Astro/HTML).

## Arquitectura Multiagente del Runtime
El backend implementa un sistema coordinado de seis agentes especializados:
1. **Nexus (Orquestador Central & Router)**:
   - Máquina de estados finitos (FSM) asíncrona.
   - Enrutado de peticiones basado en intención (intent-based routing).
   - Gestión del ciclo de vida de sesiones.
2. **Centinela (Guardrail Perimetral)**:
   - Intercepción de baja latencia (<150 ms) en el perímetro de entrada.
   - Detección y bloqueo de prompt injections, jailbreaks y preguntas fuera de dominio (off-topic).
3. **Cerebrito (Motor RAG Técnico)**:
   - Búsqueda vectorial local sobre SQLite-vec.
   - Generación de respuestas fundamentadas exclusivamente en el corpus indexado.
   - Cálculo determinístico de grounding_score (umbral estricto >= 0.85) y citación de fuentes reales.
4. **Radarito (Curación de Noticias Técnicas)**:
   - Feeds contextuales categorizados en SMT_INSPECTION, THT_SOLDERING y AI_SOFTWARE.
   - Ingesta, deduplicación y síntesis neutral de noticias técnicas.
5. **Mensajerito (Triage y Notificación de Leads)**:
   - Evaluación y clasificación de oportunidades profesionales desde formularios y chat.
   - Alerta cifrada al correo personal sin exponer credenciales ni PII.
6. **Auditor (Compuerta Binaria de Calidad & Seguridad)**:
   - Evaluación transversal Pass/Fail (APPROVED / REJECTED) sobre todas las salidas del sistema.
   - Verificación estricta de esquemas Pydantic v2, grounding score y bloqueo de fuga de credenciales, PII o marcas privadas.

## Estrategia de Inferencia de Costo Cero (Zero-Cost Matrix)
- Google AI Studio (gemini-1.5-flash / gemini-2.0-flash).
- Groq Cloud (llama-3.1-8b-instant / llama-3.1-70b-instant).
- Cloudflare Workers AI / OpenRouter Free Tier (qwen-2.5-7b, deepseek-chat).
- Fallback automático sin degradación a proveedores de pago.

## Frontend Hub & Spoke
- **Dashboard Principal**: Hub central con retrato interactivo, métricas en tiempo real y feed dinámico de noticias.
- **Spoke Electrónica — SMT/THT**: Inspección 3D (SPI, AOI, AXI), procesos térmicos, soldadura y metrología Nordson BT.
- **Spoke Desarrollo de Software (AI)**: 5 casos de estudio industriales desacoplados, diseño defensivo y arquitectura limpia.
- **Internacionalización Dinámica**: Motor client-side con autodetección de idioma del navegador (Español para navegadores hispanos, Inglés para cualquier otro idioma) y persistencia en localStorage.
- **Drawer RAG Modal**: Interfaz de chat interactiva para consultar a Cerebrito sobre cualquier aspecto técnico del perfil y proyectos.
