# APhA AI MVP Suite - Technical Overview

A suite of 6 AI-powered MVPs designed to improve member acquisition, engagement, retention, and revenue for the American Pharmacists Association (APhA).

---

## Summary

| MVP | Purpose | AI/ML | Backend Port | Frontend Port | DB Port |
|-----|---------|-------|-------------|--------------|---------|
| Churn Prediction | Predict member churn risk | XGBoost + SHAP | 8000 | 3000 | 5432 |
| Membership Concierge | Chat widget for membership Q&A | OpenAI + RAG | 8001 | 3001 | 5433 |
| Personalized Value Email | Monthly ROI emails to members | OpenAI | 8002 | 3002 | 5434 |
| CPE Gap Calculator | CPE gap analysis for renewal | OpenAI | 8003 | 3003 | 5435 |
| Cross-Sell Engine | Product expansion scoring | XGBoost (5 models) | 8004 | 3004 | 5436 |
| Drug Reference Tool | Clinical drug Q&A (B2B SaaS) | OpenAI + RAG | 8005 | 3005 | 5437 |

**Shared stack across all MVPs:** FastAPI + SQLAlchemy + PostgreSQL (backend), React 18 + TailwindCSS (frontend), Docker Compose (infra).

---

## 1. Churn Prediction API

**Location:** `/backend/` + `/frontend/` (root-level project)

### What It Does
ML-powered member churn prediction system that identifies at-risk members using behavioral signals, enabling the retention team to intervene before members lapse.

### Key Features
- 25-feature XGBoost model analyzing login recency, CPE hours, email engagement, event attendance, renewal history
- 4-tier risk classification: Critical (85-100), High (70-84), Medium (50-69), Low (0-49)
- SHAP-based explainability showing top 3 risk factors per member
- Weekly batch scoring pipeline
- Alert system for critical/high-risk members
- React dashboard with KPI cards, risk distribution charts, sortable member table

### Technical Architecture

```
User -> React Dashboard -> FastAPI Backend -> PostgreSQL
                                |
                          XGBoost Model
                                |
                          SHAP Explainer
                                |
                           MLflow Tracking
```

**ML Pipeline:**
1. 200 mock members seeded on startup with 25+ behavioral features
2. Feature extraction: login days, CPE hours (90d/YTD), email open/click rates, event attendance, publication access
3. XGBoost model predicts churn probability (0-100)
4. SHAP values computed per prediction for explainability
5. Batch scoring writes `ChurnScore` + `Alert` records to PostgreSQL

**API Endpoints:**
- `POST /auth/login` - JWT authentication
- `GET /members/` - All members with latest scores
- `GET /members/{id}` - Member detail + churn score
- `POST /scores/run` - Trigger batch scoring
- `GET /scores/distribution` - Risk tier distribution
- `GET /scores/member/{id}/explain` - SHAP explanation
- `GET /alerts/` - Active alerts
- `PATCH /alerts/{id}` - Resolve alert with outcome

**Tech:** XGBoost, SHAP, scikit-learn, MLflow, JWT auth, Alembic migrations

---

## 2. Membership Concierge (Chat Widget)

**Location:** `/concierge/`

### What It Does
24/7 AI-powered chat widget for the APhA website that answers membership questions, recommends tiers, captures leads, and drives signups using RAG over APhA knowledge base content.

### Key Features
- Intent detection: join, renew, benefits, membership tiers, off-topic
- RAG retrieval using ChromaDB vector store over APhA knowledge base
- Tier recommendations: Student, New Practitioner, Pharmacist, Technician, Researcher
- Lead capture after 3 conversation turns
- Conversation tracking with intent logging
- Analytics dashboard showing conversations, lead rate, intent distribution

### Technical Architecture

```
Visitor -> Chat Widget (React) -> FastAPI Backend -> OpenAI (gpt-4o-mini)
                                       |                    ^
                                  PostgreSQL          ChromaDB (RAG)
                                       |                    |
                                  Conversations      Knowledge Base
                                  + Leads            (markdown files)
```

**Data Flow:**
1. Visitor opens chat widget, session token generated
2. Message sent to `/chat/` with session token
3. Intent detected from user message
4. ChromaDB retrieves top-4 relevant knowledge base chunks via similarity search
5. OpenAI generates response with system prompt (context + turn count + intent)
6. Tier recommendation keywords parsed from response
7. After 3 turns, lead capture prompt injected
8. All messages persisted to PostgreSQL

**API Endpoints:**
- `POST /chat/` - Send message, get AI response
- `GET /chat/session/{session_token}` - Full conversation history
- `POST /leads/` - Capture visitor email/name
- `GET /leads/` - List captured leads
- `GET /analytics/summary` - Conversation + lead metrics

**Tech:** LangChain, ChromaDB, sentence-transformers, OpenAI

---

## 3. Personalized Member Value Email

**Location:** `/email_mvp/`

### What It Does
Generates monthly AI-personalized emails showing each member their exact benefit usage and dollar value, making membership ROI tangible to increase renewal rates.

