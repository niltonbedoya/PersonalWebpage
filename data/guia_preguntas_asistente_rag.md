# Guía de Consultas y Preguntas Sugeridas para el Asistente RAG

## Propósito de la Guía
Este documento sirve de índice temático y guía de orientación para los usuarios, reclutadores y colegas técnicos que interactúan con el asistente RAG (Cerebrito) del portfolio de Nilton Bedoya. El asistente está diseñado para responder exclusivamente con base en el corpus verificado, garantizando un grounding score superior a 0.85 y veredicto aprobado por el Auditor.

A continuación se detallan las consultas recomendadas organizadas por especialidad técnica.

---

## 1. Consultas sobre Ingeniería Electrónica SMT/THT

El perfil de hardware abarca procesos de ensamblaje, inspección avanzada, control térmico, metalurgia y manipulación automática de placas. (Nota de alcance: exclusión estricta de maquinaria Pick & Place).

Preguntas que puedes formular:
- **Inspección Óptica 3D y SPI**:
  - ¿Qué experiencia tiene Nilton Bedoya con sistemas Parmi (3D SPI, 3D AOI y PCI para inspección de barnizado)?
  - ¿Cómo se configuran los umbrales de inspección de pasta de soldar (altura, volumen y coplanaridad)?
  - ¿Cómo funciona la inspección óptica 2D en equipos Marantz para componentes SMD y THT?
- **Inspección por Rayos X (AXI) e Integridad de Uniones**:
  - ¿Cómo se realiza la inspección no destructiva de soldadura oculta en BGA y QFN con equipos Matrix AXI?
  - ¿Qué diagnósticos mecánicos y calibraciones de celda de carga se realizan en equipos Nordson BT (Bond Tester)?
- **Sistemas Térmicos y Soldadura**:
  - ¿Cómo se controla el perfil térmico y la formación de dross en hornos de soldadura por ola Ersa o Electrovert?
  - ¿Qué consideraciones metalúrgicas se aplican a la pasta de soldar SAC305 y la compatibilidad de fluxes?
- **Handling y Automatización**:
  - ¿Qué conocimientos tiene sobre cargadores, descargadores, buffers FIFO/LIFO y buses de control industrial?
  - ¿Cuál es el límite de alcance industrial en este portfolio?

---

## 2. Consultas sobre Proyectos de Software y Soluciones AI (GitHub)

Repositorios reales y arquitecturas de software desarrolladas por Nilton Bedoya:

Preguntas que puedes formular:
- **Tire Counter Monorepo (`niltonbedoya/tire-counter-monorepo`)**:
  - ¿Cuál es la arquitectura y el stack tecnológico del proyecto Tire Counter?
  - ¿Cómo funciona la máquina de estados finitos (FSM) de despacho y la bóveda de datos inmutable?
  - ¿Qué servidores Model Context Protocol (MCP) incluye el monorepo para auditoría y validación?
- **Servicio de Tickets (`niltonbedoya/servicio_tickets`)**:
  - ¿Cómo está implementada la arquitectura de monolito modular con FastAPI y React 18?
  - ¿Cómo funciona el modo offline-first con IndexedDB y sincronización de partes de trabajo y firmas?
- **CardioNutri (`niltonbedoya/cardionutri`)**:
  - ¿Qué características tiene la plataforma CardioNutri en React Native Expo y FastAPI?
  - ¿Cómo se gestiona la sincronización con Health Connect y sensores biométricos?
- **ERP Comercial y Control de Importaciones**:
  - ¿Cómo opera la solución de visión por computador AI para conteo y lectura de código?
  - ¿Qué stack utiliza para el ERP comercial y la sincronización con Supabase?
- **Traductor Simultáneo (`niltonbedoya/Traductor-Simultaneo`)**:
  - ¿Cómo funciona el pipeline de traducción y síntesis de voz en tiempo real con Azure Speech?
- **Linux Home Server (`niltonbedoya/LINUXHOMESERVER`)**:
  - ¿Cómo está configurada la infraestructura del servidor doméstico en Mac Mini con Docker y Tailscale?

---

## 3. Consultas sobre Arquitectura de la Plataforma y Metodología

Preguntas sobre cómo está construida esta plataforma y la metodología de ingeniería:
- **Metodología Gentle-AI**:
  - ¿Qué es la metodología Gentle-AI y cómo combina Organic Driven Development (ODD) con TDD estricto?
  - ¿Por qué se utiliza una suite de pruebas 100% determinista sin dependencias de red en tiempo de test?
- **Sistema Multiagente y Routing de Costo Cero**:
  - ¿Cuáles son los roles de los agentes Nexus, Cerebrito, Centinela, Mensajerito y Auditor?
  - ¿Cómo selecciona Nexus los proveedores LLM gratuitos (Groq, Google AI Studio, Cloudflare Workers AI, OpenRouter)?
  - ¿Cómo protege Centinela el perímetro contra inyecciones de prompt y ataques de jailbreak?
  - ¿Cómo valida el Auditor las salidas para impedir la fuga de datos y asegurar un grounding score mayor a 0.85?

---

## 4. Consultas sobre Trayectoria Profesional, Privacidad y Solicitud de CV

- ¿Cuál es la síntesis de la trayectoria profesional y áreas de especialización de Nilton Bedoya?
- ¿Cómo se puede solicitar el currículum vitae (CV) oficial o contactar para colaboraciones técnicas y profesionales?
- ¿Cuál es el protocolo de privacidad y por qué se requiere indicar empresa, contacto, teléfono, correo y motivo para acceder al CV oficial?
- ¿Qué sucede tras formular más de 5 preguntas sobre la trayectoria o al pedir información personal en el asistente RAG?
