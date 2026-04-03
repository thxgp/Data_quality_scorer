from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone
import enum

Base = declarative_base()

class StatusEnum(enum.Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"

class RawDataRecord(Base):
    """Stores every individual record fetched for audit and traceability."""
    __tablename__ = "raw_data_records"

    id = Column(Integer, primary_key=True)
    source = Column(String, index=True)         # 'reddit' or 'hackernews'
    record_id = Column(String, index=True)      # Original ID from the source
    data_json = Column(JSON)                    # Full record as JSON
    ingested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class QualityMetrics(Base):
    """Stores quality scores for each batch check (Data for Power BI)."""
    __tablename__ = "quality_metrics"

    id = Column(Integer, primary_key=True)
    source = Column(String, index=True)
    measured_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Dimension Scores (0-1)
    completeness_score = Column(Float)
    consistency_score = Column(Float)
    freshness_score = Column(Float)
    uniqueness_score = Column(Float)
    accuracy_score = Column(Float)
    
    # Aggregated Metrics
    overall_score = Column(Float)               # 0-100
    status = Column(SQLEnum(StatusEnum))        # GREEN/YELLOW/RED
    
    record_count = Column(Integer)
    issues_json = Column(JSON)                  # Detailed issue breakdown

    def __repr__(self):
        return f"<QualityMetrics(source='{self.source}', score={self.overall_score})>"
