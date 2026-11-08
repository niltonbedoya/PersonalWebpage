#!/usr/bin/env bash
# deploy/deploy.sh
# Ejecutado por el runner self-hosted de GitHub Actions en el Mac Mini.
# Hace git pull, reinstala dependencias si cambiaron, y reinicia el servicio FastAPI.
set -euo pipefail

REPO_DIR="${REPO_DIR:-${HOME}/Proyectos/PersonalWebpage}"
SERVICE_NAME="${SERVICE_NAME:-personalwebpage.service}"
LOG_FILE="${HOME}/personalwebpage-deploy.log"

USER_ID="$(id -u)"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/${USER_ID}}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/${USER_ID}/bus}"

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

# 2. Reconstruir índice RAG
log "Reconstruyendo índice RAG..."
if [ -f "${REPO_DIR}/venv/bin/python" ]; then
  PYTHON_BIN="${REPO_DIR}/venv/bin/python"
elif [ -f "${REPO_DIR}/.venv/bin/python" ]; then
  PYTHON_BIN="${REPO_DIR}/.venv/bin/python"
else
  PYTHON_BIN="python3"
fi
${PYTHON_BIN} -c "from backend.app.db.indexer import index_corpus; index_corpus()" || true

# 3. Reiniciar el servicio FastAPI (systemd user)
log "Reiniciando servicio ${SERVICE_NAME}..."
systemctl --user restart "${SERVICE_NAME}" || sudo -n systemctl restart "${SERVICE_NAME}" || true

# 4. Verificar que el servicio esté vivo
sleep 2
if systemctl --user is-active --quiet "${SERVICE_NAME}" || sudo -n systemctl is-active --quiet "${SERVICE_NAME}"; then
  log "OK: Servicio ${SERVICE_NAME} está activo."
else
  log "ERROR: El servicio ${SERVICE_NAME} no pudo iniciarse."
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
