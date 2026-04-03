import pandas as pd
import numpy as np
from typing import Dict, Any, List

class AnomalyDetector:
    """Detects unusual patterns in datasets that may indicate corruption."""

    def __init__(self, iqr_multiplier: float = 3.0):
        self.iqr_multiplier = iqr_multiplier

    def detect_constant_columns(self, df: pd.DataFrame) -> List[str]:
        """Find columns where all rows have the same value."""
        return [col for col in df.columns if df[col].nunique() == 1]

    def detect_extreme_outliers(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, int]:
        """Count outliers using a very high IQR threshold (indicative of bugs)."""
        counts = {}
        for col in columns:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                # Using 3x IQR for extreme "bug-like" outliers
                outliers = df[(df[col] < (q1 - self.iqr_multiplier * iqr)) | (df[col] > (q3 + self.iqr_multiplier * iqr))]
                counts[col] = len(outliers)
        return counts

    def run_check(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run all anomaly detection checks."""
        if df.empty: return {}
        
        return {
            'constant_columns': self.detect_constant_columns(df),
            'extreme_outliers': self.detect_extreme_outliers(df, ['score', 'comment_count']),
            'all_null_columns': [col for col in df.columns if df[col].isnull().all()]
        }
