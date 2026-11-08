# Proyecto GitHub: Servicio de Tickets y Gestión Técnica

## Resumen del Proyecto
Sistema integral de gestión técnica y comercial para empresas de servicio en campo (Field Service). Permite la gestión completa de clientes, parque de maquinaria industrial, tickets de asistencia, partes de trabajo e intervenciones en planta, agenda de técnicos y generación/firma digital de albaranes con soporte web y móvil.

## Arquitectura del Proyecto: Monolito Modular
El sistema está diseñado bajo el patrón arquitectónico de Monolito Modular, dividiendo el código estrictamente por dominios de negocio desacoplados:
- `albaranes`: Lógica de facturación de servicios, tarifas, esquemas de firma digital táctil y remota, y renderizado de albaranes en PDF.
- `clientes`: Gestión jerárquica de empresas clientes, sedes de trabajo y contactos autorizados.
- `maquinas`: Inventario de parque de maquinaria industrial instalada, números de serie, marcas, modelos e historial de intervenciones.
- `tickets`: Ciclo de vida completo de solicitudes de asistencia técnica, priorización y asignación inteligente a técnicos.

## Capacidades Offline-First y Resiliencia
- **Progressive Web App (PWA)**: Implementación de Service Workers (Workbox) con almacenamiento en caché local, permitiendo a los técnicos abrir la aplicación y consultar su agenda e historial de tickets en plantas industriales sin cobertura o sótanos blindados.
- **Cola Transaccional Outbox (IndexedDB)**: En modo sin cobertura, los técnicos pueden rellenar albaranes y recoger firmas biométricas en pantalla encolándolas localmente. Al recuperar la conectividad, el sistema sincroniza automáticamente en segundo plano y dispara las notificaciones remotas.
- **Fail-Safe para Tickets Temporales**: Saneamiento automatizado de tickets preliminares abandonados (TMP), validando la hora oficial por internet para evitar desajustes de reloj local.

## Seguridad y Hardening OWASP Top 10
- **Control de Acceso Granular (RBAC)**: Aislamiento estricto de importes y totales en albaranes según rol (técnico, gestor, administrador).
- **Protección Criptográfica**: Sesiones JWT con expiración corta (1 hora), firmas con HMAC-SHA256, hashes PBKDF2-SHA256 para credenciales y tokens de firma remota de alta entropía (48 bytes URL-safe) almacenados como hash SHA-256.
- **Prevención de Inyecciones**: Eliminación de consultas concatenadas, uso exclusivo de ORM parametrizado y validación por listas blancas (whitelisting).
- **Rate Limiting**: Limitador de tasa en memoria con algoritmo de ventana deslizante (Sliding Window) en endpoints públicos.

## Stack Tecnológico
- **Backend**: Python 3.12, FastAPI, SQLAlchemy (ORM), PostgreSQL, Pydantic v2.
- **Frontend**: React 18, TypeScript, Vite, Zustand, Tailwind CSS, shadcn/ui.
- **Móvil**: Aplicación Android nativa empaquetada mediante Capacitor.
- **Infraestructura**: Docker Compose, Caddy (proxy inverso con TLS automático y compresión zstd/gzip), red VPN segura.
- **Testing**: Suite automatizada con Pytest en backend y Playwright para pruebas E2E de interfaz.
