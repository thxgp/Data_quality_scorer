# Data Quality Scorer - Database Guide (Power BI Optimized)

This guide provides the optimized SQL queries you need to connect your Supabase database to Power BI for high-performance dashboards.

## TABLE 1: Quality Metrics (Current Status)
**Use Case**: Gauge visualizations and current status badges (GREEN/YELLOW/RED).

```sql
SELECT 
    source, 
    overall_score, 
    status, 
    measured_at,
    record_count
FROM quality_metrics
WHERE measured_at IN (
    SELECT MAX(measured_at) 
    FROM quality_metrics 
    GROUP BY source
);
```

## TABLE 2: Quality Trend History (7 Days)
**Use Case**: Line and area charts showing how your data quality changes over time.

```sql
SELECT 
    source, 
    measured_at::DATE as event_date,
    AVG(overall_score) as avg_score,
    AVG(completeness_score) * 100 as completeness,
    AVG(consistency_score) * 100 as consistency,
    AVG(freshness_score) * 100 as freshness,
    AVG(uniqueness_score) * 100 as uniqueness,
    AVG(accuracy_score) * 100 as accuracy
FROM quality_metrics
WHERE measured_at >= NOW() - INTERVAL '7 days'
GROUP BY 1, 2
ORDER BY 2 DESC;
```

## TABLE 3: Anomaly & Issue Feed
**Use Case**: Table visualization to show the most recent "Problematic" checks.

```sql
SELECT 
    source, 
    status, 
    overall_score, 
    record_count,
    measured_at,
    issues_json
FROM quality_metrics
WHERE status != 'GREEN'
ORDER BY measured_at DESC
LIMIT 50;
```

## Connection for Power BI
1. Open **Power BI Desktop**.
2. Click **Get Data** > **PostgreSQL database**.
3. Use your Supabase host (e.g. `db.supabase.co`) and enter your credentials.
4. Paste the SQL queries above into the **Advanced options** block for optimal performance!
