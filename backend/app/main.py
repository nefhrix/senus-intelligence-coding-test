from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.reported_metrics import router as reported_metrics_router

from app.db.base import Base
from app.db.session import engine

from app.models.company import Company
from app.models.document import Document
from app.models.reporting_period import ReportingPeriod
from app.models.reported_metric import ReportedMetric
from app.api.dashboard import router as dashboard_router
from app.api.documents import router as documents_router
from app.api.ai import router as ai_router
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Senus Board Intelligence API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(reported_metrics_router)
app.include_router(dashboard_router)
app.include_router(documents_router)
app.include_router(ai_router)
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "senus-board-intelligence-api",
    }