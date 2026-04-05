import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

from src.alerts.slack import SlackAlertSystem

def test_slack():
    """Manually triggers a test alert to Slack."""
    print("Connecting to Slack Alert System...")
    alert_system = SlackAlertSystem()

    # Create dummy data for the test
    test_results = {
        "overall_score": 64.50,
        "status": "RED",
        "metrics": {
            "completeness": 0.65,
            "consistency": 0.60,
            "freshness": 0.55,
            "uniqueness": 0.98,
            "accuracy": 0.97
        }
    }

    print(f"Sending test alert for 'hackernews' (Score: {test_results['overall_score']})...")
    alert_system.send_alert("hackernews", test_results)
    print("Test complete! Please check your Slack channel.")

if __name__ == "__main__":
    test_slack()
