# Despliegue en Mac Mini (Linux Mint) — Showcase Platform

Este documento explica cómo configurar tu Mac Mini (Linux Mint) como servidor de despliegue para la Showcase Platform, usando el runner self-hosted de GitHub Actions para CI/CD automático.

## Requisitos previos en el Mac Mini

- Linux Mint (o cualquier distribución con `systemd`)
- Usuario con acceso a `sudo`
- SSH habilitado y accesible (desde tu red local, y opcionalmente desde internet vía Cloudflare Tunnel)
- Git instalado: `sudo apt update && sudo apt install git`
- Python 3.12 instalado: `sudo apt install python3.12 python3-pip`
- El repositorio clonado: `git clone https://github.com/niltonbedoya/PersonalWebpage.git ~/showcase-platform`

## Paso 1: Clonar el repositorio (una sola vez)

```bash
cd ~
git clone https://github.com/niltonbedoya/PersonalWebpage.git showcase-platform
cd showcase-platform
```

## Paso 2: Instalar dependencias de Python

```bash
cd ~/showcase-platform
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

## Paso 3: Crear el servicio systemd

El servicio ejecuta `python -m backend.main` como `nilto` y se reinicia solo si falla.

```bash
sudo cp deploy/backend.service /etc/systemd/system/showcase-platform.service
sudo systemctl daemon-reload
sudo systemctl enable showcase-platform.service
sudo systemctl start showcase-platform.service
```

Verificar que está vivo:

```bash
systemctl status showcase-platform.service
curl http://127.0.0.1:8000/health
```

Deberías ver algo como:

```json
{"status":"healthy","pydantic_contracts":[...],"active_agents":[...],"zero_cost_routing":true,...}
```

## Paso 4: Configurar el runner self-hosted de GitHub Actions

Para que GitHub Actions pueda desplegar en tu Mac Mini, necesitas registrar un runner self-hosted:

1. Ve a tu repositorio en GitHub → **Settings** → **Actions** → **Runners**
2. Click en **New self-hosted runner**
3. Elige **Linux** y **x64**
4. Sigue los pasos que te muestre GitHub (descargar, extraer, configurar, ejecutar)

Resumen de comandos (ajusta la versión del runner si GitHub te indica otra):

```bash
mkdir -p ~/actions-runner && cd ~/actions-runner
curl -o actions-runner-linux-x64-2.316.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.316.0/actions-runner-linux-x64-2.316.0.tar.gz
tar xzf ./actions-runner-linux-x64-2.316.0.tar.gz
./config.sh --url https://github.com/niltonbedoya/PersonalWebpage --token <TOKEN_DE_GITHUB>
./svc.sh install
./svc.sh start
```

El token se muestra en pantalla durante el paso de configuración en GitHub.

Una vez el runner esté corriendo, el workflow de `.github/workflows/ci-cd.yml` hará automáticamente:
1. **Test:** corre los 395 tests en tu Mac Mini
2. **Deploy:** si pasan, hace `git pull`, reinstala dependencias y reinicia el servicio FastAPI

## Paso 5: Acceso remoto seguro (opcional pero recomendado)

Para acceder al backend desde fuera de tu red doméstica sin abrir puertos en el router, usa **Cloudflare Tunnel** (gratuito):

```bash
# Instalar cloudflared en el Mac Mini
sudo apt install cloudflared

# Autenticar (una sola vez)
cloudflared tunnel login

# Crear túnel apuntando a localhost:8000
cloudflared tunnel create showcase

# Mapear el túnel a tu dominio (ej: backend.tudominio.com)
cloudflared tunnel route dns showcase backend.tudominio.com

# Ejecutar el túnel
cloudflared tunnel run showcase
```

Puedes dejar el túnel corriendo como servicio:

```bash
cloudflared service install showcase
sudo systemctl start cloudflared-showcase
```

Así tu backend queda accesible en `https://backend.tudominio.com` sin abrir puertos en el router.

## Estructura de archivos de despliegue

| Archivo | Propósito |
|---------|-----------|
| `deploy/deploy.sh` | Script que ejecuta el runner: git pull, pip install, reinicia servicio |
| `deploy/backend.service` | Unit de systemd para correr el backend como servicio |
| `deploy/Dockerfile` | (Opcional) Imagen Docker del backend |
| `deploy/docker-compose.yml` | (Opcional) Orquestación con Docker Compose |
| `deploy/.env.example` | Ejemplo de variables de entorno |

## Comandos útiles

```bash
# Ver logs del backend
sudo journalctl -u showcase-platform.service -f

# Reiniciar manualmente
sudo systemctl restart showcase-platform.service

# Ver estado
systemctl status showcase-platform.service

# Probar el endpoint
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/static/pages/index.html
```

## Solución de problemas

| Problema | Solución |
|----------|----------|
| El servicio no inicia | `sudo journalctl -u showcase-platform.service -n 50` |
| Puerto 8000 ocupado | `sudo ss -tlnp | grep 8000` y mata el proceso |
| El runner no se conecta | Revisa que `./svc.sh start` esté corriendo en el Mac Mini |
| Tests fallan en CI | Ejecuta `python -m pytest backend/tests/ tests/ -q` localmente |
