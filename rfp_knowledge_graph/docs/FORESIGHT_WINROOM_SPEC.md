# Foresight + Win Room — Phased Implementation Spec

Two flagship AI features layered on the existing RFP Knowledge Graph. Both are
**additive** — they reuse existing modules (`graph/queries.py`, `ai/proposal_generator.py`,
`ai/graph_rag.py`, `graph/neo4j_client.py`) and break nothing.

- **Foresight** — predict RFPs *before* they're posted, from temporal repost patterns in the graph.
- **Win Room** — an AI evaluator that red-teams a proposal against the RFP's scoring rubric and auto-revises it, with the score climbing live.

---

## Data Foundation (already present)

`RFP` nodes already store `posted_date`, `deadline`, `status`, `budget_range`, `description`
and connect to `Organization` and `Category` (see `create_rfp_with_relations` in
`backend/graph/queries.py`). Foresight mines the history of `posted_date` per
`(Organization, Category)`; no schema change is strictly required.

Auth conventions (from `backend/api/deps.py`):
- `get_current_user` → JWT payload dict (use for admin/public reads).
- `get_current_pharmacist` → `User` ORM object with `.id`, `.username`, `.profile`.

---

# FEATURE 1 — FORESIGHT

## Concept
Agencies re-bid on cycles. For each organization (optionally per category), collect the
historical `posted_date`s, compute the typical interval, and project the next expected
posting window with a confidence score derived from how regular the cadence is.

> *"Mississippi Medicaid posts a PBM RFP roughly every 18 months; the last was Feb 2024 —
> expect the next around Aug 2025. You're an 84% fit. Start preparing now."*

---

## Phase 1 — Foresight Backend

### 1.1 NEW `backend/ai/foresight.py`
Core forecasting engine — pure Python over Cypher results (no GDS needed).

- `_org_posting_history() -> list[dict]`
  Cypher: `MATCH (o:Organization)<-[:POSTED_BY]-(r:RFP)` collect `r.posted_date`,
  `r.deadline`, last RFP id/title, and the org's categories. Group per org.
- `_cadence(dates: list[str]) -> dict | None`
  Parse `YYYY-MM-DD`, sort, compute intervals between consecutive postings, take the
  **median interval** and **coefficient of variation**. Need ≥2 dated RFPs.
- `forecast_reposts(horizon_days: int = 180, min_history: int = 2) -> list[dict]`
  For each org with enough history: `predicted_date = last_posted + median_interval`.
  Keep predictions whose window falls within `horizon_days` (and allow slightly overdue =
  "expected now"). Confidence = function of (sample size, 1 - normalized variance).
  Returns per-prediction:
  ```python
  {
    "organization": str, "org_type": str | None,
    "category": str | None,
    "predicted_window_start": "YYYY-MM-DD",
    "predicted_window_end": "YYYY-MM-DD",
    "confidence": int,            # 0-100
    "cadence_months": float,      # median interval
    "history_count": int,
    "basis": str,                 # "Posts ~every 18 mo; last Feb 2024 (4 prior RFPs)"
    "last_rfp_id": str, "last_rfp_title": str,
  }
  ```
- `personalize_predictions(predictions, profile) -> list[dict]`
  Lightweight fit score reusing the same category/state overlap logic as matching: add
  `fit_score` (0-100) per prediction based on `profile.specialties` ∩ `category` and
  `profile.location_state`. Sort by `fit_score * confidence`.
- `explain_prediction(pred) -> str` *(optional polish)*
  One-sentence LLM rationale (same pattern as `ai/explainer.py`, with deterministic
  fallback) — makes the demo feel "AI", degrades gracefully if `openai_api_key` is unset.

### 1.2 NEW `backend/api/routes/foresight.py`
```python
router = APIRouter(prefix="/api/foresight", tags=["foresight"])

@router.get("/predictions")          # admin/general view
def predictions(horizon_days: int = Query(180, le=730),
                limit: int = Query(10, le=50),
                _=Depends(get_current_user)): ...

@router.get("/predictions/personalized")   # pharmacist view (adds fit_score)
def personalized(horizon_days: int = Query(180, le=730),
                 limit: int = Query(10, le=50),
                 user=Depends(get_current_pharmacist),
                 db: Session = Depends(get_db)): ...

@router.get("/organization/{org_name}")    # cadence timeline for one org (drill-in viz)
def org_timeline(org_name: str, _=Depends(get_current_user)): ...
```

### 1.3 EDIT `backend/main.py`
- Line 3: add `foresight` to the routes import.
- After the other `include_router` calls: `app.include_router(foresight.router)`.

