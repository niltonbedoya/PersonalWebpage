# Feature Document: F4 — Integración de Identidad Visual y Logo Personal

**Objective:** Integrar la identidad de marca personal y el logotipo "NB" (delineación técnica + degradado violeta/azul cian) en el frontend existente (`web/src/styles/shared.css` y páginas en `web/public/pages/`), respetando la base "Industrial Minimal" y la capa "Software Portfolio".
**Branch:** main.
**Allowed edit surfaces:**
- `odd/f4-branding-logo.md`
- `web/src/styles/shared.css`
- `web/public/pages/index.html`
- `web/public/pages/industrial-smt.html`
- `web/public/pages/software-engineering.html`

## Specs

S1. **Favicon**: Enlazar `/static/assets/logos/logo_icon.ico` como favicon en el `<head>` de las 3 páginas (`index.html`, `industrial-smt.html`, `software-engineering.html`).
S2. **Tokens de color de marca**: Actualizar `web/src/styles/shared.css` para incorporar la paleta extraída del logotipo:
    - Cian de precisión / cobalto: `#0284c7` (hover `#0369a1`).
    - Violeta / índigo tecnológico: `#7c3aed` (hover `#6d28d9`).
    - Gradiente de marca: `linear-gradient(135deg, #7c3aed 0%, #0284c7 100%)`.
    - Mantener legibilidad, contraste y estética Industrial Minimal limpia.
S3. **Navbar con Isotipo**: Implementar un header común con el logo (`/static/assets/logos/logo_transparent.png` a 36-40px de altura), nombre "Nilton Bedoya", especialidad y enlaces de navegación con estados activos.
S4. **Hero en Hub Central (`index.html`)**: Incorporar el isotipo en tamaño destacado o tarjeta visual técnica, reforzando la narrativa de precisión geométrica y doble especialización (SMT/THT + Software/IA).
S5. **Consistencia en Spokes**: Aplicar el header/navbar unificado y la jerarquía de acentos en `industrial-smt.html` y `software-engineering.html`.
S6. **Restricciones de plataforma**: Código fuente y HTML estrictamente ASCII (consola Windows cp1252), rutas absolutas servidas bajo `/static/`, sin regresiones en la suite de tests.

## Tasks

- [x] T1. Crear feature document `odd/f4-branding-logo.md` con specs y constraints.
- [x] T2. Actualizar variables CSS y componentes en `web/src/styles/shared.css` con los tokens de color y clases de branding.
- [x] T3. Actualizar `index.html` con favicon, header con logo y seccion hero integrada.
- [x] T4. Actualizar `industrial-smt.html` y `software-engineering.html` con favicon y header unificado con logo.
- [x] T5. Verificar integridad visual y estructural (pruebas de backend y enlaces).

## Log

- 2026-11-08: Documento creado tras inspeccion visual multimodal de los archivos de logo en `web/public/assets/logos/`.
- 2026-11-08: Implementacion completada por gentle-ai-worker satisfaciendo S1-S6:
  - S1: Favicon agregado a index.html, industrial-smt.html y software-engineering.html (/static/assets/logos/logo_icon.ico).
  - S2: Tokens y componentes CSS agregados a web/src/styles/shared.css (--brand-cyan, --brand-violet, --brand-gradient, .brand-header, .hero-brand, etc.).
  - S3: Header unificado con logo /static/assets/logos/logo_transparent.png (38px), titulo Nilton Bedoya, subtitulos contextuales, links y trigger RAG.
  - S4: Hero con tarjeta tecnica de marca y badge visual con isotipo en index.html.
  - S5: Consistencia visual y estructural en spokes industrial-smt y software-engineering.
  - S6: Codigo 100% ASCII-only y suite completa de tests pasando (376 passed).
