# Feature Document: F4 -- Rediseno Dark Mode Ergonomico con Identidad de Marca

**Objective:** Redisenar completamente el frontend a Dark Mode profesional de alta fidelidad ergonomica, alineado 1:1 con la estetica de `logo_dark.png` (fondo oscuro mate `#090d16`, contrastes calibrados, logo discreto y elegante en navbar ~30px, sin bloques desproporcionados, acentos cian para Industrial y violeta para Software).
**Branch:** main.
**Allowed edit surfaces:**
- `odd/f4-branding-logo.md`
- `web/src/styles/shared.css`
- `web/public/pages/index.html`
- `web/public/pages/industrial-smt.html`
- `web/public/pages/software-engineering.html`

## Specs

S1. **Fondo Dark Mode & Tokens Cromaticos de Alta Ergonomia**:
    - `--bg: #090d16;` (lienzo tecnico oscuro profundo).
    - `--surface: #111827;` (superficie de tarjetas gris pizarra oscuro).
    - `--surface-hover: #1a2234;`
    - `--border: #1e293b;` y `--border-glow: rgba(14, 165, 233, 0.2);`
    - `--text: #f8fafc;` (blanco nitido alta legibilidad WCAG AAA).
    - `--muted: #94a3b8;` (gris tecnico equilibrado).
    - `--accent-cyan: #0ea5e9;` (acento industrial SMT/THT).
    - `--accent-violet: #8b5cf6;` (acento software & IA).
    - `--brand-gradient: linear-gradient(135deg, #8b5cf6 0%, #0ea5e9 100%);`
S2. **Dimensionamiento Ergonomico del Logo**:
    - Reducir el isotipo en navbar a un tamano discreto y profesional (~30px).
    - Eliminar la tarjeta/caja sobredimensionada del hero que desentonaba.
    - Integrar la identidad con sutileza tecnica (monograma elegante, tipografia precisa).
S3. **Header / Navbar Dark Mode**:
    - Barra oscura integrada con `backdrop-filter: blur(12px)` y fondo `#0d131f` con borde inferior sutil (`#1e293b`).
    - Enlaces de navegacion con indicadores luminosos (hover y active con acentos cian/violeta).
    - Boton de Asistente RAG estilizado en modo oscuro con borde y resplandor de gradiente.
S4. **Personalizacion Ergonomica por Pagina**:
    - **Hub (`index.html`)**: Hero conciso y elegante, Split Cards con acentos balanceados (cian para SMT/THT, violeta para Software), metricas tecnicas con look de instrumentacion.
    - **Spoke Industrial (`industrial-smt.html`)**: Estetica de sala limpia / instrumentacion industrial, tarjetas con acentos cian `#0ea5e9` y badges de tecnologia.
    - **Spoke Software (`software-engineering.html`)**: Estetica de ingenieria de software moderna / ciber-inteligencia, tarjetas con acentos violeta `#8b5cf6`, tags de codigo `#0d131f` con texto violeta.
S5. **Compatibilidad y Restricciones**:
    - Todo el HTML/CSS/JS/MD es estrictamente ASCII (entidades HTML para caracteres especiales) para compatibilidad con Windows cp1252.
    - Cero regresiones en la suite de 376 tests.

## Tasks

- [x] T1. Actualizar `odd/f4-branding-logo.md` con las especificaciones de Dark Mode.
- [x] T2. Reescribir `web/src/styles/shared.css` con el sistema completo de diseno Dark Mode.
- [x] T3. Redisenar `web/public/pages/index.html` (Hub Central en Dark Mode sin logo sobredimensionado).
- [x] T4. Redisenar `web/public/pages/industrial-smt.html` (Spoke Industrial SMT/THT en Dark Mode).
- [x] T5. Redisenar `web/public/pages/software-engineering.html` (Spoke Software en Dark Mode).
- [x] T6. Ejecutar suite de pruebas y verificar enlaces y contraste.

## Log

- 2026-11-08: Redefinicion a Dark Mode tras feedback del usuario (logo discreto ~30px, paleta completa del logo en modo oscuro ergonomico).
- 2026-11-08: Implementacion completa en shared.css, index.html, industrial-smt.html y software-engineering.html. 376/376 tests pasando satisfactoriamente. Todos los archivos verificados 100% ASCII-clean.
