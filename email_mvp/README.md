# APhA Personalized Member Value Email MVP

Monthly AI-generated emails showing each APhA member their exact benefit usage and dollar value — built to increase renewal rates by making membership ROI tangible.

## Architecture

```
email_mvp/
├── backend/
│   ├── ai/                  # Benefit valuation + Claude-powered email generation
│   ├── api/                 # FastAPI routes: members, emails, analytics
│   ├── db/                  # SQLAlchemy models: Member, EmailSend, EmailEvent
│   ├── email_delivery/      # Jinja2 renderer, QC engine, SendGrid client
│   ├── pipeline/            # ETL connectors (LMS, CRM, events, publications)
│   ├── scheduler/           # Monthly batch job orchestrator
│   └── utils/               # Config, logger, seed data
└── frontend/                # React 18 + TailwindCSS dashboard
```

## Quick Start

```bash
cd churn_mvp/email_mvp

# Copy and configure environment
cp .env.example .env
# Set ANTHROPIC_API_KEY (required for email generation)
# Set SENDGRID_API_KEY (optional — mocked in development)

# Start all services
docker-compose up --build

# Backend:  http://localhost:8002
# Frontend: http://localhost:3002
# API docs: http://localhost:8002/docs
```

## Key Flows

### Monthly Email Batch
```
POST /emails/run-batch?send_month=2026-05
```
1. ETL syncs all member activity from mock connectors
2. Computes benefit dollar values per member
3. Calls Claude (`claude-sonnet-4-20250514`) to generate personalized content
4. Renders HTML via Jinja2 template
5. Runs 6-point QC check (personalization, spam, dollar figures, CTA, length)
6. Sends via SendGrid (or mocks in development)

### Per-Member Preview
```
GET /emails/preview/{member_id}
```
Returns the AI-generated HTML email for a member without sending it.

### SendGrid Webhook
```
POST /emails/webhook/sendgrid
```
Accepts SendGrid event payloads (open, click, bounce, unsubscribe) and updates `EmailSend` engagement fields.

## Benefit Valuation Logic

| Benefit | Value |
|---------|-------|
| CPE credit | $25/credit |
| Webinar | $50/session |
| Journal article | $3/article |
| PharmacyLibrary session | $5/session |
| Annual Meeting | $350 |
| Other events | $25/event |

## QC Checks (6-point scoring)

1. Subject line 20–60 characters
2. Member first name present in body
3. ≥3 dollar figures in body
4. No spam trigger words
5. CTA present
6. Token count within limit

Email must score ≥ 0.7 **and** pass name + spam checks to be sent.

## Running Tests

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. pytest ../tests/ -v
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `ANTHROPIC_API_KEY` | — | Required for email generation |
| `SENDGRID_API_KEY` | — | Optional; mocked when empty |
| `ENV` | `development` | Set to `production` to enable real sends |
| `PILOT_BATCH_SIZE` | `50` | Members per batch run |
| `MAX_TOKENS_PER_EMAIL` | `500` | Claude token limit per email |
| `EMAIL_SEND_DAY` | `1` | Day of month for scheduled send |
