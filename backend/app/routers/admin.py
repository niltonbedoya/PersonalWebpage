"""Admin & Analytics Dashboard Router.

Protected endpoint for the portfolio owner to inspect real visitor IPs,
traffic metrics, and rotating system logs.
"""

import os
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from typing import Dict, Any

from backend.app.db.analytics import analytics_db
from backend.app.core.logging_config import get_recent_logs

admin_router = APIRouter(prefix="/admin", tags=["admin"])
security = HTTPBasic()

DEFAULT_ADMIN_USER = os.environ.get("ADMIN_USER", "nilton")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "NiltonPortfolio2026!")


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Verify HTTP Basic credentials with constant-time comparison."""
    admin_user = os.environ.get("ADMIN_USER", DEFAULT_ADMIN_USER)
    admin_password = os.environ.get("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)

    is_user_correct = secrets.compare_digest(credentials.username.encode("utf8"), admin_user.encode("utf8"))
    is_pass_correct = secrets.compare_digest(credentials.password.encode("utf8"), admin_password.encode("utf8"))

    if not (is_user_correct and is_pass_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de administración incorrectas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@admin_router.get("/api/stats")
async def get_stats_api(_: str = Depends(verify_admin)) -> Dict[str, Any]:
    """Return JSON stats for analytics."""
    return analytics_db.get_stats()


@admin_router.get("/api/logs")
async def get_logs_api(_: str = Depends(verify_admin)) -> Dict[str, Any]:
    """Return recent application log lines."""
    return {"logs": get_recent_logs(lines=100)}


@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(username: str = Depends(verify_admin)) -> HTMLResponse:
    """Render the private administrative analytics and logs dashboard."""
    stats = analytics_db.get_stats()
    visits = analytics_db.get_recent_visits(limit=50)
    logs = get_recent_logs(lines=60)

    rows_html = ""
    for v in visits:
        status_color = "#10b981" if v["status_code"] < 400 else "#f59e0b" if v["status_code"] < 500 else "#ef4444"
        ua_short = (v["user_agent"][:55] + "...") if len(v["user_agent"]) > 55 else v["user_agent"]
        rows_html += f"""
        <tr>
          <td style="color: #94a3b8; font-family: monospace; font-size: 0.85rem;">{v["timestamp"]}</td>
          <td><strong style="color: #38bdf8; font-family: monospace;">{v["ip"]}</strong></td>
          <td><span style="background: #1e293b; padding: 2px 6px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">{v["country"]}</span></td>
          <td style="color: #cbd5e1; font-family: monospace; font-size: 0.85rem;">{v["path"]}</td>
          <td><span style="color: {status_color}; font-weight: bold; font-family: monospace;">{v["status_code"]}</span></td>
          <td style="color: #94a3b8; font-size: 0.8rem;">{v["response_time_ms"]:.1f} ms</td>
          <td style="color: #64748b; font-size: 0.75rem;" title="{v["user_agent"]}">{ua_short}</td>
        </tr>
        """

    logs_text = "\n".join(logs)

    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Panel de Analíticas &mdash; Nilton Bedoya</title>
  <style>
    :root {{
      --bg: #090d16;
      --surface: #0f172a;
      --surface-border: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --cyan: #38bdf8;
      --purple: #a855f7;
    }}
    body {{
      margin: 0;
      padding: 1.5rem;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid var(--surface-border);
      padding-bottom: 1rem;
      margin-bottom: 1.5rem;
    }}
    .header h1 {{
      margin: 0;
      font-size: 1.5rem;
      background: linear-gradient(135deg, #38bdf8, #a855f7);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1rem;
      margin-bottom: 1.5rem;
    }}
    .stat-card {{
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 1.25rem;
    }}
    .stat-card h3 {{
      margin: 0 0 0.5rem 0;
      font-size: 0.85rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .stat-card .val {{
      font-size: 2rem;
      font-weight: 700;
      color: var(--cyan);
    }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 8px;
      padding: 1.25rem;
      margin-bottom: 1.5rem;
    }}
    .card h2 {{
      margin: 0 0 1rem 0;
      font-size: 1.15rem;
      color: var(--text);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
    }}
    th, td {{
      padding: 0.65rem 0.75rem;
      text-align: left;
      border-bottom: 1px solid var(--surface-border);
    }}
    th {{
      color: var(--text-muted);
      font-size: 0.75rem;
      text-transform: uppercase;
      background: #0b1120;
    }}
    .logs-box {{
      background: #050811;
      border: 1px solid #1e293b;
      border-radius: 6px;
      padding: 1rem;
      font-family: Consolas, "Courier New", monospace;
      font-size: 0.8rem;
      color: #38bdf8;
      max-height: 380px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-all;
    }}
    .btn {{
      padding: 0.5rem 1rem;
      background: var(--surface-border);
      color: var(--text);
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
      text-decoration: none;
      font-size: 0.85rem;
    }}
    .btn:hover {{
      background: #334155;
    }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>Panel de Analíticas &mdash; Nilton Bedoya</h1>
      <p style="margin: 0.25rem 0 0 0; font-size: 0.85rem; color: var(--text-muted);">
        Telemetría de visitantes en tiempo real &bull; Sesión autenticada como <strong>{username}</strong>
      </p>
    </div>
    <div>
      <a href="/admin" class="btn">&#8635; Actualizar</a>
      <a href="/static/pages/index.html" class="btn" style="margin-left: 0.5rem;">Ver Sitio Web &rarr;</a>
    </div>
  </div>

  <div class="grid">
    <div class="stat-card">
      <h3>Total Visitas</h3>
      <div class="val">{stats["total_visits"]}</div>
    </div>
    <div class="stat-card">
      <h3>Visitantes Únicos (IPs)</h3>
      <div class="val" style="color: #a855f7;">{stats["unique_ips"]}</div>
    </div>
    <div class="stat-card">
      <h3>Visitas Hoy</h3>
      <div class="val" style="color: #10b981;">{stats["visits_today"]}</div>
    </div>
  </div>

  <div class="card">
    <h2>Registro de Visitas Recientes (Últimas 50)</h2>
    <div style="overflow-x: auto;">
      <table>
        <thead>
          <tr>
            <th>Fecha / Hora</th>
            <th>Dirección IP</th>
            <th>País</th>
            <th>Página / Ruta</th>
            <th>Estado</th>
            <th>Latencia</th>
            <th>Dispositivo / User-Agent</th>
          </tr>
        </thead>
        <tbody>
          {rows_html if rows_html else '<tr><td colspan="7" style="text-align: center; color: #64748b; padding: 2rem;">Aún no hay visitas registradas.</td></tr>'}
        </tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>Fichero de Diagnóstico &amp; Logs en Vivo (logs/app.log)</h2>
    <div class="logs-box">{logs_text}</div>
  </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content, status_code=200)
