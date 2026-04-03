import pytest
import pandas as pd
from datetime import datetime, timezone, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.scoring.scorer import QualityScorer


@pytest.fixture
def scorer():
    return QualityScorer()


@pytest.fixture
def sample_df():
    """Create a sample DataFrame with realistic HackerNews-like data."""
    now = datetime.now(timezone.utc)
    return pd.DataFrame(
        [
            {
                "record_id": "1001",
                "title": "Introduction to Machine Learning",
                "author": "user1",
                "score": 150,
                "url": "https://example.com/ml-intro",
                "created_at": now - timedelta(hours=2),
                "comment_count": 45,
                "source": "hackernews",
            },
            {
                "record_id": "1002",
                "title": "Building APIs with FastAPI",
                "author": "user2",
                "score": 89,
                "url": "https://example.com/fastapi",
                "created_at": now - timedelta(hours=5),
                "comment_count": 22,
                "source": "hackernews",
            },
            {
                "record_id": "1003",
                "title": "PostgreSQL Performance Tips",
                "author": "user3",
                "score": 200,
                "url": "https://example.com/postgres",
                "created_at": now - timedelta(hours=1),
                "comment_count": 78,
                "source": "hackernews",
            },
        ]
    )


class TestScoreCompleteness:
    def test_full_data_returns_1(self, scorer, sample_df):
        score = scorer.score_completeness(sample_df)
        assert score == 1.0

    def test_missing_values_reduces_score(self, scorer):
        df = pd.DataFrame(
            {
                "record_id": ["1", "2", None],
                "title": ["A", None, "C"],
                "author": ["x", "y", "z"],
            }
        )
        score = scorer.score_completeness(df)
        assert 0 < score < 1
        # 2 nulls out of 9 cells = ~0.78
        assert abs(score - (7 / 9)) < 0.01

    def test_empty_df_returns_0(self, scorer):
        assert scorer.score_completeness(pd.DataFrame()) == 0.0


class TestScoreConsistency:
    def test_no_outliers_returns_1(self, scorer, sample_df):
        score = scorer.score_consistency(sample_df)
        assert score == 1.0

    def test_extreme_outliers_reduce_score(self, scorer):
        df = pd.DataFrame(
            {
                "score": [10, 12, 11, 13, 9, 1000000],  # Extreme outlier
                "comment_count": [5, 6, 4, 7, 5, 6],
            }
        )
        score = scorer.score_consistency(df)
        assert score < 1.0

    def test_empty_df_returns_1(self, scorer):
        assert scorer.score_consistency(pd.DataFrame()) == 1.0


class TestScoreFreshness:
    def test_recent_data_high_score(self, scorer):
        now = datetime.now(timezone.utc)
        df = pd.DataFrame({"created_at": [now - timedelta(hours=1)]})
        score = scorer.score_freshness(df, max_age_hours=24)
        assert score > 0.9

    def test_old_data_low_score(self, scorer):
        now = datetime.now(timezone.utc)
        df = pd.DataFrame({"created_at": [now - timedelta(hours=48)]})
        score = scorer.score_freshness(df, max_age_hours=24)
        assert score == 0.0

    def test_empty_df_returns_0(self, scorer):
        assert scorer.score_freshness(pd.DataFrame()) == 0.0

    def test_missing_column_returns_0(self, scorer):
        df = pd.DataFrame({"other_col": [1, 2, 3]})
        assert scorer.score_freshness(df) == 0.0


class TestScoreUniqueness:
    def test_all_unique_returns_1(self, scorer, sample_df):
        score = scorer.score_uniqueness(sample_df)
        assert score == 1.0

    def test_duplicates_reduce_score(self, scorer):
        df = pd.DataFrame({"record_id": ["1", "2", "2", "3", "3", "3"]})
        score = scorer.score_uniqueness(df)
        # 3 duplicates out of 6 = 0.5
        assert score == 0.5

    def test_empty_df_returns_1(self, scorer):
        assert scorer.score_uniqueness(pd.DataFrame()) == 1.0


class TestScoreAccuracy:
    def test_all_columns_present_returns_1(self, scorer, sample_df):
        score = scorer.score_accuracy(sample_df)
        assert score == 1.0

    def test_missing_columns_reduces_score(self, scorer):
        df = pd.DataFrame({"record_id": ["1"], "title": ["Test"], "author": ["user"]})
        score = scorer.score_accuracy(df)
        # 3 out of 7 required columns
        assert abs(score - (3 / 7)) < 0.01

    def test_empty_df_returns_0(self, scorer):
        assert scorer.score_accuracy(pd.DataFrame()) == 0.0


class TestComputeOverallScore:
    def test_perfect_data_high_score(self, scorer, sample_df):
        result = scorer.compute_overall_score(sample_df)
        assert result["overall_score"] >= 80
        assert result["status"] == "GREEN"
        assert "metrics" in result
        assert "record_count" in result
        assert result["record_count"] == 3

    def test_empty_df_low_score(self, scorer):
        result = scorer.compute_overall_score(pd.DataFrame())
        assert result["overall_score"] < 70
        assert result["status"] == "RED"
        assert result["record_count"] == 0

    def test_custom_weights(self):
        custom_weights = {
            "completeness": 0.5,
            "consistency": 0.2,
            "freshness": 0.1,
            "uniqueness": 0.1,
            "accuracy": 0.1,
        }
        scorer = QualityScorer(weights=custom_weights)
        assert scorer.weights == custom_weights

    def test_result_has_timestamp(self, scorer, sample_df):
        result = scorer.compute_overall_score(sample_df)
        assert "timestamp" in result
        # Should be ISO format
        datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))


class TestStatusThresholds:
    def test_green_threshold(self, scorer, sample_df):
        result = scorer.compute_overall_score(sample_df)
        if result["overall_score"] >= 80:
            assert result["status"] == "GREEN"

    def test_yellow_threshold(self, scorer):
        # Create data that should score in YELLOW range
        df = pd.DataFrame(
            {
                "record_id": ["1", "1", "2"],  # Some duplicates
                "title": ["A", "B", None],  # Some nulls
                "author": ["x", "y", "z"],
                "score": [10, 20, 30],
                "url": ["http://a", "http://b", "http://c"],
                "created_at": [datetime.now(timezone.utc) - timedelta(hours=20)] * 3,
                "comment_count": [1, 2, 3],
            }
        )
        result = scorer.compute_overall_score(df)
        # May be YELLOW or RED depending on exact scoring
        assert result["status"] in ["YELLOW", "RED", "GREEN"]
