# Feature: Formulario y Flujo Conversacional para Solicitud de CV Oficial en RAG

## Specs (S#)

- **S1**: Formulario interactivo en el Drawer del Asistente RAG con 5 campos obligatorios: Empresa, Nombre de contacto, Teléfono, Email y Motivo de la solicitud.
- **S2**: Endpoint backend `/contact/cv-request` con validación Pydantic v2, protección antispam por honeypot y despacho estructurado de alertas hacia `niltonbedoya@hotmail.com` mediante `Mensajerito` y `NotifierMCPAdapter`.
- **S3**: Flujo conversacional guiado (slot-filling interactivo) en `/chat`: al solicitar el CV o tras preguntar por información personal, el asistente formula preguntas individuales paso a paso sin parar hasta recopilar los 5 datos requeridos y confirma el envío.
- **S4**: Control y limitador de sesión en RAG: al acumular 5 o más consultas en la sesión, el asistente orienta de forma natural al usuario a solicitar el CV oficial mediante el formulario o el chat.
- **S5**: Actualización del corpus técnico en `data/` y reindexación vectorial SQLite-vec reflejando la política de privacidad y procedimiento de solicitud de CV.

## Tasks

- [x] T1: Escribir suite de pruebas TDD `backend/tests/test_api_cv_request.py` (Red).
- [x] T2: Implementar modelo `CVRequestForm` y endpoint `/contact/cv-request` en `backend/app/routers/contact.py`.
- [x] T3: Extender `backend/app/agents/mensajerito.py` para enriquecer `summary_notes` con empresa y destinatario.
- [x] T4: Implementar máquina de estados finitos (slot-filling) y contador de preguntas en `backend/app/routers/chat.py`.
- [x] T5: Añadir markup del formulario de CV en los 3 HTML (`index.html`, `industrial-smt.html`, `software-engineering.html`).
- [x] T6: Implementar handlers de envío y apertura del formulario en `web/src/js/drawer-rag.js`.
- [x] T7: Sincronizar diccionario bilingüe ES/EN en `web/src/js/i18n.js`.
- [x] T8: Actualizar `data/nilton_bedoya_profile.md` y `data/guia_preguntas_asistente_rag.md`, y re-indexar corpus.
- [x] T9: Validar suite completa (441 tests pasando en verde).

## Log

- 2026-11-08: Diseñado e implementado el sistema dual (formulario UI + slot-filling por chat) para solicitud de CV oficial.
- 2026-11-08: Confirmada ausencia de fugas PII en Auditor (sin caracteres `@` en respuestas de chat).
- 2026-11-08: 441/441 pruebas pasadas exitosamente.
