# APhA AI Membership Concierge

A 24/7 AI-powered chat widget embedded on the APhA website that answers membership questions, recommends the right tier, captures leads, and guides visitors into the join/renew flow.

**Built by**: Techjays AI Team

## Quick Start

```bash
cd churn_mvp/concierge

# 1. Add your Anthropic API key
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# 2. Start services
docker-compose up --build -d

# 3. Build the RAG knowledge base (first time only)
docker-compose exec backend python scripts/ingest_knowledge_base.py

# 4. Verify health
curl http://localhost:8001/health

# 5. Open the demo page
open http://localhost:3001
# Click the 💬 button — bottom right corner

# 6. View analytics
open http://localhost:3001/analytics
```

## Architecture

| Layer | Technology |
|---|---|
| API | FastAPI + Python 3.11 |
| LLM | Anthropic Claude (claude-sonnet-4-20250514) |
| RAG | LangChain + ChromaDB + sentence-transformers |
| Database | PostgreSQL via SQLAlchemy 2.0 |
| Frontend | React 18 + TailwindCSS |
| CRM | Personify mock connector |
| Email | HubSpot mock connector |

## Key Flows

1. **Visitor opens widget** → greeted by AI concierge
2. **Visitor asks a question** → intent detected → RAG retrieves relevant KB chunks → Claude generates response
3. **After 3 turns** → AI politely asks for email → lead captured → pushed to CRM + email sequence triggered
4. **Tier recommended** → TierCard shown → "Join Now" button links to pharmacist.com/join
5. **All conversations logged** → analytics dashboard tracks intents, tiers, lead rate

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/chat/` | Send a message, get AI response |
| GET | `/chat/session/{token}` | Get full conversation history |
| POST | `/leads/` | Capture visitor email/name |
| GET | `/leads/` | List all captured leads |
| GET | `/analytics/summary` | Conversation + lead metrics |

## Running Tests

```bash
docker-compose exec backend pytest tests/ -v
```

## Production Checklist

- [ ] Set real `ANTHROPIC_API_KEY`
- [ ] Replace `crm_connector.py` mock with real Personify API
- [ ] Replace `email_connector.py` mock with real HubSpot API
- [ ] Point `DATABASE_URL` to production RDS
- [ ] Run `ingest_knowledge_base.py` after any KB content updates
- [ ] Embed `ChatWidget` on pharmacist.com membership pages
