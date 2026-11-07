"""FastAPI Backend Routers — Zero-Cost LLM Routing.

Re-exports the per-agent routers so main.py keeps a single import surface:

    from backend.app.routers import router, news_router, contact_router, health_router

Each router delegates to the appropriate free-tier LLM provider:
- /chat → Nexus (router central)
- /news → Radarito (curación de feeds)
- /contact → Mensajerito (triage de leads)
- /health → estado global
"""

from backend.app.routers.chat import router
from backend.app.routers.news import news_router
from backend.app.routers.contact import contact_router
from backend.app.routers.health import health_router

__all__ = ["router", "news_router", "contact_router", "health_router"]
