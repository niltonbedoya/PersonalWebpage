#!/usr/bin/env bash
# deploy/deploy.sh
# Ejecutado por el runner self-hosted de GitHub Actions en el Mac Mini.
# Hace git pull, reinstala dependencias si cambiaron, y reinicia el servicio FastAPI.
set -euo pipefail

REPO_DIR="${HOME}/showcase-platform"   # <-- Cambiar si el repo está en otra ruta
SERVICE_NAME="showcase-platform"
LOG_FILE="${HOME}/showcase-platform-deploy.log"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

cd "${REPO_DIR}" || { log "ERROR: No se pudo entrar a ${REPO_DIR}"; exit 1; }

log "=== Iniciando despliegue en $(hostname) ==="

# 1. Traer los últimos cambios de main
log "Descargando cambios desde origin/main..."
git fetch origin
git checkout main
git reset --hard origin/main

# 2. Instalar/actualizar dependencias de Python
log "Instalando dependencias de Python..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Reiniciar el servicio FastAPI
log "Reiniciando servicio ${SERVICE_NAME}..."
if systemctl is-active --quiet "${SERVICE_NAME}"; then
  sudo systemctl restart "${SERVICE_NAME}"
else
  log "ADVERTENCIA: El servicio ${SERVICE_NAME} no está activo. Intenta iniciarlo manualmente."
  sudo systemctl start "${SERVICE_NAME}" || true
fi

# 4. Verificar que el servicio esté vivo
sleep 3
if systemctl is-active --quiet "${SERVICE_NAME}"; then
  log "OK: Servicio ${SERVICE_NAME} está activo."
else
  log "ERROR: El servicio ${SERVICE_NAME} no pudo iniciarse. Revisa los logs:"
  sudo journalctl -u "${SERVICE_NAME}" --no-pager -n 30 | tee -a "${LOG_FILE}"
  exit 1
fi

# 5. Health check rápido (si curl está disponible)
if command -v curl >/dev/null 2>&1; then
  log "Probando endpoint /health..."
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health || true)
  if [ "${HTTP_CODE}" = "200" ]; then
    log "OK: /health responde 200"
  else
    log "ADVERTENCIA: /health responde ${HTTP_CODE:-sin respuesta}"
  fi
fi

log "=== Despliegue completado ==="
