import time

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from infra.db.models import Base
from infra.db.session import engine

from apps.api.routes.trades import router as trades_router
from apps.api.routes.risk import router as risk_router
from apps.api.routes.events import router as events_router

from apps.api.routes.dashboard_page import router as dashboard_page_router
from apps.api.routes.dashboard_api import router as dashboard_api_router
from apps.api.routes.status_api import router as status_api_router
from apps.api.routes.limits_api import router as limits_api_router
from apps.api.routes.report_api import router as report_api_router

from apps.api.routes.risk_runs_api import router as risk_runs_api_router

# IMPORTANT: this variable must be named `app`
app = FastAPI(title="Risk & Trade Platform", version="0.1.0")

# UI
app.include_router(dashboard_page_router, tags=["dashboard"])
app.include_router(dashboard_api_router, prefix="/api", tags=["dashboard"])

# Core APIs
app.include_router(trades_router, prefix="/trades", tags=["trades"])
app.include_router(risk_router, prefix="/risk", tags=["risk"])
app.include_router(events_router, prefix="/events", tags=["events"])

# Dashboard support APIs
app.include_router(status_api_router, prefix="/api", tags=["dashboard"])
app.include_router(limits_api_router, prefix="/api", tags=["dashboard"])
app.include_router(report_api_router, prefix="/api", tags=["dashboard"])

# Risk run snapshot APIs
app.include_router(risk_runs_api_router, tags=["risk-runs"])


@app.on_event("startup")
def on_startup() -> None:
    for _ in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            time.sleep(1)
    raise RuntimeError("Database did not become ready in time.")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
