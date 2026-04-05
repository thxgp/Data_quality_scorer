from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import sys
import os
import numpy as np
import pandas as pd

# Append project root to sys.path
sys.path.append(os.getcwd())
from src.config import settings
from .models import Base, RawDataRecord, QualityMetrics, StatusEnum


class DatabaseManager:
    """Manages all database operations: connections, storage, and queries."""

    def __init__(self):
        # Using connection pooling for efficiency
        self.engine = create_engine(
            settings.DATABASE_URL, pool_recycle=3600, pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def init_db(self):
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self.engine)

    def get_db(self) -> Session:
        """Dependency to get a DB session."""
        db = self.SessionLocal()
        try:
            return db
        finally:
            db.close()

    def _serialize_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Convert pandas Timestamps and other non-JSON types to serializable format."""
        serialized = {}
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                serialized[key] = value.isoformat()
            elif isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                # Recursively handle nested structures
                serialized[key] = json.loads(json.dumps(value, default=str))
            else:
                serialized[key] = value
        return serialized

    def store_raw_records(self, source: str, records: List[Dict[str, Any]]):
        """Bulk store raw records for auditing."""
        with self.SessionLocal() as db:
            db_records = [
                RawDataRecord(
                    source=source,
                    record_id=r.get("record_id"),
                    data_json=self._serialize_record(r),
                )
                for r in records
            ]
            db.add_all(db_records)
            db.commit()

    def _to_python_float(self, value) -> float:
        """Convert numpy types to native Python float."""
        if isinstance(value, (np.floating, np.integer)):
            return float(value)
        return value

    def store_quality_metrics(self, source: str, results: Dict[str, Any]):
        """Save computed quality metrics to the database."""
        with self.SessionLocal() as db:
            metrics = QualityMetrics(
                source=source,
                measured_at=datetime.now(timezone.utc),
                completeness_score=self._to_python_float(
                    results["metrics"]["completeness"]
                ),
                consistency_score=self._to_python_float(
                    results["metrics"]["consistency"]
                ),
                freshness_score=self._to_python_float(results["metrics"]["freshness"]),
                uniqueness_score=self._to_python_float(
                    results["metrics"]["uniqueness"]
                ),
                accuracy_score=self._to_python_float(results["metrics"]["accuracy"]),
                overall_score=self._to_python_float(results["overall_score"]),
                status=StatusEnum(results["status"]),
                record_count=int(results["record_count"]),
                issues_json=results.get("issues", {}),
            )
            db.add(metrics)
            db.commit()
            db.refresh(metrics)
            return metrics

    def get_latest_metrics(self, source: str) -> Optional[QualityMetrics]:
        """Fetch the most recent quality check for a source."""
        with self.SessionLocal() as db:
            return (
                db.query(QualityMetrics)
                .filter(QualityMetrics.source == source)
                .order_by(desc(QualityMetrics.measured_at))
                .first()
            )
