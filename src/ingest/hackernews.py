import httpx
import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseIngestor


class HackerNewsIngestor(BaseIngestor):
    """Ingestor for HackerNews using the Firebase API."""

    BASE_URL = "https://hacker-news.firebaseio.com/v0"

    def fetch_data(self, limit: int = 50) -> pd.DataFrame:
        """Fetch top stories from HackerNews synchronously."""
        try:
            with httpx.Client() as client:
                # 1. Fetch top story IDs
                response = client.get(f"{self.BASE_URL}/topstories.json")
                response.raise_for_status()
                story_ids = response.json()[:limit]

                # 2. Fetch each story details
                stories = []
                for story_id in story_ids:
                    item_response = client.get(f"{self.BASE_URL}/item/{story_id}.json")
                    if item_response.status_code == 200:
                        stories.append(item_response.json())

                return self.normalize_stories(stories)
        except Exception as e:
            print(f"Error fetching HackerNews data: {e}")
            return pd.DataFrame()

    def normalize_stories(self, stories: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert HN raw data into a standardized DataFrame."""
        df = pd.DataFrame(stories)

        # Mapping HN fields to our standard schema
        standard_df = pd.DataFrame()
        standard_df["record_id"] = df["id"].astype(str)
        standard_df["title"] = df["title"]
        standard_df["author"] = df.get("by", "Unknown")
        standard_df["score"] = df.get("score", 0)
        standard_df["url"] = df.get("url", "")

        # Convert timestamp to datetime
        # HN uses a Unix timestamp in seconds
        standard_df["created_at"] = pd.to_datetime(df["time"], unit="s")

        standard_df["comment_count"] = df.get("descendants", 0)
        standard_df["source"] = "hackernews"

        return standard_df
