# Proyecto GitHub: LINUXHOMESERVER — Servidor Doméstico e Infraestructura Privada

## Resumen del Proyecto
Infraestructura de servidor doméstico (homelab) desplegada sobre un Mac mini con sistema operativo Linux, centralizando servicios persistentes de productividad, automatización de flujos de trabajo, monitorización y red privada virtual sin depender de nubes comerciales de terceros.

## Servicios Alojados y Arquitectura
- **Red Privada Virtual (Tailscale)**: Acceso remoto cifrado punto a punto para conectar estaciones de desarrollo, servidores y dispositivos móviles como si estuvieran en la misma red de área local.
- **Automatización de Flujos (n8n)**: Plataforma de integración y automatización de procesos técnicos conectando webhooks, bases de datos y APIs.
- **Monitorización de Disponibilidad (Uptime Kuma)**: Supervisión continua de estado, latencia y disponibilidad de servicios y contenedores con alertas en tiempo real.
- **Interfaz Móvil y Bot de Notificaciones**: Bot integrado en mensajería para alertas operativas, resúmenes de estado y ejecución de comandos remotos controlados.
- **Homepage Dashboard**: Cuadro de mandos unificado con métricas en vivo de recursos (CPU, memoria, almacenamiento), contenedores Docker y accesos rápidos segregados por entornos (Producción, Desarrollo, Administración).
- **Contenerización con Docker Compose**: Despliegue reproducible, aislamiento estricto de volúmenes y red interna no expuesta públicamente.

## Principios de Diseño
- Servidor ligero, eficiente, encendido permanentemente y de bajo consumo.
- Tailscale y claves criptográficas SSH como único vector de acceso remoto.
- Responsabilidad única por servicio y cero exposición de puertos inseguros a internet pública.
