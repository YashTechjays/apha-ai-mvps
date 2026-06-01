# APhA RFP Knowledge Graph — New AI Features Guide

> **Audience:** Manager / stakeholder demo
> **Scope:** The 5 new AI capabilities layered on top of the existing crawl → match → proposal pipeline
> **URLs:** Frontend `http://localhost:3009` · API `http://localhost:8009` · Neo4j `http://localhost:7474`

---

## The 30-Second Pitch

The original product **found** pharmacy RFPs and **matched** them to a pharmacist. These 5 new features make the product *proactive and strategic*: it now **predicts** RFPs before they're posted, **stress-tests** a proposal like a review committee, **answers questions** conversationally, **assembles winning teams**, and lets a pharmacist **simulate** how a single career move changes their odds.

| # | Feature | One-line value |
|---|---------|----------------|
| 1 | **Foresight** | Predicts upcoming RFPs from each agency's historical posting rhythm |
| 2 | **Win Room** | An AI committee scores a proposal and auto-revises it until it wins |
| 3 | **Copilot** | A conversational agent that plans and acts across all the other tools |
| 4 | **Coalition Finder** | Assembles a complementary team that covers every RFP requirement |
| 5 | **Win-Probability Simulator** | Live "what-if" scoring of profile changes against a specific RFP |

**Design principles (every feature):** additive (nothing existing was removed), **graceful degradation** (each works fully offline with a deterministic fallback when no OpenAI key is set), **pure Cypher** (no Neo4j GDS plugin required), and **server-side identity** (the logged-in pharmacist is bound from the JWT — the client/LLM never supplies it).

---

## 1. Foresight — Predict RFPs Before They're Posted

### What we added
- `backend/ai/foresight.py` — mines every organization's historical `posted_date` cadence from the graph and projects the next expected posting window with a confidence score.
- API routes (`backend/api/routes/foresight.py`):
  - `GET /api/foresight/predictions` — all predicted upcoming RFPs
  - `GET /api/foresight/predictions/personalized` — same list, re-ranked by fit to the logged-in pharmacist
  - `GET /api/foresight/organization/{org_name}` — posting history + projected next window for one agency
- A **Foresight panel** on the Dashboard showing predicted opportunities with confidence, cadence, and fit %.

### How it works
1. Pull each org's sorted posting dates from Neo4j (`(Organization)<-[:POSTED_BY]-(RFP)`).
2. Compute the **median interval** between postings and a **regularity-based confidence** (low spread relative to the median ⇒ high confidence; more historical samples ⇒ more credit). Confidence is clamped to 5–99.
3. Project `next = last_posted + median_interval`, keep it if it lands between *today − 60 days* (recently due) and *today + horizon*.
4. Personalization attaches a `fit_score` (category overlap 70% + location match 30%) and re-ranks by `fit × confidence`.
5. The one-sentence rationale is LLM-generated, with a deterministic fallback sentence.

### Why / impact
Pharmacists currently react to RFPs after they appear — often with too little time to prepare. Foresight turns the graph's history into a **forward-looking radar**, letting a pharmacist line up certifications, partners, and a draft *before* the solicitation drops. That preparation lead time is the difference between a rushed bid and a winning one.

### Use case
> "MD Anderson-style oncology RFPs come out roughly every 12 months; the last was July 2025, so expect the next window around **May–Sep 2026**. Start prepping now."

### Recent hardening
A `min_cadence_days = 75` filter was added so duplicate/overlapping seed records can't produce nonsensical "~every 0.1 months" predictions. The fit score now normalizes state names so "Texas" correctly matches a "TX" profile.

---

## 2. Win Room — AI Evaluation Committee

### What we added
- `backend/ai/win_room.py` — an evaluate → revise → re-evaluate loop that scores a proposal against the RFP rubric, surfaces concrete gaps, and rewrites the proposal across rounds so the score climbs live.
- API route: `POST /api/rfps/{rfp_id}/win-room` (body optionally carries a `proposal`; otherwise a deliberately weak starter draft is used).
- A **Win Room modal** on the RFP detail page that animates the climbing score and shows each round's strengths/gaps.

### How it works
1. **Evaluate**: the committee scores the proposal 0–100 across five rubric sub-scores (requirements coverage, qualifications, approach, clarity, differentiation) and lists specific gaps.
2. **Revise**: if gaps remain and rounds are left, the proposal is rewritten to close them.
3. **Re-evaluate** and repeat (default `rounds=2`, `target_score=90`). A revision is never allowed to regress below the previous round (guards against LLM noise).
4. Returns every round so the UI can animate the climb, plus `final_score`, `final_proposal`, and `improvement`.
5. **Offline mode**: a deterministic heuristic scorer checks which RFP requirements (by keyword) actually appear in the text plus structural completeness; the reviser appends an explicit requirements-coverage section.

