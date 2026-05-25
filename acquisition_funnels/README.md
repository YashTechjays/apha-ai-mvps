# APhA AI-Powered Public Acquisition Funnels

Three public-facing AI-powered free tools that attract non-member pharmacists through organic search, demonstrate APhA's value, capture leads, and funnel them into membership.

## The 3 Funnels

| Tool | Route | Target Search Intent | Conversion Hook |
|---|---|---|---|
| Salary Benchmarker | `/salary` | "pharmacist salary [state/specialty]" | Full analysis gated behind email |
| Drug Interaction Checker | `/interactions` | "drug interaction [drug A] [drug B]" | 3 free checks/day, unlimited with membership |
| Career Readiness Scorer | `/career` | "pharmacist career assessment" | 90-day action plan gated behind email |

## Tech Stack

- **Backend:** FastAPI + Python 3.11, SQLAlchemy, PostgreSQL, Redis
- **AI:** Anthropic Claude API (claude-sonnet-4-20250514)
- **Frontend:** React 18 + TailwindCSS + Recharts + Framer Motion
- **Email:** SendGrid (mocked in dev)
- **Infra:** Docker Compose

## Quick Start

```bash
# 1. Copy environment file
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY

# 2. Start services
docker compose up --build

# 3. Open
# Backend API docs: http://localhost:8006/docs
# Frontend: http://localhost:3006
```

## Ports

| Service | Port |
|---|---|
| Backend API | 8006 |
| Frontend | 3006 |
| PostgreSQL | 5438 |
| Redis | 6382 |

## API Endpoints

### Salary Benchmarker
- `POST /salary/benchmark` - Generate salary benchmark + AI analysis
- `GET /salary/states` - List available states
- `GET /salary/specialties` - List specialties

### Drug Interaction Checker
- `POST /interactions/check` - Check drug interaction
- `POST /interactions/search` - Autocomplete drug search

### Career Readiness Scorer
- `POST /career/score` - Score career readiness (6 dimensions)
- `GET /career/action-plan/{usage_id}` - Get action plan (lead-gated)

### Shared
- `POST /leads/` - Capture lead from any funnel
- `GET /analytics/summary` - Funnel conversion analytics
- `GET /health` - Health check

## Running Tests

```bash
cd acquisition_funnels
pip install -r backend/requirements.txt
pytest tests/backend/ -v
```

## Built by
Techjays AI Team
