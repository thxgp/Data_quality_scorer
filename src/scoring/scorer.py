import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List

class QualityScorer:
    """Calculates data quality metrics across multiple dimensions."""

    def __init__(self, weights: Dict[str, float] = None):
        # Default weights from our project plan
        self.weights = weights or {
            'completeness': 0.25,
            'consistency': 0.25,
            'freshness': 0.20,
            'uniqueness': 0.15,
            'accuracy': 0.15
        }

    def score_completeness(self, df: pd.DataFrame) -> float:
        """Percentage of non-null values."""
        if df.empty: return 0.0
        return 1.0 - (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]))

    def score_consistency(self, df: pd.DataFrame) -> float:
        """Detect outliers in numeric fields (score, comment_count)."""
        if df.empty: return 1.0
        scores = []
        for col in ['score', 'comment_count']:
            if col in df.columns:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = df[(df[col] < (q1 - 3 * iqr)) | (df[col] > (q3 + 3 * iqr))]
                scores.append(1.0 - (len(outliers) / len(df)))
        return np.mean(scores) if scores else 1.0

    def score_freshness(self, df: pd.DataFrame, max_age_hours: int = 24) -> float:
        """Measure data recency."""
        if df.empty or 'created_at' not in df.columns: return 0.0
        latest_record = pd.to_datetime(df['created_at']).max()
        if pd.isna(latest_record): return 0.0
        
        # Ensure latest_record is timezone-aware for comparison
        if latest_record.tzinfo is None:
            latest_record = latest_record.replace(tzinfo=timezone.utc)
        
        age_hours = (datetime.now(timezone.utc) - latest_record).total_seconds() / 3600
        return max(0.0, 1.0 - (age_hours / max_age_hours))

    def score_uniqueness(self, df: pd.DataFrame) -> float:
        """Detect duplicate records based on record_id."""
        if df.empty or 'record_id' not in df.columns: return 1.0
        duplicates = df.duplicated(subset=['record_id']).sum()
        return 1.0 - (duplicates / len(df))

    def score_accuracy(self, df: pd.DataFrame) -> float:
        """Validate schema presence and base data types."""
        if df.empty: return 0.0
        required_cols = ['record_id', 'title', 'author', 'score', 'url', 'created_at', 'comment_count']
        present_cols = [col for col in required_cols if col in df.columns]
        return len(present_cols) / len(required_cols)

    def compute_overall_score(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Combine all individual scores into an overall metric (0-100)."""
        metrics = {
            'completeness': self.score_completeness(df),
            'consistency': self.score_consistency(df),
            'freshness': self.score_freshness(df),
            'uniqueness': self.score_uniqueness(df),
            'accuracy': self.score_accuracy(df)
        }
        
        overall = sum(metrics[m] * self.weights[m] for m in metrics) * 100
        status = "GREEN" if overall >= 80 else "YELLOW" if overall >= 70 else "RED"
        
        return {
            'overall_score': round(overall, 2),
            'status': status,
            'metrics': {k: round(v, 4) for k, v in metrics.items()},
            'record_count': len(df),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
