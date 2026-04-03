from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import sys
import os

# Append project root to sys.path
sys.path.append(os.getcwd())
from src.config import settings
from src.database.db_manager import DatabaseManager
from src.database.models import QualityMetrics
from src.schedulers.scheduler import QualityCheckScheduler

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Automated Data Quality Monitoring for HackerNews & Reddit",
    version="0.1.0"
)

# Enable CORS for Power BI and Dashboard usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_manager = DatabaseManager()
scheduler = QualityCheckScheduler()

@app.on_event("startup")
def startup_event():
    """Start the background scheduler on API startup."""
    # Initialize DB (create tables)
    db_manager.init_db()
    # Start Scheduler
    scheduler.start()

@app.get("/health")
def health_check():
    """Health status endpoint."""
    return {"status": "healthy", "project": settings.PROJECT_NAME}

@app.get("/quality/latest/{source}")
def get_latest_quality(source: str):
    """Retrieve the absolute latest quality score for a source."""
    metrics = db_manager.get_latest_metrics(source)
    if not metrics:
        raise HTTPException(status_code=404, detail=f"No metrics found for {source}")
    return metrics

@app.get("/quality/history/{source}")
def get_quality_history(source: str, limit: int = 10):
    """Fetch historical trends (for Power BI)."""
    with db_manager.SessionLocal() as db:
        history = db.query(QualityMetrics)\
            .filter(QualityMetrics.source == source)\
            .order_by(QualityMetrics.measured_at.desc())\
            .limit(limit)\
            .all()
        return history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
