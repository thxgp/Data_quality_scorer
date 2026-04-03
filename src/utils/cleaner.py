import pandas as pd
import re
from typing import List

class DataCleaner:
    """Standardizes and cleans raw data before scoring."""

    @staticmethod
    def clean_strings(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Trim, lowercase, and remove special characters from string fields."""
        for col in columns:
            if col in df.columns:
                # Remove extra whitespace
                df[col] = df[col].astype(str).str.strip()
                # Remove non-ascii characters if needed
                df[col] = df[col].apply(lambda x: re.sub(r'[^\x00-\x7f]', r'', x))
        return df

    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str] = ['record_id']) -> pd.DataFrame:
        """Deduplicate records based on ID."""
        return df.drop_duplicates(subset=subset, keep='first')

    @staticmethod
    def normalize_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Ensure scores and counts are positive integers."""
        for col in columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                df.loc[df[col] < 0, col] = 0
        return df

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Full cleaning pipeline."""
        if df.empty: return df
        
        df = self.remove_duplicates(df)
        df = self.clean_strings(df, ['title', 'author', 'url'])
        df = self.normalize_numeric(df, ['score', 'comment_count'])
        
        return df
