import praw
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from .base import BaseIngestor
import sys
import os

# Append project root to sys.path if needed
sys.path.append(os.getcwd())
from src.config import settings

class RedditIngestor(BaseIngestor):
    """Ingestor for Reddit using PRAW."""

    def __init__(self):
        # We need the client_id and client_secret from .env
        self.reddit = praw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent=settings.REDDIT_USER_AGENT
        )

    def fetch_data(self, subreddit_name: str = "technology", limit: int = 100) -> pd.DataFrame:
        """Fetch hot posts from a subreddit."""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            for post in subreddit.hot(limit=limit):
                posts.append({
                    'record_id': post.id,
                    'title': post.title,
                    'author': str(post.author),
                    'score': post.score,
                    'url': post.url,
                    'created_at': datetime.fromtimestamp(post.created_utc),
                    'comment_count': post.num_comments,
                    'subreddit': subreddit_name,
                    'source': 'reddit'
                })
            return pd.DataFrame(posts)
        except Exception as e:
            print(f"Error fetching from Reddit: {e}")
            return pd.DataFrame()
