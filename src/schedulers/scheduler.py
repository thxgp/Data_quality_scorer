from apscheduler.schedulers.background import BackgroundScheduler
from src.ingest.coordinator import DataIngestor
from src.scoring.scorer import QualityScorer
from src.database.db_manager import DatabaseManager
from src.alerts.slack import SlackAlertSystem
from src.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QualityCheckScheduler:
    """Orchestrates manual and scheduled quality checks."""

    def __init__(self):
        self.ingestor = DataIngestor()
        self.scorer = QualityScorer()
        self.db = DatabaseManager()
        self.alerts = SlackAlertSystem()
        self.scheduler = BackgroundScheduler()

    def run_full_check(self):
        """Perform a complete Ingest -> Score -> Save pipeline."""
        logger.info("Starting automated quality check cycle...")

        sources = ["hackernews", "reddit"]

        for source in sources:
            try:
                # Fetch
                if source == "hackernews":
                    df = self.ingestor.hn.fetch_data(limit=50)
                else:
                    if self.ingestor.reddit:
                        df = self.ingestor.reddit.fetch_data(
                            subreddit_name="technology", limit=50
                        )
                    else:
                        logger.warning(
                            "RedditIngestor not initialized (Check credentials)"
                        )
                        continue

                if df.empty:
                    logger.warning(f"No data fetched for {source}")
                    continue

                # Normalise
                df = self.ingestor.normalizer.normalize(df)

                # Score
                results = self.scorer.compute_overall_score(df)
                logger.info(
                    f"Quality Check for {source}: Score {results['overall_score']} ({results['status']})"
                )

                # Persist
                self.db.store_raw_records(source, df.to_dict("records"))
                self.db.store_quality_metrics(source, results)

                # Trigger Alerts if status == RED or YELLOW
                if results["status"] in ["RED", "YELLOW"]:
                    self.alerts.send_alert(source, results)

            except Exception as e:
                logger.error(f"Error during quality check for {source}: {e}")

    def start(self):
        """Initialize and start the background scheduler."""
        self.scheduler.add_job(
            self.run_full_check, "interval", hours=settings.CHECK_INTERVAL_HOURS
        )
        self.scheduler.start()
        logger.info(
            f"Scheduler started: Running every {settings.CHECK_INTERVAL_HOURS} hour(s)"
        )

    def stop(self):
        """Shutdown the scheduler gracefully."""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")
