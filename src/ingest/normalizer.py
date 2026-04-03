import pandas as pd
from typing import List, Dict, Any

class DataNormalizer:
    """Standardizes data from different sources into a uniform schema."""

    REQUIRED_COLUMNS = [
        'record_id', 'title', 'author', 'score', 
        'url', 'created_at', 'comment_count', 'source'
    ]

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform common cleaning and validation."""
        if df.empty:
            return df

        # Ensure all required columns exist
        for col in self.REQUIRED_COLUMNS:
            if col not in df.columns:
                df[col] = None

        # Fix types
        df['score'] = pd.to_numeric(df['score'], errors='coerce').fillna(0).astype(int)
        df['comment_count'] = pd.to_numeric(df['comment_count'], errors='coerce').fillna(0).astype(int)
        
        # Ensure non-negative values
        df.loc[df['score'] < 0, 'score'] = 0
        df.loc[df['comment_count'] < 0, 'comment_count'] = 0

        # Cast to standard schema
        return df[self.REQUIRED_COLUMNS]
