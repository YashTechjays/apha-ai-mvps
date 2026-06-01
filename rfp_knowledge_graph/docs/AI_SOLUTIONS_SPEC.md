# APhA RFP Knowledge Graph — AI Solutions Suite (5 Features)

Full phased specs for five flagship AI features. All are **additive** and reuse the
existing engine:

- Graph access: `backend/graph/neo4j_client.get_session`, `backend/graph/queries.py`,
  `backend/graph/pharmacist_graph.py`
- Scoring: `backend/ai/matcher.score_rfp_for_profile(rfp, profile, user_id)`,
  `backend/ai/graph_features.history_score`
- Generation/context: `backend/ai/proposal_generator.py`, `backend/ai/graph_rag.gather_proposal_context`
- Auth: `get_current_user` (JWT payload), `get_current_pharmacist` (`User` ORM)

> **Graph data already present:** `(Pharmacist {user_id, full_name, location_state})`
> with `-[:HAS_SPECIALTY]->(Category)`, `-[:HOLDS]->(Certification)`,
> `-[:APPLIED_TO {status}]->(RFP)`. RFPs carry `posted_date`, `deadline`, `status`,
> `budget_range` and connect to `Organization`, `Location`, `Category`, `Requirement`.

---

## The Five Features

| # | Feature | One-liner | Builds on |
|---|---------|-----------|-----------|
| 1 | **Foresight** | Predicts RFPs *before* they're posted, from repost cadence | `posted_date` history |
| 2 | **Win Room** | AI committee scores + auto-revises a proposal, score climbs live | proposal gen + GraphRAG |
| 3 | **Copilot** | Conversational agent that plans & acts over the graph | all graph/AI functions as tools |
| 4 | **Coalition Finder** | Graph assembles a complementary team to cover RFP gaps | `HAS_SPECIALTY`/`HOLDS` edges |
| 5 | **Win-Probability Simulator** | What-if sliders recompute win odds live | `matcher` + `graph_features` |

### Recommended build order & dependency graph
```
Shared Demo Seed (Phase 0) ─┬─→ #1 Foresight        (needs multi-year RFP history)
                            ├─→ #4 Coalition Finder  (needs several pharmacist profiles)
                            └─→ #5 Simulator         (needs application/win history)
#2 Win Room   → independent (reuses proposal gen)
#3 Copilot    → build LAST (wraps #1, #4, #5 as agent tools for max effect)
```

---

# FEATURE 1 — FORESIGHT

**Concept:** Agencies re-bid on cycles. Mine each organization's `posted_date` history,
compute the median interval, and project the next posting window with a confidence score.
*"Mississippi Medicaid posts a PBM RFP ~every 18 months; last Feb 2024 → expect ~Aug 2025.
You're an 84% fit."*

> Full detail in `FORESIGHT_WINROOM_SPEC.md`. Condensed plan:

### Phase 1.1 — Backend
- **New `backend/ai/foresight.py`:**
  - `_org_posting_history()` — Cypher: per `Organization`, collect `r.posted_date`,
    `r.deadline`, categories, last RFP id/title.
  - `_cadence(dates)` — median interval + coefficient of variation (need ≥2 dates).
  - `forecast_reposts(horizon_days=180, min_history=2)` → predictions with
    `predicted_window_start/end`, `confidence` (0-100), `cadence_months`, `basis`,
    `last_rfp_id/title`.
  - `personalize_predictions(predictions, profile)` — add `fit_score` via category/state overlap.
  - `explain_prediction(pred)` *(optional)* — 1-sentence LLM rationale w/ deterministic fallback.
- **New `backend/api/routes/foresight.py`:** `GET /api/foresight/predictions`,
  `/predictions/personalized` (pharmacist), `/organization/{name}` (cadence timeline).
- **Edit `backend/main.py`:** import + `app.include_router(foresight.router)`.

### Phase 1.2 — Frontend
- **Edit `frontend/src/api/client.js`:** `foresightApi { predictions, personalized, organization }`.
- **New `frontend/src/components/PredictedOpportunities.jsx`:** org+category, predicted
  window, confidence bar, `basis` sentence, fit % badge, "Based on" link.
