# RFP Knowledge Graph POC — Change Impact & Rationale

Each change below answers: **What changes**, **Why we need it**, and **What impact it creates**.

---

## Phase 1 — Expand Crawl Targets

### 1. `backend/crawler/targets.py` — Add 10 new crawl sources

**What changes:**
10 new URL entries appended to the `CRAWL_TARGETS` list:
- APhA Grants/Scholarships page
- APhA News/press releases
- SAM.gov (federal pharmacy solicitations)
- Grants.gov (pharmacy grant search)
- HHS/HRSA funding page
- CMS procurement page
- Florida AHCA Medicaid pharmacy
- Texas HHSC open solicitations
- Ohio Medicaid RFPs/RFIs
- Michigan DHHS procurement

**Why we need it:**
The current system only crawls 7 state procurement sites (NY, MS, GA, WA, TN, NC). This misses:
- The primary pharmacy association (pharmacist.com / APhA) which is the core of our use case
- Federal sources (SAM.gov, Grants.gov, HHS) where large national RFPs are posted
- 3 additional high-volume Medicaid states (FL, TX, OH, MI)

Without this, the knowledge graph is populated from a narrow slice of available RFPs.

**Impact:**
- Celery's scheduled crawl (runs every 24h by default) automatically picks up all new targets — no other code changes needed
- Manual `POST /api/crawl/trigger` can also be pointed at any of these URLs
- More nodes in the graph → richer graph traversal for recommendations
- Wider geographic and organizational coverage for pharmacists in any US state

> Note: SAM.gov and pharmacist.com member sections are JS-heavy or login-gated. If Firecrawl returns 0 pages, the job completes cleanly with 0 RFPs — no errors, no crashes. The publicly accessible APhA pages (Grants, News) are expected to work.

---

## Phase 2 — Graph Schema & Queries

### 2. `backend/graph/schema.py` — Add Pharmacist node constraint

**What changes:**
One new constraint added to Neo4j on startup:
```cypher
CREATE CONSTRAINT pharmacist_username IF NOT EXISTS FOR (p:Pharmacist) REQUIRE p.username IS UNIQUE
```

**Why we need it:**
Without this, multiple `MERGE` calls for the same user could create duplicate `Pharmacist` nodes, causing split profile state (preferences stored across multiple nodes instead of one).

**Impact:**
- Guarantees one Pharmacist node per user (keyed on JWT `sub` / username)
- Neo4j enforces this at the database level — safe even under concurrent requests
- Auto-applied on next service startup via the existing `init_schema()` call

---

### 3. `backend/graph/queries.py` — Add `get_pharmacist_profile()`

**What changes:**
New Cypher function that fetches a `Pharmacist` node and collects its `PREFERS_CATEGORY` and `PREFERS_LOCATION` relationships.

**Why we need it:**
The profile needs to be read in two places: the `GET /api/profile/` endpoint and the recommendations route (to decide whether to use graph-traversal or simple filter). Without this function, those callers would duplicate the query.

**Impact:**
- Returns `None` for first-time users (no profile yet) — callers handle this gracefully with defaults
- Used as the "read" half of profile management
- Lightweight query — only touches the Pharmacist node and its 2 relationship types

---

### 4. `backend/graph/queries.py` — Add `upsert_pharmacist_profile()`

**What changes:**
New Cypher function that `MERGE`s a `Pharmacist` node and rebuilds its `PREFERS_CATEGORY` / `PREFERS_LOCATION` relationships from scratch on each save.

