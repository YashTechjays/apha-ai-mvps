# APhA RFP Knowledge Graph — Live Demo Guide

> **Audience:** Manager demo  
> **Duration:** ~15 minutes  
> **URLs:** Frontend `http://localhost:3009` · API `http://localhost:8009` · Neo4j `http://localhost:7474`

---

## What This Product Does (30-second pitch)

Government agencies and health organizations post pharmacy-related RFPs across dozens of websites. Today, pharmacists and consultants find these manually — or miss them entirely.

This system:
1. **Crawls** 7 verified government procurement portals automatically (Firecrawl)
2. **Extracts** structured RFP data using AI (OpenAI GPT-4o-mini) into a knowledge graph (Neo4j)
3. **Matches** each RFP to registered pharmacists by specialty, certifications, and location
4. **Generates** a personalized proposal draft with one click
5. **Tracks** applications through a pipeline (Draft → Submitted → Won/Lost)
6. **Emails** pharmacists automatically when a new RFP matches their profile

---

## Demo Flow (Step by Step)

### Step 1 — Admin View: The Knowledge Graph Dashboard

**URL:** `http://localhost:3009` · Login: `admin / apha2026`

**What to show:**
- The **graph stats panel**: 23 RFPs · 22 Organizations · 18 Locations · 41 Categories · 217 Relationships
- **Recent RFPs** pulled from real government sites (TennCare, NC Medicaid, WA HCA, etc.)
- **RFP Explorer** (`/rfps`) — search, filter by state/category/status
  - Search `oncology` → instant filtered results
  - Filter by state `TX` → location-aware results
- **RFP Detail page** — click any RFP to see org, requirements, budget, similar RFPs

**Talking point:** *"This data was crawled from real government procurement portals — not fake data. The AI extracted structured information from unstructured HTML pages."*

---

### Step 2 — Crawl Manager: Where the Data Comes From

**URL:** `http://localhost:3009/crawl` (admin nav)

**What to show:**
- The 7 target sites listed (TennCare, NC Medicaid, MS MSDH, GA DCH, WA HCA, NY Health, MS Medicaid)
- Click **Trigger Crawl** → watch the job queue update in real time
- Show a completed crawl job: pages crawled, RFPs extracted, timestamp

**Talking point:** *"This runs on a schedule every 24 hours automatically via Celery. Each crawl fires AI extraction and then notifies matched pharmacists."*

---

### Step 3 — Pharmacist Registration

**URL:** `http://localhost:3009/register`

**What to show:**
- Register a new account (`demo_pharm / demo1234` — use a fresh username)
- Lands on **My Profile** automatically

**Or use existing demo pharmacist:** Login as `pharmtest2 / pharmacy123`

---

### Step 4 — Profile: Teaching the System Your Expertise

**URL:** `http://localhost:3009/profile`

**What to show:**
- **Personal Info:** Name, city/state, years of experience
- **Specialties** — tap to select: `clinical-pharmacy`, `oncology`, `compliance`
- **Certifications** — type `PharmD` → Enter, `BCOP` → Enter
- **Org Type Preference** — select `government`
- **Notification Settings** — toggle + threshold slider (e.g. 60%)
- Click **Save Profile**

**Talking point:** *"This profile is what the AI uses to score every RFP in the graph. The more complete it is, the better the matches."*

---

### Step 5 — AI Matching: Your Top Matches Dashboard

**URL:** `http://localhost:3009/` (as pharmacist)

**What to show:**
- Right panel: **"Your Top Matches"** — RFPs sorted by match score
- Colored badges: **green ≥80%**, **yellow 60–79%**
- Example scores with `clinical-pharmacy + oncology + BCOP`:
  - 62% — Pharmacy Actual Acquisition Cost (AAC) Program
  - 52% — Pharmacy Benefits Administrator (PBA)
  - 42% — Analytic Support

**Talking point:** *"The match score is calculated from 4 weighted factors: specialty overlap (40%), AI semantic match of requirements vs certifications (35%), location (15%), and org type preference (10%). The semantic scoring uses OpenAI — it understands that 'BCOP' satisfies 'oncology clinical experience required'."*

---

### Step 6 — AI Proposal Generator

**URL:** Click any matched RFP → click the green **"Generate Proposal"** button

**What to show:**
- Loading spinner: *"Generating proposal with AI..."*
- Proposal appears in ~5 seconds with sections:
  - Executive Summary (mentions the pharmacist by name)
  - Qualifications & Experience (references PharmD, BCOP)
  - Technical Approach (specific to the RFP requirements)
  - Project Timeline
  - Budget Narrative
- **Copy** button — copies to clipboard
- **Download .md** button — saves as a markdown file
- **Save as Draft** button — saves to application tracker

**Talking point:** *"One click generates a proposal that already knows the RFP requirements AND the pharmacist's credentials. It's a first draft in seconds instead of hours."*

---

### Step 7 — Application Tracker

**URL:** `http://localhost:3009/applications` (pharmacist nav: "My Applications")

**What to show:**
- The draft application appears in the table
- Status tabs: All / Draft / Submitted / In Review / Won / Lost
- **Inline status dropdown** — change Draft → Submitted → watch `submitted_at` timestamp appear
- RFP title is clickable — links back to the RFP detail

**Talking point:** *"Every proposal the pharmacist generates can be tracked through the entire pipeline from first draft to win or loss."*

---

### Step 8 — Email Notification (Live)

**What to show (already triggered):**
- Open `yash@techjays.com` inbox
- Show the match email: subject `[62% Match] New RFP: Pharmacy Benefits Administrator (PBA)`
- HTML email with match score badge, RFP details, **"View RFP & Generate Proposal"** CTA button

