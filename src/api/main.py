from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Literal
from datetime import datetime
import time
import sys
import os

# Append project root to sys.path
sys.path.append(os.getcwd())
from src.config import settings
from src.database.db_manager import DatabaseManager
from src.database.models import QualityMetrics
from src.schedulers.scheduler import QualityCheckScheduler

# Simple in-memory rate limiter
rate_limit_store: dict[str, list[float]] = {}
RATE_LIMIT = 60  # requests per minute
RATE_WINDOW = 60  # seconds


def check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    # Clean old entries
    rate_limit_store[client_ip] = [
        t for t in rate_limit_store[client_ip] if now - t < RATE_WINDOW
    ]
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT:
        return False
    rate_limit_store[client_ip].append(now)
    return True


db_manager = DatabaseManager()
scheduler = QualityCheckScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db_manager.init_db()
    scheduler.start()
    yield
    # Shutdown
    scheduler.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Automated Data Quality Monitoring for HackerNews & Reddit",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for Power BI and Dashboard usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        return JSONResponse(
            status_code=429, content={"detail": "Rate limit exceeded. Try again later."}
        )
    response = await call_next(request)
    return response


# Valid sources
VALID_SOURCES = ["hackernews", "reddit"]
SourceType = Literal["hackernews", "reddit"]


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/sources")
def list_sources():
    """List all available data sources with their current status."""
    sources_info = []
    for source in VALID_SOURCES:
        latest = db_manager.get_latest_metrics(source)
        sources_info.append(
            {
                "name": source,
                "has_data": latest is not None,
                "latest_score": latest.overall_score if latest else None,
                "latest_status": latest.status if latest else None,
                "last_checked": latest.measured_at.isoformat() if latest else None,
            }
        )
    return {"sources": sources_info}


@app.get("/quality/latest/{source}")
def get_latest_quality(source: SourceType):
    """Retrieve the latest quality score for a source."""
    if source not in VALID_SOURCES:
        raise HTTPException(
            status_code=400, detail=f"Invalid source. Must be one of: {VALID_SOURCES}"
        )
    metrics = db_manager.get_latest_metrics(source)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No metrics found for {source}")
    return {
        "source": metrics.source,
        "overall_score": metrics.overall_score,
        "status": metrics.status,
        "completeness": metrics.completeness,
        "consistency": metrics.consistency,
        "freshness": metrics.freshness,
        "uniqueness": metrics.uniqueness,
        "accuracy": metrics.accuracy,
        "record_count": metrics.record_count,
        "measured_at": metrics.measured_at.isoformat(),
    }


@app.get("/quality/history/{source}")
def get_quality_history(
    source: SourceType,
    limit: int = Query(
        default=10, ge=1, le=100, description="Number of records to return"
    ),
):
    """Fetch historical quality trends for Power BI or dashboards."""
    if source not in VALID_SOURCES:
        raise HTTPException(
            status_code=400, detail=f"Invalid source. Must be one of: {VALID_SOURCES}"
        )
    with db_manager.SessionLocal() as db:
        history = (
            db.query(QualityMetrics)
            .filter(QualityMetrics.source == source)
            .order_by(QualityMetrics.measured_at.desc())
            .limit(limit)
            .all()
        )
        return {
            "source": source,
            "count": len(history),
            "history": [
                {
                    "overall_score": h.overall_score,
                    "status": h.status,
                    "completeness": h.completeness,
                    "consistency": h.consistency,
                    "freshness": h.freshness,
                    "uniqueness": h.uniqueness,
                    "accuracy": h.accuracy,
                    "record_count": h.record_count,
                    "measured_at": h.measured_at.isoformat(),
                }
                for h in history
            ],
        }


@app.get("/quality/compare")
def compare_sources():
    """Compare latest quality metrics across all sources."""
    comparison = {}
    for source in VALID_SOURCES:
        latest = db_manager.get_latest_metrics(source)
        if latest:
            comparison[source] = {
                "overall_score": latest.overall_score,
                "status": latest.status,
                "record_count": latest.record_count,
                "measured_at": latest.measured_at.isoformat(),
            }
        else:
            comparison[source] = None
    return {"comparison": comparison, "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