### 1.4 Demo seed data — **critical for a credible demo**
Predictions need multi-year history. Add `seed_forecast_history()` (extend
`backend/utils/seed_data.py`, called from the existing startup seed path, idempotent):
insert ~3 organizations each with 3–4 **closed** historical RFPs whose `posted_date`s are
spaced 12–24 months apart, plus their most recent one. The cadence engine then yields
concrete, real-looking predictions on a fresh `docker-compose up`.

---

## Phase 2 — Foresight Frontend

### 2.1 EDIT `frontend/src/api/client.js`
```js
export const foresightApi = {
  predictions: (params) => api.get('/api/foresight/predictions', { params }),
  personalized: (params) => api.get('/api/foresight/predictions/personalized', { params }),
  organization: (name) => api.get(`/api/foresight/organization/${encodeURIComponent(name)}`),
}
```

### 2.2 NEW `frontend/src/components/PredictedOpportunities.jsx`
Card list. Each row: org + category, **predicted window** (e.g. "Aug–Oct 2025"), a
**confidence bar**, the `basis` sentence, an optional **fit %** badge (pharmacist), and a
"Based on" link to `last_rfp_id`. Empty state: "No forecasts yet — crawl more history."

### 2.3 EDIT `frontend/src/pages/DashboardPage.jsx`
- Add `predicted` state; on load call `foresightApi.personalized` (pharmacist) or
  `foresightApi.predictions` (admin).
- Render `<PredictedOpportunities items={predicted} />` near the top — this is the **first
  thing** in the demo, so place it prominently (a highlighted "Foresight" section above the
  two-column grid).

---

# FEATURE 2 — WIN ROOM

## Concept
Generate a draft (reusing GraphRAG context), then have an AI "evaluation committee" score it
against the RFP's scoring rubric, list where it loses points, and auto-revise — iterating
until the score plateaus. The UI animates the score climbing **64 → 78 → 91**.

---

## Phase 3 — Win Room Backend

### 3.1 EDIT `backend/ai/prompts.py` (append constants)
- `PROPOSAL_EVALUATION_SYSTEM` — instructs the model to act as a government RFP evaluation
  committee and return **strict JSON only** (same discipline as `ENTITY_EXTRACTION_SYSTEM`).
- `PROPOSAL_EVALUATION_USER` — injects RFP title/requirements/categories + the rubric +
  the proposal text; asks for per-criterion scores + specific gaps.
- `PROPOSAL_IMPROVEMENT_SYSTEM` / `PROPOSAL_IMPROVEMENT_USER` — revise the draft to close
  the listed gaps without inventing facts.

### 3.2 NEW `backend/ai/win_room.py`
- `build_rubric(rfp: dict) -> list[dict]`
  Deterministic weighted criteria derived from the RFP, so it always works:
  `Responsiveness to Requirements (30)`, `Qualifications & Certifications (25)`,
  `Technical Approach (25)`, `Compliance (10)`, `Clarity (10)`. (Weights can later be
  tuned from `rfp.requirements`.)
- `evaluate_proposal(proposal_text, rfp, rubric) -> dict`
  LLM → JSON: `{ "overall": int, "criteria": [{name, score, max, comment}], "gaps": [str] }`.
  Strict JSON parse with a deterministic fallback (keyword coverage of requirements) so a
  missing/failing LLM still returns a usable score.
- `improve_proposal(proposal_text, rfp, profile, evaluation) -> str`
  LLM revise addressing `evaluation["gaps"]`.
