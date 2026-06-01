# APhA RFP Knowledge Graph — Enhancements Guide

Plain-language guide to the six graph + AI enhancements: **what each does, why it's
needed, and where to see it in the UI.**

> The UI is **role-based**. Pharmacists see #2, #3, #4, #5a, #6. Admins see #5b.
> Log in as a **pharmacist** for most features; log in as **admin** for trends.

---

## #1 — Applications saved into the graph

- **What:** When a pharmacist applies to an RFP, the action is mirrored into Neo4j as
  `(Pharmacist)-[:APPLIED_TO]->(RFP)`.
- **Why:** Application history previously lived only in PostgreSQL, invisible to the
  graph. Now the graph "knows who applied to what" — the foundation that powers #3 and #4.
- **Where in UI:** No screen of its own. It's the plumbing — felt indirectly through
  better recommendations and match scores below.

---

## #2 — Semantic similarity (embeddings + vector search)

- **What:** Each RFP is turned into a numeric "meaning vector," so the system finds
  *related* RFPs even when their categories/words differ
  (e.g. "oncology drug program" ↔ "specialty cancer pharmacy").
- **Why:** The old "similar RFPs" only counted shared category tags — it missed obvious
  matches with different wording.
- **Where in UI:** **RFP Detail page → "Similar RFPs" section** (bottom of the page).

---

## #3 — Win-prediction in the match score

- **What:** The match % now factors in history — orgs/categories where this pharmacist
  (or similar ones) previously won rank higher.
- **Why:** A pure profile-match score ignored track record. Two identical profiles
  should rank differently if one has a relevant win.
- **Where in UI:** The **% match badge on every RFP card** (Dashboard "Your Top Matches"
  + RFP Explorer). Cold-start users with no history fall back to the original 4-factor
  score, so nothing breaks.

---

## #4 — Collaborative recommendations ("pharmacists like you")

- **What:** "Pharmacists who applied to the same RFPs as you also pursued these."
- **Why:** Surfaces opportunities you'd never find by keyword/filter alone — peer
  behavior as a signal.
- **Where in UI:** **Dashboard → "Pharmacists like you also pursued" row**
  (pharmacist role only).

---

## #5 — Explainability + trend intelligence

### 5a — "Why was this matched?"

- **What:** A plain-English sentence tracing the graph path connecting you to the RFP.
- **Why:** Match scores felt like a black box; this builds trust.
- **Where in UI:** **RFP Detail page → blue banner under the match badge**
  (pharmacist role).

### 5b — Trends dashboard + weekly digest

- **What:** Most active agencies (PageRank-style) + trending categories; also a weekly
  email digest.
- **Why:** Strategic view of where the RFP market is moving.
- **Where in UI:** **Dashboard → "Top Organizations" + "Trending Categories"**
  (admin role); plus the weekly **email digest**.

---

## #6 — GraphRAG proposal generation

- **What:** When you generate a proposal, the AI is fed graph context first — the org's
  recurring requirements, similar past RFPs, your prior winning language.
- **Why:** Generic AI proposals become grounded ones that address what *that specific
  agency* keeps asking for.
- **Where in UI:** **RFP Detail page → "Generate Proposal" button.**

---

## Quick reference

| # | Enhancement | UI location | Role |
|---|-------------|-------------|------|
| 1 | Applications in graph | (plumbing — no direct screen) | — |
| 2 | Semantic similarity | RFP Detail → "Similar RFPs" | Pharmacist |
| 3 | Win-prediction score | % match badge on RFP cards | Pharmacist |
| 4 | Collaborative recs | Dashboard → "Pharmacists like you also pursued" | Pharmacist |
| 5a | Match explanation | RFP Detail → banner under match badge | Pharmacist |
| 5b | Trends + digest | Dashboard → Top Orgs / Trending Categories + email | Admin |
| 6 | GraphRAG proposals | RFP Detail → "Generate Proposal" | Pharmacist |

---

## Note on infrastructure

The Graph Data Science (GDS) plugin is **intentionally not installed** — `docker-compose.yml`
loads only `apoc`. The code uses pure-Cypher equivalents (e.g. `graph_insights.py` mirrors
what `gds.pageRank` would produce), so everything runs without GDS. Swapping in GDS later
is a drop-in upgrade, not a requirement.
