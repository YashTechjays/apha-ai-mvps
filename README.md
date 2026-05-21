# APhA Churn Prediction MVP

ML-powered member churn prediction system for the American Pharmacists Association, built by the Techjays AI Team.

## Quick Start

```bash
# 1. Start all services
docker-compose up --build -d

# 2. Run database migrations
docker-compose exec backend alembic upgrade head

# 3. Train the model (first-time setup)
docker-compose exec backend python -m backend.ml.train

# 4. Verify API health
curl http://localhost:8000/health

# 5. Open the dashboard
open http://localhost:3000
# Login: admin / apha2026
```

## Architecture

| Layer | Technology |
|---|---|
| API | FastAPI + Python 3.11 |
| ML | XGBoost, SHAP, MLflow |
| Database | PostgreSQL via SQLAlchemy 2.0 |
| Migrations | Alembic |
| Pipeline | Apache Airflow 2.8 |
| Frontend | React 18 + TailwindCSS + Recharts |
| Auth | JWT (python-jose) |
| Infra | AWS (S3, RDS, ECR) via Terraform |

## Features

- **25-feature ML model** trained on member behavioral signals (login recency, CPE hours, email engagement, event attendance, etc.)
- **Weekly Airflow DAG** pulls from CRM, LMS, and email platform, then runs batch scoring
- **SHAP explanations** for every risk score — shows retention team exactly why a member is flagged
- **4-tier risk classification**: Critical (85–100), High (70–84), Medium (50–69), Low (0–49)
- **React dashboard** with KPI cards, risk distribution chart, sortable member table, and member detail view

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/auth/login` | Get JWT token |
| GET | `/members/` | List all members with latest scores |
| GET | `/members/{id}` | Single member detail |
| POST | `/scores/run` | Trigger batch scoring run |
| GET | `/scores/distribution` | Risk tier counts for dashboard |
| GET | `/scores/member/{id}/explain` | SHAP explanation for member |
| GET | `/alerts/` | List active alerts |
| PATCH | `/alerts/{id}` | Resolve alert with outcome |

## Running Tests

```bash
docker-compose exec backend pytest tests/ -v
```

## Production Deployment

1. Set `TF_VAR_db_password` and run `terraform apply` in `infra/`
2. Build and push Docker image to ECR
3. Set real `DATABASE_URL` pointing to RDS endpoint
4. Replace mock connectors in `backend/pipeline/connectors/` with real API integrations

## Demo Credentials

- **admin** / apha2026
- **retention** / retention123