- **Edit `frontend/src/pages/DashboardPage.jsx`:** load + render the section at the **top**.

**Files:** 2 new + 3 edits. **Depends on:** Phase 0 seed for credible demo.

---

# FEATURE 2 — WIN ROOM

**Concept:** Draft (via GraphRAG) → AI "evaluation committee" scores against the RFP rubric
and lists gaps → auto-revise → repeat. Score climbs **64 → 78 → 91** live.

> Full detail in `FORESIGHT_WINROOM_SPEC.md`. Condensed plan:

### Phase 2.1 — Backend
- **Edit `backend/ai/prompts.py`:** `PROPOSAL_EVALUATION_SYSTEM/USER` (strict-JSON committee
  scorer), `PROPOSAL_IMPROVEMENT_SYSTEM/USER`.
- **New `backend/ai/win_room.py`:**
  - `build_rubric(rfp)` — weighted criteria (Responsiveness 30, Qualifications 25,
    Technical 25, Compliance 10, Clarity 10).
  - `evaluate_proposal(text, rfp, rubric)` → `{overall, criteria[], gaps[]}` (JSON parse +
    deterministic keyword-coverage fallback).
  - `improve_proposal(text, rfp, profile, evaluation)` — revise to close gaps.
  - `run_win_room(rfp, profile, username, context, rounds=3)` — round 0 = existing
    `generate_proposal`; loop evaluate→improve; early-stop when gain < 3. Returns full
    round timeline + `final_proposal/final_score`.
- **Edit `backend/api/routes/rfps.py`:** `POST /{rfp_id}/win-room` (reuse profile/context assembly).

### Phase 2.2 — Frontend
- **Edit `client.js`:** `rfpApi.winRoom(id, rounds)`.
- **New `frontend/src/components/WinRoomModal.jsx`:** animated score gauge, per-criterion
  bars, "fixes applied this round" list, final proposal with Copy/Download/Save.
- **Edit `frontend/src/pages/RfpDetailPage.jsx`:** "Win Room" button beside "Generate Proposal".

**Files:** 1 new module + 1 component + 3 edits. **Depends on:** nothing (independent).

---

# FEATURE 3 — COPILOT (agent over the graph)

**Concept:** A chat box where a pharmacist types *"Find RFPs in Texas I can win for MTM and
draft the best one."* An OpenAI **function-calling agent** plans and executes multi-step over
the existing graph/AI functions, returns the answer plus the **reasoning steps** (which tools
it called) so the UI can show it "thinking."

### Phase 3.1 — Backend
- **New `backend/ai/copilot.py`:**
  - `TOOLS` — OpenAI tool/function schemas wrapping existing functions:
    | Tool name | Backing function |
    |-----------|------------------|
    | `search_rfps` | `queries.search_rfps` |
    | `recommend_matches` | `matcher.score_rfp_for_profile` over `queries.get_rfps_for_matching` |
    | `similar_rfps` | `queries.get_semantically_similar_rfps` |
    | `peer_recommendations` | `pharmacist_graph.get_peer_recommendations` |
    | `forecast_opportunities` | `foresight.forecast_reposts` (Feature 1) |
    | `find_coalition` | `coalition.find_coalition` (Feature 4) |
    | `simulate_profile_change` | `win_simulator.simulate` (Feature 5) |
    | `draft_proposal` | `graph_rag.gather_proposal_context` + `proposal_generator.generate_proposal` |
    | `explain_match` | `explainer.explain_match` |
  - `DISPATCH = {name: callable}` — maps tool name → bound function (injects `user_id`/profile
    server-side; the model never supplies identity).
  - `run_copilot(message, history, user, profile, max_steps=5) -> dict`
    Loop: `chat.completions.create(model, messages, tools=TOOLS, tool_choice="auto")`; if the
    response has `tool_calls`, execute each via `DISPATCH`, append tool results, repeat until a
    final text answer or `max_steps`. Capture every step.
    Returns:
    ```python
    {
      "reply": "markdown answer",
      "steps": [{"tool": "search_rfps", "args": {...}, "summary": "found 6 RFPs"}],
      "cited_rfps": [{"id","title","organization_name","match_score?"}]
    }
    ```
