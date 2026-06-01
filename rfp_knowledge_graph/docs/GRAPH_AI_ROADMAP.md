# APhA RFP Knowledge Graph — AI + Graph Enhancement Roadmap

> **Goal:** Evolve Neo4j from a *storage layer* into a *reasoning engine*. Today every
> query is a 1–2 hop JOIN and matching is a Python formula. These six enhancements
> make the graph do similarity, recommendations, win-prediction, and grounded AI
> generation — the point at which "knowledge graph" stops being a label and becomes
> the moat.

---

## Current State (Baseline)

| Layer | What exists today |
|-------|-------------------|
| Graph | `(RFP)-[:POSTED_BY]->(Org)`, `-[:LOCATED_IN]->(Location)`, `-[:CATEGORIZED_AS]->(Category)`, `-[:REQUIRES]->(Requirement)`, `(Org)-[:BASED_IN]->(Location)` |
| Matching | `backend/ai/matcher.py` — weighted formula: 40% category Jaccard, 35% OpenAI semantic, 15% location, 10% org type |
| Proposals | `backend/ai/proposal_generator.py` — single RFP + profile → OpenAI markdown |
| Applications | `backend/db/models/application.py` — **PostgreSQL only**, `rfp_id` is a plain string (not in the graph) |
| Similarity | `get_similar_rfps()` — shared-category count only, no semantics |

**Key gap:** application/win history lives in PostgreSQL, disconnected from the graph,
so no graph algorithm can learn from it. **Enhancement #1 fixes this and unlocks the rest.**

---

## Implementation Sequence (by ROI)

```
#1 Applications in graph  ──┬─→ #4 Collaborative-filtering recs
   (foundation)            │
                           └─→ #3 Win-prediction features
#2 Embeddings + vectors  ──┬─→ #6 GraphRAG proposals
   (fast UX win)           │
                           └─→ (better #4 similarity)
#4 Recs ───────────────────→ #5 Explainability + trends
```

---

## Enhancement #1 — Persist Applications Into the Graph

