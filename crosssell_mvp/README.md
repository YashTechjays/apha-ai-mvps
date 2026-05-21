# APhA AI Cross-Sell Engine

AI-powered engine that scores every APhA member's expansion potential across 5 product streams (Education, Publications, Events, Career, Advocacy) and fires personalized nudges via email + in-portal banners to grow products-per-member.

## Why it matters
Most APhA members use 1–2 of 6 streams. Moving the average from 1.5 → 2.5 doubles revenue per member with zero acquisition cost. This engine makes that shift systematic.

## Architecture
```
crosssell_mvp/
├── backend/
│   ├── ml/                # 22 features × 5 product XGBoost models, MLflow tracked
│   ├── ai/                # Claude-powered email + banner copy (with fallback)
│   ├── nudge_engine/      # Channel router (email vs banner), suppression rules, Celery tasks
│   ├── pipeline/          # Airflow DAG (Tue 7am UTC) + 3 connectors
│   ├── api/               # FastAPI routes: auth, scores, nudges, banners, analytics
│   └── db/                # Member (25+ usage fields), CrossSellScore, Nudge, Conversion
├── frontend/              # React 18 + Vite + Tailwind + Recharts dashboard
└── tests/                 # pytest — features, scoring, message generator, API
```

## Quick Start
```bash
cd churn_mvp/crosssell_mvp
cp .env.example .env
# Optional: set ANTHROPIC_API_KEY (fallback works without)
docker-compose up --build

# Backend:    http://localhost:8004
# Frontend:   http://localhost:3004  (login: admin / apha2026)
# API docs:   http://localhost:8004/docs
# Redis:      localhost:6380
# Postgres:   localhost:5436
```

## Suppression Rules (router.py)
1. Score must be ≥ `min_expansion_score_to_nudge` (default 60)
2. Skip if member already active on that product
3. Max 2 nudges/member/month (fatigue cap)
4. 14-day cooldown per product
5. **Churn score ≥ 90 → defer to retention team** (integration point with churn MVP)

## Channel Routing
- Score ≥ 80 → email (high-conviction, more impactful)
- 60 ≤ Score < 80 → in-portal banner (less intrusive)

## Banner API (Portal Integration)
```
GET /banners/{member_id}
```
Member portal calls on login. Returns single best banner or `has_banner=false`.

## Integration with Churn MVP
`member.churn_score` is imported from churn MVP weekly. Members ≥ 90 are auto-suppressed — they need retention, not cross-sell. See `nudge_engine/router.py` rule 5.

## Running Tests
```bash
cd backend && pip install -r requirements.txt
PYTHONPATH=. pytest ../tests/ -v
```

## Demo Credentials
- Username: `admin` / password: `apha2026`
- Username: `analyst` / password: `analyst123`