**Why we need it:**
Profiles must be updatable — a pharmacist can change their preferred states or categories. A simple SET would leave stale relationships around (e.g., removing Texas from preferences wouldn't delete the old `PREFERS_LOCATION` edge). The delete-then-rebuild pattern ensures the graph always reflects the current saved preferences.

**Impact:**
- Creates the `Pharmacist` node on first save (idempotent via MERGE)
- Connects it to existing `Category` and `Location` nodes already in the graph from crawled RFPs — this is the key graph linkage that enables traversal recommendations
- Reuses `Category` and `Location` nodes rather than duplicating them

---

### 5. `backend/graph/queries.py` — Add `get_graph_recommendations()`

**What changes:**
New multi-hop Cypher query that scores open RFPs against a pharmacist's profile using graph traversal:

```
Pharmacist → PREFERS_CATEGORY → Category ← CATEGORIZED_AS ← RFP    (+3 per match)
Pharmacist → PREFERS_CATEGORY → Category ← RFP → Category ← RFP    (+2 per 2-hop match)
Pharmacist → PREFERS_LOCATION → Location ← LOCATED_IN ← RFP        (+1 per match)
RFP deadline ≤ 60 days                                               (+1 bonus)
```
Score normalized to 0–100.

**Why we need it:**
The existing `get_recommendations()` is a simple filter (WHERE category IN list, ORDER BY deadline). It doesn't use the graph at all — it just queries RFP properties. A knowledge graph's value is in traversal: finding RFPs connected to a pharmacist's interest graph through shared nodes, not just matching a flat list.

The 2-hop traversal finds RFPs that share a category with another RFP the pharmacist has affinity for — discovering non-obvious matches (e.g., a pharmacist who prefers "clinical-pharmacy" is also surfaced an RFP tagged only as "consulting" if multiple other RFPs bridge those two categories).

**Impact:**
- Replaces simple filter with genuine graph intelligence
- Returns `relevance_score` (0–100) per RFP — surfaced as "% match" in the UI
- Zero-score RFPs are excluded — list is purposeful, not just every open RFP
- Pharmacists with no profile set fall back to the old filter (no disruption)

---

## Phase 3 — Backend API

### 6. `backend/api/schemas/rfp.py` — Add `relevance_score` to `RfpSummary`

**What changes:**
```python
relevance_score: Optional[int] = None
```

**Why we need it:**
`RfpSummary` is the Pydantic model used for list and recommendation responses. Without this field, FastAPI would strip `relevance_score` from graph recommendation responses even if the query returned it.

**Impact:**
- Backward compatible — existing endpoints that don't set this field return `null`
- Recommendations endpoint now passes the score through to the client
- Frontend can show "% match" badge conditionally (`if rfp.relevance_score != null`)

---

### 7. NEW `backend/api/schemas/profile.py`

**What changes:**
Two Pydantic models:
- `PharmacistProfileResponse` — what the API returns (all fields present with defaults)
- `PharmacistProfileUpdate` — what the API accepts for updates (all fields Optional)

**Why we need it:**
FastAPI requires explicit schema models for request/response validation. The two separate models follow the existing pattern in `rfp.py` (separate list vs detail schemas) and the update model uses `Optional` so callers can do partial updates (patch-like behavior via PUT).

**Impact:**
- API automatically validates input types (e.g., rejects `experience_level: 123`)
- FastAPI generates correct OpenAPI docs for the profile endpoints
- Response model guarantees consistent shape — frontend can rely on field presence

---

### 8. NEW `backend/api/routes/profile.py`

**What changes:**
Two new endpoints:
- `GET /api/profile/` — returns current user's profile (JWT `sub` → username)
- `PUT /api/profile/` — saves profile, returns updated version

**Why we need it:**
Without an API to read/write the pharmacist profile, the Profile UI page has no way to persist preferences. The profile is stored in Neo4j (not Postgres) — consistent with the rest of the graph data, no new database table needed.

**Impact:**
- Pharmacists can now persist their skill areas, preferred states, and categories
- Profile is per-user (keyed on JWT username) — `admin` and `analyst` have separate profiles
- First `GET` returns sensible defaults — UI shows empty state, not an error
- Authenticated only (`Depends(get_current_user)`) — same auth pattern as all other `/api/*` routes

---

### 9. `backend/api/routes/recommendations.py` — Route-switch to graph traversal

**What changes:**
The endpoint now checks if the current user has a profile with preferences. If yes, calls `get_graph_recommendations()`; if no, falls back to the existing `get_recommendations()`.

**Why we need it:**
Graph traversal only works if a `Pharmacist` node exists in Neo4j with at least one `PREFERS_CATEGORY` or `PREFERS_LOCATION` edge. Calling it without a profile returns nothing useful. The fallback preserves the existing behavior for unauthenticated demo use or first-time users.

**Impact:**
- Zero breaking change — users without a profile get the same deadline-ordered list as before
- Users with a profile get scored, ranked, graph-aware recommendations automatically
- No new query param needed — the switch is automatic based on profile existence

---

### 10. `backend/main.py` — Register profile router

**What changes:**
```python
# Import line:
from backend.api.routes import auth, rfps, crawl, graph, recommendations, profile

# Router registration:
app.include_router(profile.router)
```

**Why we need it:**
FastAPI only serves endpoints from routers that are explicitly registered. Without this, `GET /api/profile/` returns 404.

**Impact:**
- `GET /api/profile/` and `PUT /api/profile/` become live endpoints
- Appears in FastAPI's auto-generated docs at `http://localhost:8009/docs`

---

## Phase 4 — Frontend

### 11. `frontend/package.json` — Add `react-force-graph-2d`

**What changes:**
```json
"react-force-graph-2d": "^1.25.0"
```

**Why we need it:**
The graph visualization widget needs a library to render a force-directed graph in the browser. `react-force-graph-2d` renders via HTML Canvas (no SVG overhead), handles 100s of nodes smoothly, and works with Vite out of the box. `recharts` (already present) only does charts — it cannot render a graph with arbitrary nodes and edges.

**Impact:**
- `docker-compose up` re-runs `npm install` automatically (existing compose command: `sh -c "npm install && npm run dev"`) — no manual step needed
- Adds ~200KB to the frontend bundle (acceptable for a POC)

---

### 12. `frontend/src/api/client.js` — Add `profileApi`

**What changes:**
```js
export const profileApi = {
  get: () => api.get('/api/profile/'),
  update: (data) => api.put('/api/profile/', data),
}
```

**Why we need it:**
All API calls go through the central Axios instance in `client.js` — this ensures the JWT token interceptor is applied automatically. ProfilePage needs to call these endpoints; without the export, it would need to import the raw `api` instance and manage headers manually.

**Impact:**
- `ProfilePage` imports `profileApi` and calls `profileApi.get()` / `profileApi.update()` cleanly
- Token expiry/401 handling is automatic (existing interceptor)

---

### 13. NEW `frontend/src/pages/ProfilePage.jsx`

**What changes:**
New page with toggle-chip UI:
- Name input, experience level dropdown
- Skill chips (PharmD, BCPS, MTM Certified, 340B, etc.)
- Category chips — these map directly to Neo4j Category node names that RFPs are tagged with
- State chips — these map to Location node state values in Neo4j
- Save button → PUT /api/profile/ → success message

**Why we need it:**
Without a UI to set preferences, the graph-traversal recommendation engine has no input. Pharmacists need a way to declare what they're interested in so the Cypher query has `PREFERS_CATEGORY` and `PREFERS_LOCATION` edges to traverse.

**Impact:**
- First-time pharmacists see empty chips, can select and save in 30 seconds
- Saving immediately affects `GET /api/recommendations/` results
- Profile persists across sessions (stored in Neo4j)

---

### 14. NEW `frontend/src/components/GraphViz.jsx`

**What changes:**
Canvas-based force-directed graph widget using `react-force-graph-2d`:
- Accepts `rfps` array as prop
- Builds graph: RFP nodes (blue) → Category nodes (light blue) + Organization nodes (purple)
- Node labels appear on zoom > 1.5x
- Placeholder shown when no data

**Why we need it:**
The core POC concept is a **knowledge graph** — but without any visualization, it's invisible to stakeholders. Showing the graph makes the "why Neo4j" question obvious during a demo. It demonstrates that RFPs are connected through shared categories/organizations, not just a flat list.

**Impact:**
- Hidden by default behind "Show Graph" toggle (doesn't slow dashboard load)
- Works on the existing RFP data already fetched for the dashboard — no new API call
- Makes the graph structure tangible for demos

---

### 15. `frontend/src/pages/DashboardPage.jsx` — Enhance with graph viz + score badges

**What changes:**
- Import `GraphViz`, add `showGraph` toggle state
- "Show Graph" / "Hide Graph" button in header
- `<GraphViz rfps={[...recent, ...recommended]} />` rendered conditionally
- Recommendation cards get green "X% match" badge overlay when `relevance_score` is set
- "Edit profile" link added next to "Recommended for You" heading

**Why we need it:**
The dashboard is the first screen pharmacists see. The recommendations without scores look identical to the existing simple list — no visible evidence of graph intelligence. The score badge and the "Edit profile" CTA complete the feedback loop: pharmacist sets preferences → sees graph finds matches → score tells them why.

**Impact:**
- `relevance_score` of `null` → badge hidden (backward compatible with unscored results)
- Graph visualization is opt-in (toggle) so it doesn't affect performance for regular use
- "Edit profile" discovery — without this link, users may not find the Profile page

---

### 16. `frontend/src/App.jsx` — Add Profile route + nav entry

**What changes:**
```jsx
// NAV array:
{ path: '/profile', label: 'My Profile' }

// Routes:
<Route path="/profile" element={<ProfilePage />} />
```

**Why we need it:**
Without adding the route, `/profile` returns a blank page. Without the nav entry, users can't discover the page without manually typing the URL.

**Impact:**
- "My Profile" appears in the left sidebar navigation
- Route is protected (inside `PrivateRoute`) — unauthenticated users are redirected to login

---

## Summary Table

| Change | Why | Impact Level |
|---|---|---|
| +10 crawl targets | Capture pharmacist.com + federal RFP sources | High — more data in graph |
| Pharmacist constraint | Prevent duplicate profile nodes | Low — safety constraint |
| `get_pharmacist_profile()` | Read profile for API + recommendation routing | Medium — enables all profile features |
| `upsert_pharmacist_profile()` | Persist preferences as graph edges | High — connects pharmacist to graph |
| `get_graph_recommendations()` | Multi-hop traversal scoring | High — core POC intelligence |
| `relevance_score` in schema | Pass score through API response | Low — schema field, enables UI badge |
| `profile.py` schema | Validate profile input/output | Low — API safety |
| `profile.py` route | `GET`/`PUT` /api/profile/ endpoints | High — exposes profile to frontend |
| Recommendations route update | Auto-switch to graph traversal when profile exists | High — activates graph recommendations |
| Register profile router | Make profile endpoints live | Low — required wiring |
| `react-force-graph-2d` | Enable graph visualization | Medium — POC demo value |
| `profileApi` in client.js | Clean API access from frontend | Low — required wiring |
| `ProfilePage.jsx` | Pharmacist preference UI | High — input for recommendations |
| `GraphViz.jsx` | Visual proof of graph structure | Medium — demo/stakeholder value |
| Dashboard enhancements | Show scores + graph viz | Medium — makes POC visible |
| App routing + nav | Discover and reach Profile page | Low — required wiring |