### Key Features
- Benefit valuation: CPE credits ($25 each), webinars ($50), journal articles ($3), PharmacyLibrary ($5), events ($25-350)
- ETL pipeline syncing member activity from mock LMS, CRM, events, publications connectors
- AI-generated personalized email content with member name, benefit highlights, ROI
- Jinja2 HTML rendering with member data + dollar figures
- 6-point QC engine: subject line length, member name, dollar figures count, spam word check, CTA presence, token limit
- SendGrid webhook tracking (opens, clicks, bounces, unsubscribes)
- Monthly batch scheduling via APScheduler

### Technical Architecture

```
APScheduler (monthly) -> ETL Pipeline -> Benefit Calculator -> OpenAI
                              |                                   |
                         Mock Connectors                    Email Content
                         (LMS, CRM, Events)                      |
                                                           QC Engine (6 checks)
                                                                 |
                                                           Jinja2 Renderer
                                                                 |
                                                        SendGrid (mocked in dev)
                                                                 |
                                                           PostgreSQL
                                                           (EmailSend + Events)
```

**Data Flow:**
1. APScheduler triggers monthly job on day 1
2. ETL syncs member activity from mock connectors
3. Per member: benefit summary computed, dollar value calculated, ROI multiplier derived
4. OpenAI generates personalized email with highlights + CTA
5. 6-point QC check validates email quality
6. Jinja2 renders HTML email from template
7. SendGrid sends (mocked in dev)
8. SendGrid webhooks update open/click/bounce/unsubscribe metrics

**API Endpoints:**
- `GET /emails/` - List email sends (filterable by month, status)
- `GET /emails/member/{member_id}` - Member email history
- `GET /emails/preview/{member_id}` - AI-generated preview (no send)
- `POST /emails/send/{member_id}` - Send single email
- `POST /emails/run-batch?send_month=2026-05` - Batch send for month
- `POST /emails/webhook/sendgrid` - SendGrid event webhook
- `GET /analytics/summary` - Monthly engagement metrics

**Tech:** APScheduler, Jinja2, SendGrid, OpenAI

---

## 4. CPE Gap Calculator

**Location:** `/cpe_calculator/`

### What It Does
Free public-facing tool that helps pharmacists calculate their CPE (Continuing Pharmacy Education) gap for license renewal. Acts as a top-of-funnel acquisition tool, gating the full plan behind an email capture to drive membership signups.

### Key Features
- State requirements database covering all 50 states + DC (hours required, cycle years, mandatory topics)
- Course catalog of ~60 APhA ACPE-accredited courses with CPE hours, pricing, topics
- AI-powered 3-course preview plan prioritizing mandatory topics
- Deterministic fallback when API is unavailable
- Email gate: 3 preview courses visible, 2 "locked" cards requiring email to unlock
- Membership upsell showing member vs non-member pricing
- Per-state SEO meta tags for 51 landing pages

### Technical Architecture

```
Pharmacist -> React Frontend -> FastAPI Backend -> State Requirements DB (JSON)
                                     |                      |
                                     |                Course Catalog (JSON)
                                     |                      |
                                     +-------> OpenAI (plan generation)
                                     |              |
                                     |        Deterministic Fallback
                                     |
                                PostgreSQL          SendGrid (mocked)
                                (Calculations       (Nurture sequence)
                                 + Leads)
```

**Data Flow:**
1. User selects state, fills renewal date, hours completed, license type, specialty
2. Backend looks up state-specific CPE requirements
3. Calculates `hours_gap = hours_required - hours_completed`
4. Filters course catalog by license type + specialty
5. Sorts by mandatory topics first
6. OpenAI selects optimal courses with strict JSON schema (deterministic fallback available)
7. Returns 3-course preview + 2 locked cards
8. User clicks "Unlock" -> email capture modal
9. Lead saved -> SendGrid nurture triggered (mocked) -> full plan unlocked

**API Endpoints:**
- `POST /calculate/` - Generate 3-course preview plan
- `GET /calculate/full/{id}?session_id=...` - Full plan (lead-gated)
- `POST /leads/` - Capture email, unlock plan
- `GET /analytics/summary` - Calculation count, lead conversion, top states
- `GET /seo/state/{code}` - SEO meta payload per state

**Tech:** OpenAI, SendGrid, JSON-based state/course data

---

## 5. AI Cross-Sell Engine

**Location:** `/crosssell_mvp/`

### What It Does
AI engine that scores every member's expansion potential across 5 product streams (Education, Publications, Events, Career, Advocacy) and fires personalized nudges to grow products-per-member.

### Key Features
- 5 XGBoost models (22 features each), one per product stream
- Suppression rules: score >= 60 to nudge, skip if already active, max 2/month, 14-day cooldown, defer if churn >= 90
- Channel routing: score >= 80 -> email, 60-79 -> in-portal banner
- AI-generated personalized copy (email subject/body, banner headline/body)
- Celery background task processing with Redis queue
- Churn score integration (suppresses high-churn members)
- Analytics with conversion tracking and nudge history

### Technical Architecture