### Why / impact
A proposal usually only gets reviewed once — at submission, by the customer, when it's too late to fix. Win Room gives the pharmacist their **own review committee on demand**, exposing exactly which requirements aren't addressed and producing a stronger draft in seconds. It converts a black-box "submit and hope" into an iterative, score-driven improvement loop.

### Use case
> Paste (or auto-generate) a draft → committee scores it **30/100**, flags "no mention of REMS experience, no URAC accreditation, no concrete methodology" → auto-revises → **85** → **90**. The pharmacist downloads the final, committee-hardened proposal.

### Recent hardening
The Win Room now starts from a **deliberately thin** `weak_starter_draft` (a generic letter of interest) instead of the already-polished generated proposal, so the score visibly climbs (e.g. **30 → 85 → 90, +60**) rather than starting at 90 with no improvement to show.

---

## 3. Copilot — Conversational Agent

### What we added
- `backend/ai/copilot.py` — an OpenAI function-calling agent that plans and acts over the other features.
- API route: `POST /api/copilot/chat` (body `{ "message": "..." }`).
- A **Copilot page** (`/copilot` in the nav) with a chat interface that shows both the answer and the chain of tool calls it took.

### How it works
1. The LLM is given four tools and decides which to call: `search_rfps`, `predict_upcoming_rfps` (Foresight), `find_coalition`, `simulate_win_probability`.
2. A plan-and-act loop (max 5 turns) executes each chosen tool, feeds the result back, and continues until the model produces a final answer.
3. **Identity is injected server-side** — the caller's `user_id` and profile are bound into every tool call; the LLM never supplies them (so it can't impersonate another pharmacist).
4. Returns `{ answer, steps, used_llm }` — `steps` is the visible reasoning trail.
5. **Offline mode**: a deterministic keyword router maps the message to a single tool (predict vs. search) and formats the result.

### Why / impact
The other four features are powerful but each lives behind its own button. Copilot is the **single front door** — a pharmacist can ask a plain-English question and the agent orchestrates Foresight, Coalition, Simulator, and search to answer it. It lowers the learning curve to zero and makes the whole system feel like one assistant rather than five tools.

### Use case
> "What oncology RFPs are open, and what are my odds on the best one?" → Copilot calls `search_rfps('oncology', open)`, picks the top result, calls `simulate_win_probability(rfp_id)`, and replies with the RFP plus the pharmacist's win probability and the highest-impact lever — citing real org names and scores.

---

## 4. Coalition Finder — Build a Winning Team

### What we added
- `backend/ai/coalition.py` — assembles a complementary team of pharmacists that collectively covers an RFP's required specialties.
- API route: `GET /api/rfps/{rfp_id}/coalition?max_team_size=4`.
- A **"Find a Coalition"** button on the RFP detail page showing the team, who covers what, and overall coverage %.

### How it works
1. The RFP's `CATEGORIZED_AS` categories form the **requirement set** to cover.
2. Each candidate pharmacist covers the subset of those categories matching their `HAS_SPECIALTY` edges (pure Cypher read).
3. A **greedy set-cover** in Python repeatedly adds the pharmacist who closes the most still-open requirements, until everything is covered or the team hits `max_team_size`.
4. Returns the team (each member with the categories they `cover` + certifications), `covered_categories`, `uncovered_categories`, and `coverage_pct`.

### Why / impact
Big RFPs often demand a breadth of expertise no single pharmacist has (oncology *and* compliance *and* 340B). Coalition Finder reframes "I can't bid on this alone" into "here's the **3-person team** that covers 100% of it" — unlocking opportunities that would otherwise be skipped, and surfacing partnership/networking value from the graph.

### Use case
> An RFP needs oncology + specialty-pharmacy + patient-care + compliance. Coalition Finder returns a 3-pharmacist team: Dr. A covers oncology+specialty, Dr. B covers patient-care, Dr. C covers compliance → **100% coverage**.

---

## 5. Win-Probability Simulator — Interactive What-If Scoring

### What we added
- `backend/ai/simulator.py` — recomputes a pharmacist's win probability for an RFP when they toggle hypothetical profile changes (add a specialty, change location).
- API routes (`backend/api/routes/simulator.py`):
  - `GET /api/simulator/{rfp_id}/baseline` — current probability, factor breakdown, available toggles, and ranked **levers**
  - `POST /api/simulator/{rfp_id}` — recompute for a hypothetical profile (not persisted)
- A **Win-Probability Simulator** panel on the RFP detail page.

### How it works
1. Uses a **deterministic variant of the production matcher** so every toggle is instant and fully offline (no LLM/network per keystroke). The factor *weights* match the matcher so simulated odds line up with real matches:
   - Category overlap **40%** · Requirements/certs **35%** · Location **15%** · Org-type **10%**