**Talking point:** *"Pharmacists don't need to log in to find matches. When the crawler finds new RFPs, Celery fires notification emails automatically to every pharmacist whose profile scores above their threshold."*

---

## Technical Architecture (For Technical Questions)

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)               │
│              http://localhost:3009                       │
│  RegisterPage · ProfilePage · DashboardPage             │
│  RfpListPage · RfpDetailPage · ApplicationsPage        │
└────────────────────┬────────────────────────────────────┘
                     │ REST API (Axios)
┌────────────────────▼────────────────────────────────────┐
│                 Backend (FastAPI)                        │
│              http://localhost:8009                       │
│                                                          │
│  /auth/login|register   → JWT (HS256)                   │
│  /users/me|profile      → PostgreSQL                    │
│  /api/rfps              → Neo4j                         │
│  /api/rfps/matches      → Neo4j + OpenAI scorer         │
│  /api/rfps/{id}/generate-proposal → OpenAI GPT-4o-mini  │
│  /api/rfps/{id}/applications      → PostgreSQL          │
│  /api/crawl/trigger     → Celery task                   │
└──────┬──────────────┬───────────────────────────────────┘
       │              │
┌──────▼──────┐ ┌─────▼────────────────────────────────────┐
│  PostgreSQL │ │              Neo4j Graph DB               │
│  port 5441  │ │         http://localhost:7474             │
│             │ │                                           │
│  users      │ │  (RFP)─[POSTED_BY]→(Organization)        │
│  profiles   │ │  (RFP)─[LOCATED_IN]→(Location)           │
│  applications│ │  (RFP)─[CATEGORIZED_AS]→(Category)       │
│  crawl_jobs │ │  (RFP)─[REQUIRES]→(Requirement)          │
└─────────────┘ └──────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│            Celery Worker + Beat (Redis broker)          │
│                                                          │
│  run_crawl_job          → Firecrawl → OpenAI extract    │
│  scheduled_crawl        → every 24h, all 7 targets      │
│  notify_new_rfp_matches → score + Postmark SMTP email   │
└─────────────────────────────────────────────────────────┘
```

### Stack Versions
| Component | Technology | Version |
|-----------|-----------|---------|
| API | FastAPI + Uvicorn | 0.100+ |
| Auth | JWT (python-jose) + bcrypt | HS256 |
| Graph DB | Neo4j | 5.x |
| Relational DB | PostgreSQL | 15 |
| Task Queue | Celery + Redis | 5.x |
| Web Crawler | Firecrawl SDK | v1 |
| AI Extraction | OpenAI GPT-4o-mini | — |
| AI Matching | OpenAI + Jaccard similarity | — |
| Email | Postmark SMTP | — |
| Frontend | React 18 + Vite + Tailwind CSS | — |
| Containers | Docker Compose | — |

### Matching Score Formula
```
match_score = (
  0.40 × category_jaccard(rfp.categories, profile.specialties)
+ 0.35 × openai_semantic(rfp.requirements, profile.certifications)
+ 0.15 × location_score(rfp.state, profile.state)
+ 0.10 × org_type_score(rfp.org_type, profile.preferred_orgs)
) × 100
```

### Crawl Sources (Live Government Sites)
| Site | State | Type |
|------|-------|------|
| TennCare Upcoming Procurements | TN | Medicaid |
| NC DHHS RFPs & RFIs | NC | Medicaid |
| Washington HCA Bids & Contracts | WA | State Health |
| NY Health Funding Opportunities | NY | State Health |
| MS MSDH Procurement | MS | State Health |
| MS Medicaid Resources | MS | Medicaid |
| GA DCH Bidding Opportunities | GA | State Health |

---

## Demo Credentials

| Role | Username | Password | Access |
|------|----------|----------|--------|
| Admin | `admin` | `apha2026` | Dashboard, RFP Explorer, Crawl Manager |
| Analyst | `analyst` | `analyst123` | Dashboard, RFP Explorer |
| Pharmacist (demo) | `pharmtest2` | `pharmacy123` | Full pharmacist pipeline |

---

## Pre-Demo Checklist

- [ ] All containers running: `docker compose ps` in `rfp_knowledge_graph/`
- [ ] Frontend loads: `http://localhost:3009`
- [ ] API health: `http://localhost:8009/health` → `{"status":"ok"}`
- [ ] Neo4j browser: `http://localhost:7474` (optional — impressive visual)
- [ ] Log in as `pharmtest2` first to warm up the match cache (~20s first load)
- [ ] Open `yash@techjays.com` inbox in a separate tab for the email demo

---

## Potential Manager Questions

**Q: Is this real data or mock data?**  
A: Real data crawled from 7 live government procurement portals. 23 RFPs currently in the graph from TennCare, NC DHHS, WA HCA, and others.

**Q: How often does it crawl?**  
A: Every 24 hours automatically. Can also be triggered manually from the Crawl Manager.

**Q: How accurate is the matching?**  
A: The semantic component uses OpenAI to understand context — it knows BCOP satisfies "oncology experience required." Scores are tunable via the profile threshold slider.

**Q: What happens when a pharmacist misses an email?**  
A: All matches are also visible on their dashboard under "Your Top Matches" when they log in.

**Q: Can this scale to more sites?**  
A: Yes — adding a new crawl target is one entry in `targets.py`. The extraction and matching pipeline handles it automatically.

**Q: How is auth secured?**  
A: JWT tokens (HS256, 8-hour expiry). Passwords hashed with bcrypt. Admin/pharmacist roles are separated at the API dependency level.
