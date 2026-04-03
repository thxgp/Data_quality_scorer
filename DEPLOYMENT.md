# Deployment Guide

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL database (Supabase recommended)
- Reddit API credentials (optional, for Reddit data source)
- Slack webhook URL (optional, for alerts)

## Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL`: PostgreSQL connection string (e.g., `postgresql://user:pass@host:5432/dbname`)

Optional variables:
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USER_AGENT`: For Reddit data source
- `SLACK_WEBHOOK_URL`: For Slack alerts
- `CHECK_INTERVAL_HOURS`: Quality check frequency (default: 1)

## Local Development

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Start the API
python -m src.api.main
```

The API will be available at `http://localhost:8000`.

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /sources` | List all data sources with status |
| `GET /quality/latest/{source}` | Latest quality score for a source |
| `GET /quality/history/{source}` | Historical quality trends |
| `GET /quality/compare` | Compare all sources |

## Docker Deployment

### Build and Run

```bash
# Build the image
docker build -t data-quality-scorer .

# Run with environment variables
docker run -d \
  --name data-quality-api \
  -p 8000:8000 \
  -e DATABASE_URL="your_database_url" \
  -e SLACK_WEBHOOK_URL="your_webhook" \
  data-quality-scorer
```

### Using Docker Compose

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop
docker-compose down
```

## Cloud Deployment

### Render.com

1. Connect your GitHub repository
2. Create a new Web Service
3. Set environment variables in Render dashboard
4. Deploy

### Railway

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Deploy: `railway up`

### Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login and deploy
fly auth login
fly launch
fly secrets set DATABASE_URL="your_database_url"
fly deploy
```

## Database Setup (Supabase)

1. Create a new Supabase project
2. Copy the connection string from Settings > Database
3. Tables are auto-created on first API startup

### Manual Table Creation (if needed)

```sql
-- Raw data records
CREATE TABLE IF NOT EXISTS raw_data_records (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    title TEXT,
    author VARCHAR(100),
    score INTEGER,
    url TEXT,
    created_at TIMESTAMP,
    comment_count INTEGER,
    ingested_at TIMESTAMP DEFAULT NOW()
);

-- Quality metrics
CREATE TABLE IF NOT EXISTS quality_metrics (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    overall_score FLOAT NOT NULL,
    status VARCHAR(10) NOT NULL,
    completeness FLOAT,
    consistency FLOAT,
    freshness FLOAT,
    uniqueness FLOAT,
    accuracy FLOAT,
    record_count INTEGER,
    measured_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_metrics_source ON quality_metrics(source);
CREATE INDEX idx_metrics_measured_at ON quality_metrics(measured_at DESC);
CREATE INDEX idx_raw_source ON raw_data_records(source);
```

## Monitoring

### Health Checks

The `/health` endpoint returns:
```json
{
  "status": "healthy",
  "project": "Data Quality Scorer",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Slack Alerts

Configure `SLACK_WEBHOOK_URL` to receive alerts when:
- Quality score drops to YELLOW (70-80)
- Quality score drops to RED (<70)

### Power BI Integration

Use the `/quality/history/{source}` endpoint to fetch data for Power BI dashboards. See `DATABASE.md` for SQL queries.

## Troubleshooting

### Common Issues

1. **Database connection failed**
   - Verify `DATABASE_URL` is correct
   - Check network/firewall rules
   - Ensure database is running

2. **Reddit API not working**
   - Verify credentials in `.env`
   - Check Reddit app status at https://www.reddit.com/prefs/apps

3. **Slack alerts not sending**
   - Verify webhook URL is correct
   - Test webhook manually: `curl -X POST -H 'Content-type: application/json' --data '{"text":"test"}' YOUR_WEBHOOK_URL`

4. **Tests failing**
   - Ensure all dependencies installed: `pip install -r requirements.txt`
   - Run with verbose: `pytest tests/ -v --tb=short`
