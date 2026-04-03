import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.ingest.hackernews import HackerNewsIngestor
from src.ingest.normalizer import DataNormalizer


class TestHackerNewsIngestor:
    @patch("src.ingest.hackernews.httpx.Client")
    def test_fetch_data_success(self, mock_client_class):
        # Setup mock client instance
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        # Mock responses
        mock_top_stories = Mock()
        mock_top_stories.json.return_value = [1001, 1002, 1003]
        mock_top_stories.raise_for_status = Mock()
        mock_top_stories.status_code = 200

        mock_story1 = Mock()
        mock_story1.json.return_value = {
            "id": 1001,
            "title": "Test Story 1",
            "by": "user1",
            "score": 100,
            "url": "https://example.com/1",
            "time": 1700000000,
            "descendants": 25,
        }
        mock_story1.status_code = 200

        mock_story2 = Mock()
        mock_story2.json.return_value = {
            "id": 1002,
            "title": "Test Story 2",
            "by": "user2",
            "score": 50,
            "url": "https://example.com/2",
            "time": 1700001000,
            "descendants": 10,
        }
        mock_story2.status_code = 200

        mock_story3 = Mock()
        mock_story3.json.return_value = {
            "id": 1003,
            "title": "Test Story 3",
            "by": "user3",
            "score": 75,
            "url": "https://example.com/3",
            "time": 1700002000,
            "descendants": 15,
        }
        mock_story3.status_code = 200

        mock_client.get.side_effect = [
            mock_top_stories,
            mock_story1,
            mock_story2,
            mock_story3,
        ]

        ingestor = HackerNewsIngestor()
        df = ingestor.fetch_data(limit=3)

        assert len(df) == 3
        assert "record_id" in df.columns
        assert "title" in df.columns
        assert "author" in df.columns
        assert "score" in df.columns
        assert df.iloc[0]["title"] == "Test Story 1"

    @patch("src.ingest.hackernews.httpx.Client")
    def test_fetch_data_handles_missing_fields(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)

        mock_top_stories = Mock()
        mock_top_stories.json.return_value = [1001]
        mock_top_stories.raise_for_status = Mock()
        mock_top_stories.status_code = 200

        # Story with missing optional fields
        mock_story = Mock()
        mock_story.json.return_value = {
            "id": 1001,
            "title": "Ask HN: Question",
            "by": "user1",
            "score": 30,
            "time": 1700000000,
            # No url, no descendants
        }
        mock_story.status_code = 200

        mock_client.get.side_effect = [mock_top_stories, mock_story]

        ingestor = HackerNewsIngestor()
        df = ingestor.fetch_data(limit=1)

        assert len(df) == 1
        assert df.iloc[0]["url"] is None or df.iloc[0]["url"] == ""

    @patch("src.ingest.hackernews.httpx.Client")
    def test_fetch_data_handles_api_error(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__ = Mock(return_value=mock_client)
        mock_client_class.return_value.__exit__ = Mock(return_value=False)
        mock_client.get.side_effect = Exception("API Error")

        ingestor = HackerNewsIngestor()
        df = ingestor.fetch_data(limit=5)

        assert df.empty


class TestDataNormalizer:
    @pytest.fixture
    def normalizer(self):
        return DataNormalizer()

    def test_normalize_adds_missing_columns(self, normalizer):
        df = pd.DataFrame({"record_id": ["1", "2"], "title": ["A", "B"]})
        result = normalizer.normalize(df)

        for col in DataNormalizer.REQUIRED_COLUMNS:
            assert col in result.columns

    def test_normalize_fixes_numeric_types(self, normalizer):
        df = pd.DataFrame(
            {
                "record_id": ["1"],
                "title": ["Test"],
                "author": ["user"],
                "score": ["100"],  # String instead of int
                "url": ["http://test.com"],
                "created_at": [datetime.now()],
                "comment_count": ["50"],  # String
                "source": ["hackernews"],
            }
        )
        result = normalizer.normalize(df)

        assert result["score"].dtype in ["int32", "int64"]
        assert result["comment_count"].dtype in ["int32", "int64"]

    def test_normalize_handles_negative_values(self, normalizer):
        df = pd.DataFrame(
            {
                "record_id": ["1"],
                "title": ["Test"],
                "author": ["user"],
                "score": [-10],
                "url": ["http://test.com"],
                "created_at": [datetime.now()],
                "comment_count": [-5],
                "source": ["hackernews"],
            }
        )
        result = normalizer.normalize(df)

        assert result["score"].iloc[0] >= 0
        assert result["comment_count"].iloc[0] >= 0

    def test_normalize_empty_df(self, normalizer):
        result = normalizer.normalize(pd.DataFrame())
        assert result.empty

    def test_normalize_returns_only_required_columns(self, normalizer):
        df = pd.DataFrame(
            {
                "record_id": ["1"],
                "title": ["Test"],
                "author": ["user"],
                "score": [100],
                "url": ["http://test.com"],
                "created_at": [datetime.now()],
                "comment_count": [50],
                "source": ["hackernews"],
                "extra_column": ["should be removed"],
            }
        )
        result = normalizer.normalize(df)

        assert "extra_column" not in result.columns
        assert len(result.columns) == len(DataNormalizer.REQUIRED_COLUMNS)