**Activates:** Multi-hop traversals (Point #1) — the foundation for #3 and #4.

**Problem:** `Application` rows (PostgreSQL) reference `rfp_id` as an opaque string.
The graph has no idea who applied to or won what, so no graph algorithm can use it.

### Backend changes
- **New graph nodes/edges** in `backend/graph/queries.py`:
  - `(Pharmacist {user_id})` node mirroring the PostgreSQL `User` id
  - `(Pharmacist)-[:APPLIED_TO {status, applied_at}]->(RFP)`
  - `(Pharmacist)-[:WON]->(RFP)` / `(Pharmacist)-[:LOST]->(RFP)` (or a `status` property on `APPLIED_TO`)
  - `(Pharmacist)-[:HAS_SPECIALTY]->(Category)` and `(Pharmacist)-[:HOLDS]->(Certification)` (mirror profile arrays as nodes so they're traversable)
- **New function** `sync_application_to_graph(user_id, rfp_id, status)` — `MERGE` the pharmacist node + relationship; called from:
  - `backend/api/routes/applications.py` → after `POST` and `PUT` (status change)
  - `backend/api/routes/users.py` → on profile save, sync `HAS_SPECIALTY` / `HOLDS` edges
- **Backfill script** `backend/scripts/backfill_applications_to_graph.py` — one-time replay of existing PostgreSQL applications + profiles into Neo4j.

### Design decisions
- PostgreSQL stays the **source of truth** for application data (transactions, status timestamps). Graph is a **projection** for traversal/algorithms — keep writes idempotent with `MERGE` so re-sync is safe.
- Add a Neo4j constraint: `CREATE CONSTRAINT pharmacist_id IF NOT EXISTS FOR (p:Pharmacist) REQUIRE p.user_id IS UNIQUE`.

### Verification
- Save a draft + change status → confirm `(Pharmacist)-[:APPLIED_TO]->(RFP)` appears in Neo4j Browser.
- `MATCH (p:Pharmacist)-[:APPLIED_TO]->(r:RFP) RETURN p, r` renders the new layer.

---

## Enhancement #2 — RFP Embeddings + Vector Similarity

**Activates:** Graph algorithms (Point #2). Replaces naive shared-category similarity
with semantic similarity. **Fastest concrete win — Neo4j 5 has native vector indexes.**

### Backend changes
- **New module** `backend/ai/embeddings.py`:
  - `embed_text(text: str) -> list[float]` using OpenAI `text-embedding-3-small` (1536 dims, cheap)
  - `embed_rfp(rfp: dict) -> list[float]` — embed `title + description + categories + requirements`
- **Store the vector** in `create_rfp_with_relations()` (`backend/graph/queries.py`):
  - `SET r.embedding = $embedding` (Neo4j stores float arrays natively)
- **Create the index** (one-time, in a migration or `neo4j_client` startup):
  ```cypher
  CREATE VECTOR INDEX rfp_embedding IF NOT EXISTS
  FOR (r:RFP) ON r.embedding
  OPTIONS { indexConfig: { `vector.dimensions`: 1536, `vector.similarity_function`: 'cosine' } }
  ```
- **New query** `get_semantically_similar_rfps(rfp_id, limit=5)`:
  ```cypher
  MATCH (r:RFP {id: $id})
  CALL db.index.vector.queryNodes('rfp_embedding', $limit + 1, r.embedding)
  YIELD node AS other, score
  WHERE other.id <> $id
  RETURN other.id, other.title, score ORDER BY score DESC LIMIT $limit
  ```
- **Swap** `get_similar_rfps()` usage in `get_rfp_detail()` to use vector similarity
  (keep category-overlap as a fallback when an embedding is missing).
- **Backfill script** `backend/scripts/backfill_embeddings.py` — embed all 23 existing RFPs.

### Verification
- RFP detail "Similar RFPs" panel now surfaces semantically related RFPs even when
  categories differ (e.g. "oncology drug program" ↔ "specialty cancer pharmacy").

---

## Enhancement #3 — Win-Prediction Features From Graph Patterns

**Activates:** 3+ hop traversals (Point #1) + algorithms (Point #2). Depends on #1.

**Goal:** Augment the match score with historical signal — *"RFPs from organizations
in categories where this pharmacist (or similar pharmacists) has historically won."*

### Backend changes
- **New module** `backend/ai/graph_features.py`:
  - `org_win_rate(org_name) -> float` — `WON / APPLIED_TO` ratio for that org
  - `category_affinity(user_id, categories) -> float` — pharmacist's historical win rate in those categories (multi-hop: Pharmacist→WON→RFP→CATEGORIZED_AS→Category)
  - `peer_signal(user_id, rfp_id) -> float` — did similar pharmacists win this org/category? (uses #4's similarity)
- **Extend the scorer** `backend/ai/matcher.py`:
  - Add a 5th weighted factor `W_HISTORY` (start ~0.15, rebalance the others to sum to 1.0)
  - Gate it behind a flag/`if history available` so cold-start profiles (no history) fall back to the current 4-factor formula — **backward compatible**.
- Cache graph-feature lookups per `(user_id, rfp_id)` for the duration of a match request.

### Verification
- A pharmacist with a prior win at "TennCare" sees TennCare RFPs ranked higher than
  an identical-profile pharmacist with no history.

---

## Enhancement #4 — Collaborative-Filtering Recommendations

**Activates:** Algorithms (Point #2) + multi-hop (Point #1). Depends on #1 (and improves with #2).
*"Pharmacists like you also pursued these RFPs."*

### Backend changes
- **Install GDS** — add `neo4j` Graph Data Science plugin alongside APOC in `docker-compose.yml`:
  - `NEO4J_PLUGINS: '["apoc","graph-data-science"]'`
- **New module** `backend/ai/recommender.py`:
  - **Option A (simple, no GDS):** Cypher collaborative filtering —
    ```cypher
    MATCH (me:Pharmacist {user_id: $uid})-[:APPLIED_TO]->(r:RFP)<-[:APPLIED_TO]-(peer:Pharmacist)
    MATCH (peer)-[:APPLIED_TO]->(rec:RFP)
    WHERE NOT (me)-[:APPLIED_TO]->(rec) AND rec.status = 'open'
    RETURN rec.id, rec.title, count(DISTINCT peer) AS peer_count
    ORDER BY peer_count DESC LIMIT 10
    ```
  - **Option B (GDS, scalable):** project a `Pharmacist`–`RFP` bipartite graph and run
    `gds.nodeSimilarity` / `gds.fastRP` embeddings → KNN for recommendations.
- **New route** in `backend/api/routes/matches.py`: `GET /api/rfps/recommendations/collaborative`
  (requires `get_current_pharmacist`). Blend with the formula score from `matcher.py`
  into a single ranked list.

### Frontend
- `frontend/src/pages/DashboardPage.jsx` — add a "Pharmacists like you also pursued" row
  beneath "Your Top Matches."

### Verification
- Two pharmacists share an application → each starts seeing the other's *other* RFPs
  in the collaborative panel.

---

## Enhancement #5 — Explainability Paths + Org/Category Trend Intelligence

**Activates:** Pathfinding (Point #3) + centrality algorithms (Point #2).

### 5a. "Why was this matched?" — pathfinding
- **New query** `explain_match(user_id, rfp_id)` in `backend/graph/queries.py`:
  ```cypher
  MATCH path = shortestPath(
    (p:Pharmacist {user_id: $uid})-[*..6]-(r:RFP {id: $rid})
  )
  RETURN path
  ```
- **New module** `backend/ai/explainer.py` — feed the path nodes/edges to OpenAI to
  produce a one-sentence rationale: *"Matched because your Oncology specialty connects
  to 6 RFPs in this category, 4 from this same agency."*
- **New endpoint** `GET /api/rfps/{rfp_id}/match-explanation`.
- **Frontend:** RFP detail page — show the rationale under the match badge.

### 5b. Trend dashboard — centrality
- **New module** `backend/ai/graph_insights.py`:
  - `gds.pageRank` on Organizations → most influential/active agencies
  - Category demand growth (count RFPs per category over `posted_date` windows)
- **Reuse the email pipeline** (`backend/utils/email.py`, `backend/crawler/scheduler.py`):
  add a weekly `send_trends_digest` Celery beat task → OpenAI summarizes the graph
  insights into a digest email.
- **Frontend:** admin "Insights" page with top organizations + trending categories.

### Verification
- Match explanation renders a sentence with a real path; admin Insights shows a
  PageRank-ordered org list.

---

## Enhancement #6 — GraphRAG Proposal Generation

**Activates:** the strongest "AI + knowledge graph" story. Builds on #2.

**Today:** `generate_proposal(rfp, profile, username)` gets one RFP + the profile.
**GraphRAG:** traverse the graph to retrieve *context* and inject it into the prompt —
similar past winning proposals, the org's other RFPs, common requirements in the category.

### Backend changes
- **New module** `backend/ai/graph_rag.py`:
  - `gather_proposal_context(rfp_id, user_id) -> dict`:
    - Org's other RFPs + their common requirements (1–2 hops from the org)
    - Top-N semantically similar RFPs (Enhancement #2 vector search)
    - This pharmacist's past **won** proposal text for similar RFPs (Enhancement #1, from PostgreSQL `Application.proposal_text`)
    - Most common requirements in the RFP's categories (`category → REQUIRES` aggregation)
- **Extend** `backend/ai/proposal_generator.py`:
  - `generate_proposal(rfp, profile, username, context=None)` — append a `CONTEXT`
    section to the user prompt; `context=None` preserves current behavior (**backward compatible**).
- **Extend prompt** in `backend/ai/prompts.py` — add a context block instructing the
  model to address the org's recurring requirements and mirror prior winning language.
- **Wire it** in `backend/api/routes/rfps.py` → `POST /{rfp_id}/generate-proposal`:
  call `gather_proposal_context()` before `generate_proposal()`.

### Verification
- Generated proposal references the org's recurring requirements (e.g. *"As [Org]
  consistently requires X, our approach includes…"*) — verifiably grounded in graph data.

---

## Cross-Cutting Work

| Area | Task |
|------|------|
| **Infra** | Add `graph-data-science` plugin to `docker-compose.yml` (#4, #5) |
| **Schema** | Vector index (#2), `Pharmacist`/`Certification` nodes + uniqueness constraints (#1) |
| **Migration** | Backfill scripts: embeddings (#2), applications→graph (#1) |
| **Config** | Add `embedding_model_name` to `backend/utils/config.py` |
| **Cost** | Embeddings are one-time per RFP (~$0.0001 each); cache aggressively. Semantic match already LRU-cached in `matcher.py` |
| **Testing** | Unit-test new graph queries against a test Neo4j; keep formula fallbacks so features degrade gracefully when graph data is sparse |

---

## Demo Narrative for Manager

> *"Today the graph **stores** data. After this roadmap the graph **reasons**:
> it finds semantically similar RFPs (#2), recommends opportunities based on what
> peers won (#4), predicts win likelihood from history (#3), explains every match
> in plain English (#5), and grounds the AI proposal writer in real institutional
> knowledge (#6). That's the difference between a database and a knowledge graph —
> and it's the defensible moat."*

### Suggested phased delivery
1. **Phase A (fast wins):** #2 embeddings + #1 application sync — visible UX + foundation.
2. **Phase B (intelligence):** #6 GraphRAG proposals + #4 collaborative recs.
3. **Phase C (polish + strategy):** #3 win-prediction + #5 explainability/trends.
