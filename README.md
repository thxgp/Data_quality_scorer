# Data Quality Scorer - Automatic Monitoring System 🚀

This project is an automated data quality monitoring system that pulls data from Reddit and HackerNews, runs it through a 5-dimension scoring engine, and provides real-time Slack alerts and a Power BI-ready database.

## 🛠️ Tech Stack & Capabilities
- **Backend Architecture**: FastAPI, SQLAlchemy, APScheduler, PRAW. 🏗️
- **Storage**: Supabase (PostgreSQL) with optimized JSON support. 🗄️
- **Quality Engine**: Scores data based on **Completeness, Consistency, Freshness, Uniqueness, and Accuracy**. 🧠
- **Real-time Alerting**: Pushes 🟡/🔴 Slack notifications for quality drops. 🚨
- **Portfolio Ready**: Professional API documentation (Swagger) and Power BI optimized SQL views. 📈

## 🚀 Quick Launch
1.  **Configure Environment**: Copy `.env.example` to `.env` and enter your credentials (Supabase, Reddit, Slack). 🛠️
2.  **Install Dependencies**: `pip install -r requirements.txt`. 📦
3.  **Start API & Monitoring**: `python -m src.api.main`. 💎

## 🌐 API Endpoints
- `/health`: System status check. ✅
- `/quality/latest/{source}`: Most recent quality score. 📊
- `/quality/history/{source}`: Historical data trends for Power BI. 📈

## 📂 Project Structure
- `src/ingest`: Data fetching and normalization. 📥
- `src/scoring`: Core quality scoring logic. 🧠
- `src/database`: Supabase persistence and models. 🗄️
- `src/api`: FastAPI server and endpoints. 🌐
- `src/alerts`: Slack notification system. 🚨
- `src/schedulers`: Automated hourly background jobs. ⏰

## 📈 Power BI Integration
See [**DATABASE.md**](./DATABASE.md) for optimized SQL queries and a step-by-step connection guide. 🎯
