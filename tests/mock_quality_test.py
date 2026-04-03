import pandas as pd
from datetime import datetime, timedelta, timezone
from src.scoring.scorer import QualityScorer

def test_mock_scoring():
    scorer = QualityScorer()
    
    # Create mock data with some quality issues
    data = [
        # Perfect record
        {'record_id': '1', 'title': 'Post 1', 'author': 'User1', 'score': 100, 'url': 'http1', 
         'created_at': datetime.now(timezone.utc), 'comment_count': 10},
        # Missing author and URL (completeness issue)
        {'record_id': '2', 'title': 'Post 2', 'author': None, 'score': 50, 'url': None, 
         'created_at': datetime.now(timezone.utc), 'comment_count': 5},
        # Duplicate record_id (uniqueness issue)
        {'record_id': '1', 'title': 'Post 1 Duplicate', 'author': 'User1', 'score': 100, 'url': 'http1', 
         'created_at': datetime.now(timezone.utc), 'comment_count': 10},
        # Outlier score (consistency issue)
        {'record_id': '3', 'title': 'Post 3', 'author': 'User2', 'score': 10000, 'url': 'http2', 
         'created_at': datetime.now(timezone.utc), 'comment_count': 2},
        # Old record (freshness issue)
        {'record_id': '4', 'title': 'Post 4', 'author': 'User3', 'score': 20, 'url': 'http3', 
         'created_at': datetime.now(timezone.utc) - timedelta(days=2), 'comment_count': 1},
    ]
    
    df = pd.DataFrame(data)
    results = scorer.compute_overall_score(df)
    
    print("\n--- DATA QUALITY REPORT (MOCK DATA) ---")
    print(f"Overall Score: {results['overall_score']}")
    print(f"Status: {results['status']}")
    print("\n--- METRIC BREAKDOWN ---")
    for metric, score in results['metrics'].items():
        print(f"{metric.capitalize()}: {score}")
    print("----------------------------------------\n")

if __name__ == "__main__":
    test_mock_scoring()