```
Batch Trigger -> 5x XGBoost Models -> Suppression Rules -> Channel Router
                      |                                         |
                 150 Mock Members                    +----------+----------+
                 (25+ features)                      |                     |
                                                Email (>=80)        Banner (60-79)
                                                     |                     |
                                               OpenAI (copy)        OpenAI (copy)
                                                     |                     |
                                               Celery Worker         Portal API
                                               (SendGrid mock)            |
                                                     |              React Dashboard
                                                PostgreSQL
                                          (Scores, Nudges, Conversions)
```

**Data Flow:**
1. Batch scoring triggered via API or schedule
2. Loads 150 mock members with 25+ usage fields
3. Per product stream (education, publications, events, career, advocacy):
   - Extracts 22 features (tenure, tier, engagement, product usage, churn score, etc.)
   - XGBoost predicts expansion probability
   - Suppression check: already active? recently nudged? high churn?
   - Generates top 3 contextual reasons
4. Router applies suppression rules, routes to email or banner channel
5. OpenAI generates personalized copy (deterministic fallback available)
6. Celery worker delivers emails (mocked)
7. Dashboard displays member profiles with top opportunity + all product scores

**API Endpoints:**
- `POST /scores/run` - Trigger batch scoring
- `GET /scores/members` - Member expansion profiles
- `GET /scores/member/{id}` - Product scores for single member
- `GET /nudges/active` - Active nudges for member
- `GET /banners/{member_id}` - Best banner for portal integration
- `POST /nudges/send` - Trigger email nudge

**Tech:** XGBoost, MLflow, Celery, Redis, OpenAI, JWT auth

---

## 6. AI Drug Reference Tool (B2B SaaS)

**Location:** `/drug_reference_mvp/`

### What It Does
Retrieval-augmented clinical drug reference SaaS for licensed pharmacists. Answers natural-language clinical questions with cited answers grounded in APhA content. B2B subscription model with Stripe billing.

### Key Features
- RAG over 12 markdown files (drug monographs, clinical guidelines, pharmacy practice)
- Clinical safety guardrails blocking patient-specific dosing, diversion-pattern, and harm-related queries
- Citation system: every answer cited with source chunks
- Tiered rate limiting via Redis sliding-window limiter
- 5 subscription tiers: Trial ($0), Individual ($99), Team ($299), Institution ($799), Enterprise (custom)
- API key access for Team+ plans
- Query classification (clinical, formulary, pricing, safety, educational)
- Stripe Checkout + webhook integration for billing
- Deterministic fallback when API is unavailable

### Technical Architecture

```
Pharmacist -> React Frontend -> FastAPI Backend -> Safety Check
                                     |                  |
                                  JWT Auth         Query Classifier
                                     |                  |
                                Rate Limiter       ChromaDB (RAG)
                                  (Redis)               |
                                     |            Top-K Chunks + Citations
                                     |                  |
                                     +-------> OpenAI (answer generation)
                                     |                  |
                                PostgreSQL        Deterministic Fallback
                                (Users, Subs,
                                 QueryLogs)
                                     |
                                Stripe (billing)
```

**Data Flow:**
1. User signs up -> trial subscription created
2. User asks clinical question to `/api/v1/query`
3. Safety check blocks patient-specific or harm-related queries
4. Query classified (clinical, formulary, etc.)
5. ChromaDB retrieves top-k chunks with diversity filtering
6. Citations built from retrieved chunks
7. OpenAI generates grounded answer with system prompt
8. Deterministic fallback if API unavailable
9. QueryLog persisted with query text, answer, latency, safety flags
10. Subscription quota decremented

**API Endpoints:**
- `POST /api/v1/auth/signup` - Create user + trial subscription
- `POST /api/v1/auth/login` - Issue JWT
- `POST /api/v1/auth/api-keys` - Create API key (Team+ plans)
- `POST /api/v1/query` - Ask clinical question
- `POST /api/v1/query/feedback` - Thumbs up/down on answer
- `GET /api/v1/query/history` - Recent queries
- `GET /api/v1/subscriptions/plans` - Available plans
- `POST /api/v1/subscriptions/checkout` - Stripe checkout session
- `POST /api/v1/webhooks/stripe` - Stripe webhook handler
- `GET /api/v1/analytics/usage` - 30-day usage stats

**Subscription Tiers:**

| Plan | Price | Queries/Month | Rate Limit | API Access |
|------|-------|--------------|------------|------------|
| Trial | $0 | 10 | 2/min | No |
| Individual | $99 | 500 | 10/min | No |
| Team | $299 | 2,500 | 30/min | Yes |
| Institution | $799 | 15,000 | 120/min | Yes |
| Enterprise | Custom | Unlimited | 1,000/min | Yes |

**Tech:** ChromaDB, sentence-transformers (all-MiniLM-L6-v2), LangChain, Stripe, Redis, bcrypt

---

## Running Any MVP

Each MVP runs independently via Docker Compose:

```bash
cd <mvp_directory>
docker compose up --build
```

All MVPs follow the same pattern:
- **Backend** on `localhost:<backend_port>` (FastAPI with auto-docs at `/docs`)
- **Frontend** on `localhost:<frontend_port>` (React + Vite dev server)
- **Database** on `localhost:<db_port>` (PostgreSQL, auto-migrated on startup)
