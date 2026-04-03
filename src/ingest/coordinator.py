import pandas as pd
from typing import List, Optional
from .hackernews import HackerNewsIngestor
try:
    from .reddit import RedditIngestor
except ImportError:
    # Handle if PRAW or other dependencies aren't yet available
    RedditIngestor = None
from .normalizer import DataNormalizer

class DataIngestor:
    """Unified coordinator for fetching data from multiple sources."""

    def __init__(self):
        self.hn = HackerNewsIngestor()
        self.reddit = None
        if RedditIngestor:
            try:
                self.reddit = RedditIngestor()
            except Exception:
                # Likely credentials not yet set, which is fine
                pass
        self.normalizer = DataNormalizer()

    def fetch_all(self, hn_limit: int = 50, reddit_limit: int = 50) -> pd.DataFrame:
        """Fetch data from both HN and Reddit and return a combined DataFrame."""
        all_dfs = []
        
        # HN
        try:
            hn_df = self.hn.fetch_data(limit=hn_limit)
            all_dfs.append(self.normalizer.normalize(hn_df))
        except Exception as e:
            print(f"Error fetching from HN: {e}")

        # Reddit
        if self.reddit:
            try:
                # We can monitor multiple subreddits
                for sub in ["technology", "dataengineering", "python"]:
                    sub_df = self.reddit.fetch_data(subreddit_name=sub, limit=reddit_limit)
                    all_dfs.append(self.normalizer.normalize(sub_df))
            except Exception as e:
                print(f"Error fetching from Reddit: {e}")

        if not all_dfs:
            return pd.DataFrame()

        return pd.concat(all_dfs, ignore_index=True)
