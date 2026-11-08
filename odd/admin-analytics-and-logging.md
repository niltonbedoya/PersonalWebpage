# Feature Document: Panel de Analíticas Privado (/admin) & Logging Rotativo

**Objective:** Implementar un sistema de telemetría propio, privado y de costo cero para registrar todas las visitas reales con su IP (mediante cabeceras Cloudflare `CF-Connecting-IP`), una vista administrativa web `/admin` protegida con HTTP Basic Auth, y un sistema de logging rotativo en disco (`logs/app.log`) para diagnóstico del sistema y del RAG.

**Branch:** main. **Test runner:** `python -m pytest backend/tests/ -v`

## Specs

S1. Detección de IP y país real: extraer prioritariamente `CF-Connecting-IP` y `CF-IPCountry` de Cloudflare (con fallback a `X-Forwarded-For` y `client.host`).
S2. Registro de analíticas: registrar cada visita a páginas y endpoints API en SQLite (`data/analytics.db`) registrando `timestamp`, `ip`, `country`, `path`, `user_agent`, `status_code` y `response_time_ms`.
S3. Panel web `/admin`: interfaz visual privada protegida mediante HTTP Basic Auth (`ADMIN_USER` y `ADMIN_PASSWORD` en `.env`), mostrando:
   - Resumen de métricas: total visitas, visitantes únicos (IPs), visitas de hoy.
   - Tabla de visitas recientes con timestamp, IP, país, ruta y estado.
   - Visor de las últimas líneas de logs de `logs/app.log`.
S4. Sistema de logs rotativo: `RotatingFileHandler` en `logs/app.log` (10 MB máx, 5 backups) con formato estructurado, registrando peticiones, bloqueos de seguridad y errores.
S5. TDD: suite de tests unitarios e integrados comprobando autenticación `/admin`, registro de visitas en SQLite y rotación de logs sin regresiones sobre los 455 tests existentes.
S6. Geolocalización granular de visitantes: capturar y persistir ciudad (`city`) y zona/región (`region`) junto con la IP y país (vía cabeceras Cloudflare `CF-IPCity` y `CF-Region`, con resolución de respaldo geoip cacheada), mostrándolas en una columna dedicada de Ubicación en el panel `/admin`.

## Tasks

T1. Crear feature doc `odd/admin-analytics-and-logging.md`.
T2. Crear módulo de base de datos de analíticas `backend/app/db/analytics.py` con tests en `backend/tests/test_analytics_db.py`.
T3. Crear configuración de logging rotativo `backend/app/core/logging_config.py`.
T4. Implementar middleware de registro de visitas en `backend/main.py`.
T5. Implementar router `/admin` protegido con HTTP Basic Auth en `backend/app/routers/admin.py` con tests en `backend/tests/test_api_admin.py`.
T6. Ampliar esquema de base de datos analytics con `city` y `region`, resolver geoip granular y enriquecer la tabla del panel `/admin`.
T7. Ejecutar suite completa de tests, verificar 100% verde, registrar memoria en Engram, commit y push a `main`.

## Log

L1. 2026-11-08: Panel de analíticas privado (/admin) y logging rotativo completado con éxito.
- S1 & S2: Creado módulo `backend/app/db/analytics.py` con tabla SQLite `visits` e índices optimizados en `data/analytics.db`.
- S3: Creado router `/admin` protegido con HTTP Basic Auth (`ADMIN_USER`, `ADMIN_PASSWORD`) que renderiza dashboard visual con métricas, IPs reales, países, latencia y visor de logs en vivo.
- S4: Configurado `backend/app/core/logging_config.py` con `RotatingFileHandler` en `logs/app.log` (10 MB máx, 5 copias) para diagnóstico bounded.
- S5: Suite completa de pruebas expandida a 464 tests (9 nuevos tests en `test_analytics_db.py` y `test_api_admin.py`), 100% en verde sin regresiones.
L2. 2026-11-08: Enriquecimiento de geolocalización granular (S6, T6, T7).
- Extendido `backend/app/db/analytics.py` con soporte para `city` y `region` y migración automática e idempotente.
- Creado `backend/app/core/geoip.py` para resolver ciudad y región desde cabeceras Cloudflare (`CF-IPCity`, `CF-Region`) y fallback cacheado en memoria.
- Actualizado `backend/main.py` para inyectar `city` y `region` en `analytics_middleware`.
- Actualizado `backend/app/routers/admin.py` con la columna "Ciudad / Zona" junto a la Dirección IP.
- Tests actualizados y suite de 464 tests pasando 100% verde.

