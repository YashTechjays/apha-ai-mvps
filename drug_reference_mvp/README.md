# APhA Clinical Assistant — AI Drug Reference Tool (B2B SaaS MVP)

A retrieval-augmented clinical drug reference for licensed pharmacists, packaged as a B2B SaaS with Stripe-based subscription billing, JWT + API key auth, rate limiting, and a React frontend.

This is the **AI Drug Reference Tool MVP** — sixth project in the APhA AI suite under `/Users/mainadmin/churn_mvp/`.

---

## What it does

- Pharmacists ask clinical drug-information questions in natural language
- Answers are retrieved from a curated APhA reference library (drug monographs, clinical guidelines, pharmacy practice) and synthesized by Claude (with deterministic fallback)
- Every clinically substantive statement is cited
- Built-in safety guardrails flag patient-specific or red-flag queries
- Subscription-based access (Trial / Individual / Team / Institution / Enterprise) with per-plan rate limits and query quotas
- API access for B2B integrations

---

## Architecture

```
React (3005) ──► FastAPI (8005) ──► Postgres (5437) ──► SQLAlchemy models
                       │              Redis (6381)   ──► sliding-window rate limit
                       │              ChromaDB        ──► sentence-transformer embeddings
                       │              Anthropic Claude (claude-sonnet-4-20250514)
                       │              Stripe (checkout + webhooks)
                       └─► /api/v1/{auth, query, subscriptions, webhooks, analytics}
```

### Stack

| Layer | Tech |
|------|------|
| Backend | Python 3.11 · FastAPI · SQLAlchemy 2.0 · Alembic-ready |
| RAG | ChromaDB + sentence-transformers (`all-MiniLM-L6-v2`) |
| LLM | Anthropic Claude (`claude-sonnet-4-20250514`) with deterministic fallback |
| Auth | JWT (python-jose) + API keys (bcrypt-hashed, prefix lookup) |
| Billing | Stripe Checkout + Webhooks |
| Rate limit | Redis sliding window (in-memory fallback) |
| Frontend | React 18 · Vite · TailwindCSS · react-markdown |
| Tests | pytest + SQLite test DB |

---

## Quick Start

### 1. Local development (without Docker)

```bash
cd /Users/mainadmin/churn_mvp/drug_reference_mvp

# Install backend deps
python3 -m pip install -r backend/requirements.txt

# Copy env
cp .env.example .env
# Edit .env to add your ANTHROPIC_API_KEY, etc.

# (Optional) start postgres + redis via docker-compose
docker-compose up -d postgres redis

# Ingest content into vector store + database
python3 -m scripts.ingest_content --reset

# Run the API
uvicorn backend.main:app --reload --port 8005

# In another terminal — frontend
cd frontend
npm install
npm run dev    # http://localhost:3005
```

### 2. Full stack via Docker

```bash
docker-compose up --build
```

---

## API

Visit `http://localhost:8005/docs` for interactive Swagger UI.

### Auth flow

```bash
# Signup
curl -X POST http://localhost:8005/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@pharm.com","password":"supersecure123","organization_name":"Riverside Pharmacy"}'

# Ask a query (JWT)
curl -X POST http://localhost:8005/api/v1/query \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the renal dosing for metformin?"}'

# Or with API key
curl -X POST http://localhost:8005/api/v1/query \
  -H "X-API-Key: apha_<your-key>" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the renal dosing for metformin?"}'
```

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/signup` | Create user + trial subscription |
| `POST /api/v1/auth/login` | Issue JWT |
| `GET /api/v1/auth/me` | Current user |
| `POST /api/v1/auth/api-keys` | Create API key |
| `GET /api/v1/auth/api-keys` | List user's API keys |
| `DELETE /api/v1/auth/api-keys/{id}` | Revoke key |
| `POST /api/v1/query` | Ask a clinical question (RAG + Claude) |
| `POST /api/v1/query/feedback` | Submit thumbs up/down |
| `GET /api/v1/query/history` | Recent queries |
| `GET /api/v1/subscriptions/plans` | Available plans |
| `GET /api/v1/subscriptions/me` | Current subscription |
| `POST /api/v1/subscriptions/checkout` | Stripe checkout session |
| `POST /api/v1/subscriptions/cancel` | Cancel at period end |
| `POST /api/v1/webhooks/stripe` | Stripe webhook handler |
| `GET /api/v1/analytics/usage` | Usage stats (30-day default) |

---

## Plans

| Plan | Price/mo | Queries/mo | Seats | Rate limit | API |
|------|---------|-----------|-------|-----------|-----|
| Trial | $0 | 10 | 1 | 2/min | ❌ |
| Individual | $99 | 500 | 1 | 10/min | ❌ |
| Team | $299 | 2,500 | 10 | 30/min | ✅ |
| Institution | $799 | 15,000 | 50 | 120/min | ✅ |
| Enterprise | Custom | Custom | Custom | 1000/min | ✅ |

Create Stripe products and prices:

```bash
STRIPE_SECRET_KEY=sk_test_... python3 -m scripts.create_stripe_products
# Copy the price IDs into .env
```

---

## Content Library

`content/` directory contains 12 curated markdown files:

- **Drug monographs (5):** metformin, lisinopril, atorvastatin, warfarin, amoxicillin, sertraline
- **Clinical guidelines (4):** diabetes_management, hypertension_guidelines, anticoagulation_therapy, pain_management
- **Pharmacy practice (3):** drug_interactions, medication_safety, patient_counseling

To add content: drop new `.md` files into the appropriate `content/<category>/` directory and re-run `python3 -m scripts.ingest_content --reset`.

---

## Testing

```bash
python3 -m pytest tests/
```

All tests use SQLite in-memory DB and disable Anthropic so they run offline (deterministic fallback paths). 23 tests cover:

- RAG ingestion + retrieval end-to-end
- Clinical assistant safety guardrails and fallback behavior
- Auth signup/login/JWT/API-key flows
- Query → log → feedback flow
- Plan definitions, Stripe mock checkout, webhook event parsing
- Rate limiter quota enforcement

---

## Project Layout

```
drug_reference_mvp/
├── backend/
│   ├── ai/              # Claude clinical assistant, prompts, safety, citations
│   ├── api/             # FastAPI routes, schemas, deps
│   ├── billing/         # Stripe client, plan definitions
│   ├── db/              # SQLAlchemy models, session
│   ├── rag/             # Vector store + retriever + ingestion pipeline
│   ├── rate_limiter/    # Redis sliding-window limiter
│   ├── utils/           # Config, logger
│   └── main.py
├── content/             # APhA clinical reference markdown (12 files)
├── frontend/            # React + Vite + Tailwind app
├── scripts/             # ingest_content.py, create_stripe_products.py
├── tests/               # pytest suite (23 tests)
├── docker-compose.yml
└── README.md
```

---

## Safety & Disclaimers

- **Not a substitute for clinical judgment.** The assistant produces reference information for licensed pharmacists; final patient-specific decisions remain with the clinician.
- **Built-in safety guardrails** block patient-specific dosing requests, diversion-pattern queries, and harm-related prompts.
- **All citations grounded in the retrieved corpus** — the LLM is instructed to refuse to fabricate references.

---

## License

Demo / proprietary. Not affiliated with the American Pharmacists Association in this MVP build.
