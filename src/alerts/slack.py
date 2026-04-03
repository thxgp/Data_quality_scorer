from slack_sdk.webhook import WebhookClient
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class SlackAlertSystem:
    """Handles sending real-time notifications to Slack."""

    def __init__(self):
        self.webhook_url = settings.SLACK_WEBHOOK_URL
        if self.webhook_url:
            self.client = WebhookClient(self.webhook_url)
        else:
            self.client = None

    def send_alert(self, source: str, results: dict):
        """Send a formatted Slack message about a quality breach."""
        if not self.client:
            logger.warning("Slack Webhook URL not set. Skipping alert.")
            return

        score = results['overall_score']
        status = results['status']
        
        # Determine emoji based on status
        emoji = "🔴" if status == "RED" else "🟡"
        
        # Construct the payload
        message = (
            f"{emoji} *Data Quality Alert: {source.upper()}*\n"
            f"> *Project:* {settings.PROJECT_NAME}\n"
            f"> *Overall Score:* `{score}/100`\n"
            f"> *Status:* {status}\n\n"
            "*Metric Breakdown:*\n"
            f"- Completeness: `{results['metrics']['completeness']}`\n"
            f"- Consistency: `{results['metrics']['consistency']}`\n"
            f"- Freshness: `{results['metrics']['freshness']}`\n"
            f"- Uniqueness: `{results['metrics']['uniqueness']}`\n"
            f"- Accuracy: `{results['metrics']['accuracy']}`\n\n"
            "Please check the dashboard for more details! 🚀"
        )

        try:
            response = self.client.send(text=message)
            if response.status_code == 200:
                logger.info(f"Alert sent to Slack for {source}")
            else:
                logger.error(f"Error sending Slack alert: {response.body}")
        except Exception as e:
            logger.error(f"Slack communication failure: {e}")