2. `baseline()` returns the current score + a per-factor breakdown + the palette of toggleable specialties.
3. **Levers**: it ranks the highest-impact single changes the pharmacist could make (e.g. "+18% if you add oncology specialty"), showing only changes with a positive delta.
4. `simulate()` compares baseline odds to a hypothetical profile and returns the delta.

### Why / impact
Career-development advice is usually vague ("get more certifications"). The Simulator makes it **concrete and quantified** for a specific opportunity: it shows the exact percentage-point gain from each possible move, so a pharmacist can invest their time where it actually moves the needle.

### Use case
> Baseline win probability **47%** on an oncology RFP. Toggle "add oncology specialty" → jumps to **65%**. The lever list shows that's the single highest-impact change available.

### Recent hardening
Location scoring now normalizes full state names to codes ("Texas" ↔ "TX"), so the location factor scores correctly and the simulator no longer suggests an absurd "relocate to Texas" lever to a pharmacist who's *already* in Texas.

---

## End-to-End Demo Flow (recommended order, ~12 min)

> Log in as the demo pharmacist first (e.g. `pharmtest2 / pharmacy123`) so all features are personalized. First load warms the match cache (~20s).

### Part A — Foresight (Dashboard) · 2 min
1. Open `http://localhost:3009/` as the pharmacist.
2. Scroll to **"Foresight — Predicted Opportunities."**
3. Point at the top prediction: organization, **fit %**, **confidence %**, cadence ("Posts ~every 12 months; last 2025-07-12"), and the predicted window.
4. **Talking point:** *"This isn't a posted RFP yet — the system predicted it from the agency's history so the pharmacist can prepare months ahead."*

### Part B — Open an RFP & Simulate · 3 min
1. Click into a matched oncology RFP (e.g. *Specialty Oncology Pharmacy*).
2. Open the **Win-Probability Simulator** panel — show the baseline % and the factor breakdown (category/requirements/location/org-type).
3. Toggle **"add oncology specialty"** → watch the probability jump live.
4. **Talking point:** *"Every toggle recomputes instantly and offline, using the exact same weights as the real matcher — so these odds are trustworthy, not a toy."*

### Part C — Coalition Finder · 2 min
1. On the same RFP, click **"Find a Coalition."**
2. Show the assembled team, the categories each member covers, and the **coverage %**.
3. **Talking point:** *"No single pharmacist covers all of this — but here's the team that covers 100%. That's a bid that wouldn't otherwise happen."*

### Part D — Win Room · 3 min
1. On the same RFP, click **"Open Win Room."**
2. Watch the committee score the initial draft **(~30)**, list concrete gaps, and auto-revise: **30 → 85 → 90**.
3. Expand a round to show the strengths/gaps the committee called out.
4. Click **"Download Final Proposal."**
5. **Talking point:** *"The pharmacist gets their own review committee on demand — it tells them exactly what's missing and rewrites the proposal to fix it."*

### Part E — Copilot (ties it together) · 2 min
1. Go to **`/copilot`**.
2. Ask: *"What open oncology RFPs are there, and what are my odds on the best one?"*
3. Show the answer **and** the visible reasoning steps (search → simulate).
4. **Talking point:** *"Copilot is the single front door — it orchestrates all of these tools from one plain-English question, and it always acts as the logged-in pharmacist, never anyone else."*

---

## Demo Safety Net (key talking point)

Every feature **degrades gracefully**: with no OpenAI key, Foresight still predicts (deterministic rationale), Win Room still scores and revises (heuristic committee), Copilot still routes to a tool (keyword router), and Coalition + Simulator are *fully deterministic by design*. **The demo cannot break on a missing/expired API key.**

---

## API Quick Reference

| Feature | Method | Endpoint |
|---------|--------|----------|
| Foresight (all) | GET | `/api/foresight/predictions?horizon_days=180&limit=10` |
| Foresight (personalized) | GET | `/api/foresight/predictions/personalized` |
| Foresight (one org) | GET | `/api/foresight/organization/{org_name}` |
| Win Room | POST | `/api/rfps/{rfp_id}/win-room` |
| Copilot | POST | `/api/copilot/chat` |
| Coalition | GET | `/api/rfps/{rfp_id}/coalition?max_team_size=4` |
| Simulator (baseline) | GET | `/api/simulator/{rfp_id}/baseline` |
| Simulator (what-if) | POST | `/api/simulator/{rfp_id}` |

All endpoints require a valid JWT; the pharmacist identity is read server-side from the token.

---

## Pre-Demo Checklist

- [ ] Containers running: `docker compose ps` in `rfp_knowledge_graph/`
- [ ] API health: `http://localhost:8009/health` → `{"status":"ok"}`
- [ ] Graph seeded with clean cadence data (Foresight shows realistic 8–12 month cadences, no "0.1 month" noise)
- [ ] Logged in as a pharmacist with specialties + location set (drives Foresight fit, Simulator, Coalition)
- [ ] Pick one oncology RFP up front to use for Simulator → Coalition → Win Room in sequence
