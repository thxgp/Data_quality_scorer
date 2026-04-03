from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import sys
import os

# Append project root to sys.path
sys.path.append(os.getcwd())
from src.config import settings
from .models import Base, RawDataRecord, QualityMetrics, StatusEnum

class DatabaseManager:
    """Manages all database operations: connections, storage, and queries."""

    def __init__(self):
        # Using connection pooling for efficiency
        self.engine = create_engine(
            settings.DATABASE_URL,
            pool_recycle=3600,
            pool_pre_ping=True
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
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

    def store_raw_records(self, source: str, records: List[Dict[str, Any]]):
        """Bulk store raw records for auditing."""
        with self.SessionLocal() as db:
            db_records = [
                RawDataRecord(
                    source=source,
                    record_id=r.get('record_id'),
                    data_json=r
                ) for r in records
            ]
            db.add_all(db_records)
            db.commit()

    def store_quality_metrics(self, source: str, results: Dict[str, Any]):
        """Save computed quality metrics to the database."""
        with self.SessionLocal() as db:
            metrics = QualityMetrics(
                source=source,
                measured_at=datetime.now(timezone.utc),
                completeness_score=results['metrics']['completeness'],
                consistency_score=results['metrics']['consistency'],
                freshness_score=results['metrics']['freshness'],
                uniqueness_score=results['metrics']['uniqueness'],
                accuracy_score=results['metrics']['accuracy'],
                overall_score=results['overall_score'],
                status=StatusEnum(results['status']),
                record_count=results['record_count'],
                issues_json=results.get('issues', {})
            )
            db.add(metrics)
            db.commit()
            db.refresh(metrics)
            return metrics

    def get_latest_metrics(self, source: str) -> Optional[QualityMetrics]:
        """Fetch the most recent quality check for a source."""
        with self.SessionLocal() as db:
            return db.query(QualityMetrics)\
                .filter(QualityMetrics.source == source)\
                .order_by(desc(QualityMetrics.measured_at))\
                .first()
