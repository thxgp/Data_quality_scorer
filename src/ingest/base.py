from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Any


class BaseIngestor(ABC):
    """Base class for all data source ingestors."""

    @abstractmethod
    def fetch_data(self, *args: Any, **kwargs: Any) -> pd.DataFrame:
        """Fetch data from the source and return a normalized DataFrame."""
        pass

    def normalize(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Common normalization logic if needed."""
        return pd.DataFrame(data)
