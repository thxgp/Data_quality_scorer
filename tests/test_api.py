import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the settings before importing the app
with patch.dict(
    os.environ,
    {
        "DATABASE_URL": "sqlite:///:memory:",
        "REDDIT_CLIENT_ID": "test",
        "REDDIT_CLIENT_SECRET": "test",
        "REDDIT_USER_AGENT": "test",
        "SLACK_WEBHOOK_URL": "",
        "CHECK_INTERVAL_HOURS": "1",
    },
):
    from src.api.main import app, db_manager, VALID_SOURCES


@pytest.fixture
def client():
    # Prevent actual scheduler from starting
    with patch("src.api.main.scheduler"):
        with patch.object(db_manager, "init_db"):
            with TestClient(app) as c:
                yield c


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestSourcesEndpoint:
    def test_sources_returns_200(self, client):
        with patch.object(db_manager, "get_latest_metrics", return_value=None):
            response = client.get("/sources")
            assert response.status_code == 200

    def test_sources_lists_all_sources(self, client):
        with patch.object(db_manager, "get_latest_metrics", return_value=None):
            response = client.get("/sources")
            data = response.json()
            assert "sources" in data
            source_names = [s["name"] for s in data["sources"]]
            assert "hackernews" in source_names
            assert "reddit" in source_names

    def test_sources_shows_metrics_when_available(self, client):
        mock_metrics = Mock()
        mock_metrics.overall_score = 85.5
        mock_metrics.status = "GREEN"
        mock_metrics.measured_at = datetime.now(timezone.utc)

        with patch.object(db_manager, "get_latest_metrics", return_value=mock_metrics):
            response = client.get("/sources")
            data = response.json()
            source = next(s for s in data["sources"] if s["name"] == "hackernews")
            assert source["has_data"] is True
            assert source["latest_score"] == 85.5
            assert source["latest_status"] == "GREEN"


class TestLatestQualityEndpoint:
    def test_invalid_source_returns_400(self, client):
        response = client.get("/quality/latest/invalid_source")
        assert response.status_code == 422  # FastAPI validation error

    def test_no_metrics_returns_404(self, client):
        with patch.object(db_manager, "get_latest_metrics", return_value=None):
            response = client.get("/quality/latest/hackernews")
            assert response.status_code == 404

    def test_returns_metrics_when_available(self, client):
        mock_metrics = Mock()
        mock_metrics.source = "hackernews"
        mock_metrics.overall_score = 92.5
        mock_metrics.status = "GREEN"
        mock_metrics.completeness = 1.0
        mock_metrics.consistency = 0.98
        mock_metrics.freshness = 0.95
        mock_metrics.uniqueness = 1.0
        mock_metrics.accuracy = 1.0
        mock_metrics.record_count = 50
        mock_metrics.measured_at = datetime.now(timezone.utc)

        with patch.object(db_manager, "get_latest_metrics", return_value=mock_metrics):
            response = client.get("/quality/latest/hackernews")
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "hackernews"
            assert data["overall_score"] == 92.5
            assert data["status"] == "GREEN"


class TestHistoryEndpoint:
    def test_invalid_source_returns_422(self, client):
        response = client.get("/quality/history/invalid_source")
        assert response.status_code == 422

    def test_limit_validation(self, client):
        # Limit too high
        response = client.get("/quality/history/hackernews?limit=200")
        assert response.status_code == 422

        # Limit too low
        response = client.get("/quality/history/hackernews?limit=0")
        assert response.status_code == 422

    def test_returns_history(self, client):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query

        with patch.object(db_manager, "SessionLocal", return_value=mock_session):
            response = client.get("/quality/history/hackernews?limit=5")
            assert response.status_code == 200
            data = response.json()
            assert data["source"] == "hackernews"
            assert "history" in data


class TestCompareEndpoint:
    def test_compare_returns_200(self, client):
        with patch.object(db_manager, "get_latest_metrics", return_value=None):
            response = client.get("/quality/compare")
            assert response.status_code == 200

    def test_compare_includes_all_sources(self, client):
        with patch.object(db_manager, "get_latest_metrics", return_value=None):
            response = client.get("/quality/compare")
            data = response.json()
            assert "comparison" in data
            for source in VALID_SOURCES:
                assert source in data["comparison"]


class TestRateLimiting:
    def test_rate_limit_not_triggered_normally(self, client):
        # A few requests should be fine
        with patch.object(db_manager, "get_latest_metrics", return_value=None):
            for _ in range(5):
                response = client.get("/sources")
                assert response.status_code == 200