- `run_win_room(rfp, profile, username, context=None, rounds=3) -> dict`
  Orchestrate: round 0 draft = existing `generate_proposal(...)` (so it builds on GraphRAG
  #6). Then loop `evaluate → improve`, capturing each round. **Stop early** when the score
  gain `< 3`. Returns:
  ```python
  {
    "rounds": [
      {"round": 0, "score": 64, "criteria": [...], "gaps": [...], "proposal": "..."},
      {"round": 1, "score": 78, "criteria": [...], "gaps": [...], "proposal": "..."},
      {"round": 2, "score": 91, "criteria": [...], "gaps": [...], "proposal": "..."}
    ],
    "final_proposal": "...",
    "final_score": 91,
    "rfp_id": "...", "rfp_title": "..."
  }
  ```

### 3.3 EDIT `backend/api/routes/rfps.py`
Add alongside the existing `generate-proposal` route (reuse its profile-dict + context
assembly):
```python
@router.post("/{rfp_id}/win-room")
def win_room(rfp_id: str, rounds: int = Query(3, ge=1, le=4),
             user=Depends(get_current_pharmacist), db: Session = Depends(get_db)):
    rfp = get_rfp_detail(rfp_id) or 404
    context = gather_proposal_context(rfp, user_id=str(user.id))
    return run_win_room(rfp, profile_dict, user.username, context=context, rounds=rounds)
```

### 3.4 Config *(optional)*
Add `win_room_rounds: int = 3` to `backend/utils/config.py` (or keep the query param).

---

## Phase 4 — Win Room Frontend

### 4.1 EDIT `frontend/src/api/client.js`
```js
// inside rfpApi:
winRoom: (id, rounds = 3) => api.post(`/api/rfps/${id}/win-room`, null, { params: { rounds } }),
```

### 4.2 NEW `frontend/src/components/WinRoomModal.jsx`
Demo theatre. On open, call `rfpApi.winRoom(id)`; the API returns **all** rounds, the UI
**reveals them sequentially** with a short delay for effect:
- A large **animated score gauge** climbing per round (64 → 78 → 91).
- **Per-criterion bars** updating each round.
- A **"Fixes applied this round"** list (the `gaps` that were closed).
- Final proposal text with the existing **Copy / Download / Save as Draft** actions
  (lift these from the current `ProposalModal`).

### 4.3 EDIT `frontend/src/pages/RfpDetailPage.jsx`
Add a **"Win Room"** button next to the existing "Generate Proposal" button (pharmacist
only); wire it to open `WinRoomModal`. Keep the plain "Generate Proposal" path intact.

---

## Phase 5 — Verification & Demo Prep

1. `docker-compose up` → all services healthy; `GET /health` ok.
2. Startup seed creates forecast history → `GET /api/foresight/predictions` returns ≥3
   concrete predictions with windows + confidence.
3. Pharmacist login → `GET /api/foresight/predictions/personalized` returns `fit_score`.
4. Dashboard shows the **Predicted Opportunities** section first.
5. RFP detail → **Win Room** → `POST /api/rfps/{id}/win-room` returns a multi-round
   timeline with a monotonically rising score; modal animates the climb.
6. Per `CLAUDE.md` verification: `pytest`, `ruff check .`, `ruff format --check .`.
7. Add focused unit tests: `_cadence` math, `forecast_reposts` windowing, evaluator JSON
   parsing + fallback. Keep deterministic fallbacks so features degrade without an API key.

---

## File Change Summary

| # | File | Type | Phase |
|---|------|------|-------|
| 1 | `backend/ai/foresight.py` | New | 1 |
| 2 | `backend/api/routes/foresight.py` | New | 1 |
| 3 | `backend/main.py` | Edit — register router | 1 |
| 4 | `backend/utils/seed_data.py` | Edit — seed history | 1 |
| 5 | `frontend/src/api/client.js` | Edit — foresightApi + winRoom | 2 / 4 |
| 6 | `frontend/src/components/PredictedOpportunities.jsx` | New | 2 |
| 7 | `frontend/src/pages/DashboardPage.jsx` | Edit — predictions section | 2 |
| 8 | `backend/ai/prompts.py` | Edit — eval/improve prompts | 3 |
| 9 | `backend/ai/win_room.py` | New | 3 |
| 10 | `backend/api/routes/rfps.py` | Edit — win-room route | 3 |
| 11 | `frontend/src/components/WinRoomModal.jsx` | New | 4 |
| 12 | `frontend/src/pages/RfpDetailPage.jsx` | Edit — Win Room button | 4 |
| 13 | tests + (optional) `config.py` | New/Edit | 5 |

**~5 new files, ~6 edits, 0 deletions.**

---

## Demo Script (90 seconds)

1. **Dashboard** → "Predicted Opportunities" glows: *"3 RFPs forecast in the next 90 days,
   one at 84% fit."* (Foresight hook — opportunities that aren't public yet.)
2. Open the highest-fit prediction's "Based on" RFP → **RFP detail**.
3. Click **Win Room** → draft scores **64**, then climbs **78 → 91** live, each jump
   annotated (*"+9: added the 340B compliance language this agency always weights"*).
4. Close: *"From an opportunity that wasn't even posted yet, to a committee-ready
   91-point proposal — in under two minutes."*

---

## Risks / Honest Caveats
- **Foresight accuracy needs history.** With a fresh crawl there isn't enough signal, so
  the demo relies on `seed_forecast_history()`. Be transparent that it sharpens as the
  crawler accumulates real postings. (Future: persist predictions as nodes and track
  hit-rate when a real RFP later matches a forecast.)
- **LLM variance.** The evaluator/score can wobble run-to-run; the early-stop + deterministic
  fallback keep it sane. The score climb is real (re-evaluated each round), not hardcoded.
- **GDS not required.** Everything stays pure-Cypher + Python, consistent with the existing
  codebase choices.
