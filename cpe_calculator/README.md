# APhA CPE Gap Calculator

Free, public-facing AI tool that helps any pharmacist (member or non-member) find out exactly which APhA CPE courses they need to renew their state license. Acts as a top-of-funnel acquisition tool for APhA membership.

## Funnel
```
Search ("California pharmacist CPE requirements")
  → Free tool (this app)
  → Personalized 3-course preview
  → Email gate → Full plan unlocked
  → "All these courses are free with APhA membership"
  → Join APhA
```

## Architecture
```
cpe_calculator/
├── backend/
│   ├── ai/                # Claude-powered plan generator + fallback
│   ├── api/               # FastAPI routes: calculate, leads, analytics, SEO
│   ├── data/              # All 50 states + DC CPE requirements, APhA course catalog
│   ├── db/                # SQLAlchemy models: Calculation, Lead
│   └── integrations/      # SendGrid lead-nurture trigger (mocked)
├── frontend/              # React 18 + Vite + Tailwind + Framer Motion
├── tests/backend/         # pytest suite (state data, planner, API)
└── scripts/               # validate_state_data.py
```

## Quick Start
```bash
cd churn_mvp/cpe_calculator
cp .env.example .env
# Set ANTHROPIC_API_KEY (optional — fallback plan works without)
docker-compose up --build

# Backend:  http://localhost:8003
# Frontend: http://localhost:3003
# API docs: http://localhost:8003/docs
```

## Key Endpoints
| Method | Path | Purpose |
|---|---|---|
| POST | `/calculate/` | Generate plan — returns 3-course preview |
| GET | `/calculate/full/{id}?session_id=...` | Full plan (lead-gated) |
| POST | `/leads/` | Capture email, unlock full plan, trigger nurture |
| GET | `/analytics/summary` | Calc count, lead conversion, top states |
| GET | `/seo/state/{code}` | SEO meta payload per state |

## How the Plan Generator Works
1. Look up state's `hours_required`, `cycle_years`, and mandatory topics
2. Compute `hours_gap = hours_required - hours_completed`
3. Filter the APhA course catalog by `license_type` and `specialty`
4. Sort: mandatory topics first (e.g. PA needs 2h Pharmacy Law → law course leads)
5. Pass to Claude (`claude-sonnet-4-20250514`) with strict JSON schema
6. Fall back to deterministic selector if Claude API key is absent
7. Return preview (first 3 courses) — full plan gated behind email capture

## Lead-Capture Conversion Flow
- Calculator returns 3 preview courses + 2 blurred "locked" cards
- User clicks "🔓 Unlock full plan (free)" → modal asks for email
- Lead saved → SendGrid nurture sequence triggered (mocked) → full plan unlocked
- All plans surface a `MembershipUpsell` with savings vs. non-member pricing

## SEO Strategy
After launch, generate 51 landing pages — one per state — at `/state/california`, `/state/texas`, etc. Each pre-fills the state field and renders state-specific meta tags via the `/seo/state/{code}` endpoint. Target queries: `"<state> pharmacist CPE requirements 2026"`.

## Testing
```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. pytest ../tests/backend/ -v

# State data validation
python ../scripts/validate_state_data.py
```

## Environment Variables
| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | postgres on :5435 | PostgreSQL connection |
| `ANTHROPIC_API_KEY` | empty | Falls back to deterministic plan if missing |
| `SENDGRID_API_KEY` | empty | Lead nurture stays mocked if missing |
| `FREE_PREVIEW_HOURS` | 3 | Number of courses shown before email gate |
| `JOIN_URL` | pharmacist.com/join | Membership CTA target |