- **New `backend/api/routes/copilot.py`:**
  ```python
  router = APIRouter(prefix="/api/copilot", tags=["copilot"])

  class ChatBody(BaseModel):
      message: str
      history: list[dict] = []     # [{role, content}]

  @router.post("/chat")
  def chat(body: ChatBody, user=Depends(get_current_pharmacist), db=Depends(get_db)):
      profile_dict = {...}         # same shape used in matches.py
      return run_copilot(body.message, body.history, user, profile_dict)
  ```
- **Edit `backend/main.py`:** register `copilot.router`.
- **Safety:** server injects identity; tools are read-mostly. `draft_proposal` returns text
  only (no DB writes). Cap `max_steps` to bound cost/latency.

### Phase 3.2 — Frontend
- **Edit `client.js`:** `copilotApi = { chat: (message, history) => api.post('/api/copilot/chat', { message, history }) }`.
- **New `frontend/src/pages/CopilotPage.jsx`:** chat transcript; while waiting, render the
  returned **`steps`** as a "reasoning trace" (e.g. *"Searching RFPs → Scoring matches →
  Drafting proposal"*); render `cited_rfps` as inline `RfpCard`s; markdown answer bubble.
- **Edit `frontend/src/App.jsx`:** add `import CopilotPage`, nav entry `{ path: '/copilot',
  label: 'Copilot' }` (both nav arrays), and `<Route path="/copilot" element={<CopilotPage/>}/>`.

### Phase 3.3 — Polish (optional)
- **Streaming** via SSE so steps appear live.
- **Live graph highlight:** return touched node ids; light them up in a `react-force-graph-2d`
  panel beside the chat (the "watch it reason on the graph" moment).

**Files:** 2 new + 2 edits (+ optional graph panel). **Depends on:** strongest when #1/#4/#5
exist (more tools = more impressive); works with a subset.

---

# FEATURE 4 — COALITION FINDER

**Concept:** For an RFP, compute the requirements/specialties/certs the current pharmacist
**lacks**, then traverse the graph to assemble a minimal **complementary team** of other
pharmacists who collectively cover the gaps. *"You cover 3/5 requirements. Add Dr. Lee (340B)
and Dr. Patel (oncology) → 5/5 covered."* This is a network effect only a graph can produce.

### Phase 4.1 — Backend
- **New `backend/graph/coalition.py`:**
  - `_rfp_needs(rfp_id)` — Cypher: RFP's `Category` names (+ `Requirement` descriptions).
  - `_candidate_pharmacists(needed_categories, exclude_user_id)` — Cypher:
    ```cypher
    MATCH (p:Pharmacist)-[:HAS_SPECIALTY]->(c:Category)
    WHERE c.name IN $needed AND p.user_id <> $me
    OPTIONAL MATCH (p)-[:HOLDS]->(ct:Certification)
    RETURN p.user_id AS user_id, p.full_name AS name,
           collect(DISTINCT c.name) AS covers_categories,
           collect(DISTINCT ct.name) AS certifications
    ```
- **New `backend/ai/coalition.py`:**
  - `find_coalition(rfp_id, user_id, my_profile) -> dict`
    1. `needed = rfp categories`; `mine = my_profile.specialties`.
    2. `gaps = needed − mine`.
    3. Greedy **set-cover** over candidates: repeatedly pick the pharmacist covering the most
       remaining gaps until covered or no improvement.
    4. Returns:
       ```python
       {
         "gaps": ["340B", "oncology"],
         "coverage_before": 60,        # % of needed I cover alone
         "coverage_after": 100,
         "team": [{"user_id","name","covers":["340B"],"certifications":[...]}],
         "rationale": "Partner with ... to cover all requirements."  # optional LLM
       }
       ```
  - `_rationale(team, gaps)` *(optional)* — 1-sentence LLM summary, deterministic fallback.
- **New `backend/api/routes/coalition.py`:**
  `GET /api/rfps/{rfp_id}/coalition` (`get_current_pharmacist`); builds `my_profile` dict,
  calls `find_coalition`. **Note:** register the router **before** `rfps.router` in `main.py`
  (same ordering reason as `matches.router` — avoids `/{id}` catching the sub-path).
- **Edit `backend/main.py`:** register `coalition.router` before `rfps.router`.

### Phase 4.2 — Frontend
- **Edit `client.js`:** `coalitionApi = { get: (rfpId) => api.get(`/api/rfps/${rfpId}/coalition`) }`.
- **New `frontend/src/components/CoalitionPanel.jsx`:** coverage bar (before→after), gap chips,
  team member cards (name + what each covers), rationale line.
- **Edit `frontend/src/pages/RfpDetailPage.jsx`:** "Find a Team" button → renders `CoalitionPanel`
  (pharmacist only).

**Files:** 3 new + 2 edits. **Depends on:** Phase 0 seed (several pharmacist profiles with
varied specialties/certs) — otherwise no candidates to team with.

---

# FEATURE 5 — WIN-PROBABILITY SIMULATOR

**Concept:** Interactive what-if. The pharmacist toggles hypothetical profile changes (add a
cert, add a specialty, change state) and instantly sees how win odds shift for a target RFP (or
their top RFPs) — **without saving** anything. Shows the graph "reasoning" live and nudges
profile completion.

### Phase 5.1 — Backend
- **New `backend/ai/win_simulator.py`:**
  - `_win_probability(rfp, profile, user_id) -> int`
    Blend the existing match score with historical signal:
    `0.7 * score_rfp_for_profile(rfp, profile, user_id) + 0.3 * 100*history_score(...)`
    (history optional; fall back to score alone). Returns 0-100.
  - `simulate(base_profile, overrides, user_id, rfp_id=None, top_n=5) -> dict`
    - `sim_profile = {**base_profile, specialties: base+added, certifications: base+added,
      location_state: override or base}`.
    - If `rfp_id`: compute baseline vs simulated for that RFP + per-factor breakdown.
    - Else: score `get_rfps_for_matching()` under both profiles, return the **top movers**
      (RFPs whose score increased most).
    - Returns:
      ```python
      {
        "baseline_score": 58, "simulated_score": 81, "delta": 23,
        "factors": [{"name":"category","before":..,"after":..}],   # when rfp_id given
        "top_movers": [{"id","title","before","after","delta"}]      # when no rfp_id
      }
      ```
  - **No persistence** — overrides are in-memory only; never calls `sync_*`.
- **New `backend/api/routes/simulator.py`:**
  ```python
  router = APIRouter(prefix="/api/simulator", tags=["simulator"])

  class WhatIfBody(BaseModel):
      rfp_id: str | None = None
      add_specialties: list[str] = []
      add_certifications: list[str] = []
      location_state: str | None = None

  @router.post("/what-if")
  def what_if(body: WhatIfBody, user=Depends(get_current_pharmacist), db=Depends(get_db)): ...
  ```
- **Edit `backend/main.py`:** register `simulator.router`.

### Phase 5.2 — Frontend
- **Edit `client.js`:** `simulatorApi = { whatIf: (data) => api.post('/api/simulator/what-if', data) }`.
- **New `frontend/src/pages/SimulatorPage.jsx`:** chips to add specialties/certs + state
  dropdown; debounced call on change; **animated dual gauge** (baseline vs simulated) + a
  "top movers" list showing which RFPs jumped. Optionally embeddable as a panel on RfpDetail
  for a single-RFP what-if.
- **Edit `frontend/src/App.jsx`:** `import SimulatorPage`, nav `{ path: '/simulator', label:
  'Win Simulator' }`, `<Route path="/simulator" element={<SimulatorPage/>}/>`.

**Files:** 2 new + 3 edits. **Depends on:** Phase 0 seed (application/win history makes the
history term meaningful; works without it on the base score).

---

# PHASE 0 (SHARED) — DEMO SEED & DATA

Three features need richer graph data than a fresh crawl provides. Add **one idempotent seed
routine** (extend `backend/utils/seed_data.py`, called from the existing startup seed path):

- `seed_forecast_history()` — ~3 orgs × 3–4 **closed** RFPs with `posted_date`s spaced 12–24
  months apart + a recent one → Foresight has cadence to project. *(Feature 1)*
- `seed_demo_pharmacists()` — ~5 `Pharmacist` nodes with varied `HAS_SPECIALTY`/`HOLDS` and
  some `APPLIED_TO {status:'won'/'lost'}` edges → Coalition has candidates, Simulator has
  history, Copilot/peer-recs have signal. *(Features 4, 5, 3)*

Guard everything with existence checks so re-running `docker-compose up` is safe.

---

# VERIFICATION (all features)

Per `CLAUDE.md`: `pytest`, `ruff check .`, `ruff format --check .`.

1. `docker-compose up` → all services healthy; `GET /health` ok; seed runs.
2. **Foresight:** `GET /api/foresight/predictions` → ≥3 predictions with windows + confidence;
   `/personalized` adds `fit_score`.
3. **Win Room:** `POST /api/rfps/{id}/win-room` → multi-round timeline, monotonically rising score.
4. **Copilot:** `POST /api/copilot/chat {"message":"find Texas MTM RFPs and draft one"}` →
   `reply` + non-empty `steps` + `cited_rfps`.
5. **Coalition:** `GET /api/rfps/{id}/coalition` → gaps + a team raising coverage to ~100%.
6. **Simulator:** `POST /api/simulator/what-if` with an added cert → `simulated_score > baseline_score`.
7. **Unit tests:** `_cadence` math, evaluator JSON parse + fallback, set-cover correctness,
   simulator non-persistence (graph unchanged after a call). Keep deterministic fallbacks so
   every feature degrades gracefully without an OpenAI key.

---

# COMBINED DEMO SCRIPT (~3 min)

1. **Dashboard → Foresight:** *"3 RFPs forecast in 90 days, one at 84% fit"* — opportunities
   not yet public.
2. **Copilot:** type *"Which of these can I win, and prep the best one?"* — watch the reasoning
   steps stream; it returns a ranked list.
3. **RFP detail → Coalition:** *"You cover 3/5 requirements — add these two pharmacists for
   5/5."* (graph network effect).
4. **Simulator:** add a **340B** cert → win gauge jumps **58 → 81**, and 4 RFPs climb the list.
5. **Win Room:** generate → score climbs **64 → 91** live, each fix annotated.
6. Close: *"From an opportunity that wasn't public, to a team, to a committee-ready 91-point
   proposal — the graph didn't just store data, it reasoned."*

---

# MASTER FILE SUMMARY

| Feature | New files | Edits | Independent? |
|---------|-----------|-------|--------------|
| 0 Demo Seed | — | `seed_data.py` | foundation |
| 1 Foresight | `ai/foresight.py`, `routes/foresight.py`, `components/PredictedOpportunities.jsx` | `main.py`, `client.js`, `DashboardPage.jsx` | needs Phase 0 |
| 2 Win Room | `ai/win_room.py`, `components/WinRoomModal.jsx` | `prompts.py`, `routes/rfps.py`, `client.js`, `RfpDetailPage.jsx` | yes |
| 3 Copilot | `ai/copilot.py`, `routes/copilot.py`, `pages/CopilotPage.jsx` | `main.py`, `client.js`, `App.jsx` | best last |
| 4 Coalition | `graph/coalition.py`, `ai/coalition.py`, `routes/coalition.py`, `components/CoalitionPanel.jsx` | `main.py`, `client.js`, `RfpDetailPage.jsx` | needs Phase 0 |
| 5 Simulator | `ai/win_simulator.py`, `routes/simulator.py`, `pages/SimulatorPage.jsx` | `main.py`, `client.js`, `App.jsx` | needs Phase 0 (soft) |

**Totals:** ~15 new files, ~14 edits across 5 features + shared seed. **0 deletions.**

---

# CROSS-CUTTING NOTES
- **No GDS required** — everything stays pure-Cypher + Python, consistent with the codebase.
- **Identity is server-injected** everywhere (Copilot tools, Coalition, Simulator); the LLM
  never supplies `user_id`.
- **Deterministic fallbacks** on every LLM path so features work without an API key (scores,
  rationales, explanations all degrade to rule-based output).
- **Router ordering:** any new `/api/rfps/...` sub-route (Coalition) must be registered before
  `rfps.router` in `main.py`, matching the existing `matches`/`applications` pattern.
