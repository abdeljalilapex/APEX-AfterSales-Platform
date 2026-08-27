# PROJECT_HANDOFF.md — APEX AutoPerf Group

**Status as of:** August 2026
**Purpose:** This document allows a new senior engineer to take over the APEX project with zero prior context. Read this document fully before touching any code.

---

## 1. Project Vision

APEX is being transformed from a methodology-driven fictional-company prototype into a **real multi-tenant SaaS product** for the automotive after-sales sector (independent garages up to large dealership networks).

**Core value proposition:** ingest operational data from a client's ERP system (invoices, repair orders, purchases, appointments), turn it into performance KPIs (calculated, threshold-evaluated, traced to source), and eventually layer automated recommendations (best/worst technician, product, repair — with actionable suggestions) plus periodic market/competitor intelligence.

**This ambition was explicitly and formally decided as a new milestone (ADR-022)** — the project did not start with this goal. It started as a fictional-company exercise focused on building a rigorous working methodology. Do not treat "vendable multi-client SaaS" as having been the intent from day one; it is a deliberate pivot, documented as such.

Two data categories are planned, with incompatible freshness requirements:
- **Internal (ERP) data**: near real-time (minutes), strict per-client isolation.
- **External (market/competitor) data**: monthly/quarterly, potentially shared across clients in the same sector (open question, not resolved).

---

## 2. Current Project State

**Honest summary: the technical foundation is built and verified against real infrastructure. Nothing customer-facing exists yet. No real ERP has ever been connected.**

Verified against a real Supabase production instance (not just locally):
- PostgreSQL schema (32 tables)
- Python KPI engine (SQLAlchemy Core)
- FastAPI REST API (5 routes)
- Authentication (Supabase Auth, JWT verified via JWKS/ES256)
- Row-Level Security enabled (deny-by-default) on all 32 tables
- A minimal frontend prototype consuming the real API is in progress/finalization

**Not started at all:** ERP integration, public deployment, billing/subscription model, any real customer, event-queue abstraction, strict whitelist for `source_critere` interpretation, frontend component architecture / state management.

Do not describe project completion as a percentage — the domains are too unequal (see section 8 and section 15 for why).

---

## 3. Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│  Frontend prototype (minimal, single view, in progress)   │
│    Supabase Auth login → API call → display KPI result     │
├──────────────────────────────────────────────────────────┤
│  FastAPI API (5 routes), JWT-protected, CORS enabled       │
│    (CORS currently PERMISSIVE — dev only, must be          │
│    restricted before any public deployment)                 │
├──────────────────────────────────────────────────────────┤
│  Auth: Supabase Auth, JWT verified via JWKS (ES256,         │
│  asymmetric) — no shared secret to protect server-side       │
├──────────────────────────────────────────────────────────┤
│  KPI Engine (Python, SQLAlchemy Core):                       │
│    extracteur.py / calculateur.py / evaluateur.py /          │
│    ecrivain.py / provenance.py                                │
├──────────────────────────────────────────────────────────┤
│  PostgreSQL on Supabase (real, production project           │
│  "APEX Production", EU-West region)                          │
│    Organisation → Concession → operational data              │
│    RLS enabled (deny-by-default) on all 32 tables             │
├──────────────────────────────────────────────────────────┤
│  ERPAdapter — designed in principle only, NOT implemented     │
├──────────────────────────────────────────────────────────┤
│  Real client ERP — NO CONNECTION EXISTS TODAY                 │
└──────────────────────────────────────────────────────────┘
```

**Stack decisions:**
- Backend: Python / FastAPI
- DB: PostgreSQL via Supabase (free tier during dev; paid tier required before any real client)
- Auth: Supabase Auth
- Planned hosting: Render (not yet done)
- DB access library: SQLAlchemy Core (not full ORM) — chosen to avoid a second source of truth vs. raw SQL schema, and for reuse potential by the API layer (ADR-027)
- ERP sync strategy (planned, not built): incremental polling every 2–5 min, tolerant of per-client rate limits, filtered by a `date_champ_periode` column (not hardcoded in code) — see ADR-025/028/031

**Non-obvious infrastructure gotcha:** Supabase's direct DB connection (`db.<ref>.supabase.co:5432`) requires IPv6. Many environments (including the dev sandbox and GitHub Codespaces used for this project) lack outbound IPv6. **Always use the Session Pooler connection string** (`*.pooler.supabase.com`, IPv4) instead. This cost significant debugging time — don't repeat it.

**Another non-obvious gotcha:** Newer Supabase projects sign JWTs with **ES256 by default**, with no option to revert to legacy HS256 shared-secret signing. Auth verification must use JWKS (public key fetch), not a shared `SUPABASE_JWT_SECRET`. This was discovered mid-project and required a full rewrite of the auth module — do not assume HS256.

---

## 4. Architecture Decision Records (ADR) — Summary

The project maintains a single chronological ADR log (`APEX_ADR.md`), never rewritten retroactively (a superseded decision gets a new number; the old entry is marked superseded, not deleted). **39 entries as of this handoff.** Read the full log before making any architectural change. Key entries:

- **ADR-001**: `Repository` as the single data-access point (the one thing to rewrite during the backend migration).
- **ADR-006/007/008**: KPIDefinition/KPIValue separation; "scheduled calculation + stored" architecture chosen over on-the-fly or rule-DSL approaches.
- **ADR-009**: KPI versioning — every `KPIValue` references the exact formula version active at calculation time.
- **ADR-014**: Single ADR log, short format, never rewritten.
- **ADR-015**: Silent automatic recalculation on source data correction — `id`/`cree_le`/`cree_par` preserved, `recalcule_le` updated. This rule is tested end-to-end, including through the HTTP layer.
- **ADR-021**: Conceptual model → PostgreSQL schema (7 documented gaps, see section 12).
- **ADR-022**: Governance clarification — the multi-client SaaS ambition is a NEW decision milestone, not a continuation of the original fictional-company intent.
- **ADR-023**: `Recommendation` layer designed as a distinct extension of the KPI engine.
- **ADR-024**: Two data categories (internal/external) formally distinguished.
- **ADR-025**: Incremental polling as default ERP sync strategy (over webhooks) — chosen for uniformity across heterogeneous ERPs, not dependent on webhook support.
- **ADR-026**: `Organisation` entity introduced above `Concession` — payer-client isolation must be a schema boundary, not a coding discipline. RLS on `organisation_id` earmarked as the future enforcement mechanism.
- **ADR-027**: SQLAlchemy Core chosen for the Python KPI engine.
- **ADR-028**: (a) Permanent session-resume checklist (mandatory at the start of every new working session — see section 16), (b) rate-limit tolerance requirement for future ERPAdapter.
- **ADR-029**: `Recommendation` formally replaces `AI Advisor` (a pre-written static-text placeholder identified since v2.0 audit) — no dual system.
- **ADR-030**: Confirmation that a validation trigger for `HistoriqueStatut` (see section 12) remains deferred, pending real data to size the rules correctly.
- **ADR-031**: `kpi_definitions.date_champ_periode` added to schema, removing a hardcoded dictionary from `extracteur.py`.
- **ADR-032**: FastAPI construction (Étape 3) — a real UUID/str Pydantic serialization bug was found and fixed via actual execution, not code review.
- **ADR-033/034**: Real deployment verification against Supabase — notable methodological point: ADR-033 explicitly distinguishes verification performed by the AI developer vs. verification performed manually by the project owner (the AI dev sandbox cannot reach `supabase.co`). ADR-034 closes the reserve after full engine+API verification against the real instance.
- **ADR-035/036**: `membres_organisation` table (user↔organisation link), documented gap: no real FK to Supabase's internal `auth.users` table.
- **ADR-037**: ES256/JWKS discovery and full auth module rewrite, confirmed against real Supabase.
- **ADR-038**: Formal closure of the authentication milestone.
- **ADR-039**: RLS behavioral verification script (anon-key access test) + frontend prototype.

**Format**: Décision · Contexte · Justification · Documents impactés · Statut. Follow this format for any new entry.

---

## 5. Completed Features

- 32-table PostgreSQL schema, deployed and tested against real Supabase.
- Python KPI engine (extraction via declarative JSON criteria, aggregation, threshold evaluation, write with dedup/recalc logic, source provenance resolution) — tested against real data with correct results verified independently via manual SQL.
- FastAPI API (5 endpoints: list KPI definitions, trigger calculation, read history, resolve provenance, health check).
- Authentication: Supabase Auth + JWKS/ES256 verification, organisation-based authorization (401/403/200 all tested against real infra).
- Security hardening: `.gitignore` hardened, pre-commit hook blocking secret patterns (tested: a committed connection string with a password was correctly rejected), full Git history + bash_history scanned (gitleaks + manual, zero leaks found), RLS enabled deny-by-default on all 32 tables (declaratively confirmed; behavioral test via anon key in progress — see section 6).
- Private GitHub repository holding all deliverables.

---

## 6. Features Currently In Progress

- **RLS behavioral verification**: `rowsecurity = true` is confirmed on all 32 tables, but a declarative flag is not proof of correct isolation — a wrong or missing policy can either block everything or isolate nothing depending on defaults. **Do not consider RLS "done" until a script that attempts real access via the Supabase `anon` key (not the `postgres` role) returns a confirmed-blocked result.** This is explicitly called out by an independent external review as the one open item on security.
- **Minimal frontend prototype**: a single HTML page (separate from the old prototype HTML file, which must not be touched), implementing: Supabase Auth login → real API call → result display. Local testing (mock JWKS, CORS preflight) has passed. **Final verification against a real Supabase login has not yet been confirmed** (same sandbox network constraint as everywhere else — must be run by the project owner, not the AI dev).
- CORS on the API is currently permissive (`allow_origins=*` or similar) for prototype development — explicitly flagged as temporary technical debt, not yet restricted.

---

## 7. Pending Tasks (not started)

- ERPAdapter implementation (interface only designed, matching `Repository`'s method signatures).
- Connection to any real client ERP.
- `Recommendation` layer implementation (decision to replace `AI Advisor` is made; no code exists yet).
- External market/competitor data collection (n8n workflow envisioned, monthly/quarterly frequency).
- Billing/subscription schema and logic — does not exist at all.
- API hosting (Render or equivalent) — still local/Codespaces only.
- RLS fine-grained policies (per `organisation_id`) — currently deny-by-default with zero policies.
- Frontend component architecture, state management, and full UI — the current prototype is a single test page, not a product interface.
- Automated scheduler for KPI calculation (the old HTML prototype's `Scheduler` has no backend equivalent — calculation is currently a manual/explicit API call).
- Strict whitelist for allowed fields/operators in `source_critere` JSON interpretation (see section 11/12 — security debt, currently low-risk only because KPI definitions are written exclusively by the core team).
- Abstraction layer between future ERPAdapter output and the KPI Engine input (a `publish_event()`-style single function boundary) — cheap to add now, expensive to retrofit later. Recommended by external review; not yet implemented.

---

## 8. Current Priorities (in order)

1. Close the RLS behavioral verification loop (script + real test result).
2. Finalize and confirm the frontend prototype against a real Supabase login (owner-executed).
3. Restrict CORS before any public exposure.
4. Add the ERPAdapter→KPIEngine abstraction boundary (cheap now, expensive later).
5. Connect to the first real pilot ERP client — **the single most important unresolved risk in the entire project.** No amount of additional backend polish reduces this risk; only a real ERP connection does.
6. Only after a pilot client is engaged: enforce the `source_critere` whitelist (becomes urgent the moment anyone outside the core team, including a "trusted" pilot client, can write/edit a KPI definition).

Do NOT prioritize Redis, message queues (Kafka/Celery), or a full frontend framework rewrite before a real pilot client exists — this would be premature infrastructure investment for load that does not yet exist. This was a deliberate, debated decision (see an independent architectural review's initial disagreement and subsequent partial concession on this point).

---

## 9. Folder Structure

```
APEX-AfterSales-Platform/          (GitHub private repo root)
├── api/
│   ├── __init__.py
│   ├── main.py                    (FastAPI app, routes, CORS config)
│   ├── auth.py                    (JWT/JWKS verification, org authorization)
│   └── schemas.py                 (Pydantic request/response models)
├── kpi_engine_py/
│   ├── __init__.py
│   ├── db.py                      (SQLAlchemy engine/connection setup)
│   ├── extracteur.py              (reads source_critere JSON, filters data)
│   ├── calculateur.py             (aggregation: count/sum/avg/ratio)
│   ├── evaluateur.py              (threshold evaluation → status)
│   ├── ecrivain.py                (writes KPIValue, handles dedup/recalc)
│   └── provenance.py              (resolves source record traceability)
├── schema.sql                     (full PostgreSQL schema, 32 tables)
├── test_data.sql                  (minimal integrity test dataset)
├── enrichir_test.sql              (enriched dataset for meaningful KPI calc)
├── test_engine_reel.py            (real end-to-end engine test, no mocks)
├── test_api_reel.py               (real end-to-end API test — check which
│                                    version: some variants generate their
│                                    own mock JWT and override SUPABASE_URL
│                                    to a local mock server; use
│                                    test_api_reel_supabase.py-style variant
│                                    for testing against real Supabase)
├── mock_jwks_server.py            (local JWKS server for offline auth testing)
├── .env.example                   (template: DATABASE_URL, SUPABASE_URL —
│                                    NOT SUPABASE_JWT_SECRET, that pattern
│                                    is obsolete since the ES256 migration)
├── .gitignore                     (hardened: .env, *.key, *credentials*, etc.)
├── .git/hooks/pre-commit           (secret-pattern blocker — must be
│                                    reinstalled manually in any fresh
│                                    Codespace/clone: not versioned by git
│                                    itself by default in this setup)
├── APEX_ADR.md                    (the ADR log — READ FIRST)
├── APEX_CHANGELOG.md              (chronological changelog)
└── README.md
```

**Known repo hygiene issue:** several duplicate/stale zip archives and superseded file versions (e.g. multiple `apex_api_etapeX*.zip`, numbered duplicate ADR/schema files) exist in the repo from iterative uploads. A cleanup pass is recommended but has not been done — always verify you're reading the latest `APEX_ADR.md` / `APEX_CHANGELOG.md` at repo root, not a numbered duplicate.

---

## 10. Coding Standards & Development Principles

These principles were established early and enforced without exception for the entire project so far. **Do not deviate from them.**

- **No big bang.** Every change is split into independently verifiable steps. Never ship a large multi-concern change as one block.
- **Real execution over code review.** Every claim of "it works" must be backed by actually running the code against a real (or realistically representative) database/service — not just reading it. Several real bugs (Decimal/float mismatch, UUID/str Pydantic serialization, ES256 vs HS256) were only caught this way.
- **Non-regression checked before and after every change.** Re-run existing tests, don't just add new ones.
- **Gaps are surfaced explicitly, never silently patched or hidden.** When an implementation must deviate from the conceptual design (e.g. `HistoriqueStatut` without a real FK), document the gap, its consequence, and the alternatives considered — even if you decide not to fix it yet.
- **Tensions with existing decisions are actively surfaced, not silently overridden**, even when a new instruction implies a prior decision "was already X" — verify against the actual ADR log before accepting a premise.
- **Declarative confirmation ≠ behavioral proof**, especially for security controls (see RLS in section 6). Always seek the behavioral test when the stakes are security-relevant.
- **Distinguish who actually verified something.** If a test was run by the AI developer vs. manually by the project owner (due to sandbox network restrictions), say so explicitly rather than presenting both as equivalent.

---

## 11. Security Decisions Already Implemented

- Authentication: Supabase Auth, JWT verified via JWKS (ES256, asymmetric) — no shared secret on the server side to protect.
- Authorization: organisation-membership check on every protected route (403 if the requesting user is not a member of the organisation owning the requested resource).
- `cree_par` on every KPI write is derived from the authenticated token's user id — never a hardcoded default in production paths.
- RLS enabled (deny-by-default, no policies yet) on all 32 tables — see section 6 for the "declarative vs behavioral" caveat.
- Full secret-leak audit performed: current files, complete Git history (manual + gitleaks scan), and shell history — zero leaks found at any point.
- `.gitignore` hardened + pre-commit hook actively blocking secret-looking patterns before they reach any commit (tested with a real connection-string-with-password fixture — correctly rejected).
- Database password has been rotated at least once already after accidental exposure in a chat/screenshot context — rotate again if any credential is ever pasted into an insecure channel.

**Not yet implemented (see sections 7/8/12):** fine-grained RLS policies, CORS restriction, `source_critere` field/operator whitelist, API rate limiting, audit logging, encryption-at-rest policy, key rotation schedule, GDPR/data-retention policy (relevant if targeting the European/Moroccan market with real customer financial data).

---

## 12. Technical Debt

| Item | Description | Urgency |
|---|---|---|
| `HistoriqueStatut.entite_id` | Polymorphic reference with no real FK (only a CHECK on `entite_type`) — an app-level bug could produce orphaned history rows. A validation trigger was designed then explicitly deferred (ADR-021/030), pending real data to size the rules. | Re-evaluate before scaling past prototype/pilot usage. |
| `membres_organisation.user_id` | No real FK to Supabase's internal `auth.users` table (outside the app schema, can't be referenced directly). | Low — documented, accepted. |
| CORS on the API | Currently permissive for dev convenience. | High — must fix before any public deployment. |
| `source_critere` JSON interpretation | No strict whitelist of allowed fields/operators — a theoretical injection vector if KPI definitions are ever writable by anyone outside the core team. Currently low risk (core team only writes definitions). | Becomes urgent the moment a pilot client can edit thresholds/definitions. |
| ERPAdapter↔KPIEngine coupling | Currently would be a direct function call if built naively — no abstraction boundary for a future event/queue-based architecture. | Cheap to fix now, before ERPAdapter exists; expensive after. |
| Repo file hygiene | Duplicate/stale zip archives and numbered file variants cluttering the repo root. | Low, cosmetic — but risk of reading a stale file by mistake. |
| No automated test suite / CI | Tests exist as standalone scripts (`test_engine_reel.py`, `test_api_reel.py`) run manually — no pytest suite, no CI pipeline (e.g. GitHub Actions), no `--no-verify` protection against bypassing the local pre-commit hook. | Medium — recommended before team grows beyond a single AI-assisted contributor. |
| No DB migration tool | Schema changes have been applied by re-running `schema.sql` or manual `ALTER TABLE` via SQL Editor — no Alembic or equivalent. | Medium — will matter once schema changes must be rolled out without data loss on a live client DB. |

---

## 13. Important Constraints

- **The AI developer's sandbox has no network access to `supabase.co` or to this project's private GitHub repo.** Any verification against real Supabase infrastructure, or any file transfer to/from GitHub, must be performed manually by the human project owner. This is a hard, structural constraint, not a temporary inconvenience — plan every "real verification" step assuming a human must execute it.
- **Development sessions are constrained by an AI usage/credit quota** that can run out mid-task without warning. See the mandatory session-resume checklist in section 16 — this exists specifically because of this constraint, after it caused several incomplete-looking deliveries in the past.
- **The project owner is not a professional developer.** Instructions to the human operator must be step-by-step, copy-pasteable, and should not assume familiarity with git internals, terminal conventions, or cloud dashboards beyond what has already been walked through in this project's history.
- **Supabase direct connection requires IPv6** — not available in the dev sandbox nor in GitHub Codespaces used for testing. Always use the Session Pooler (IPv4) connection string.
- **Supabase JWT signing is ES256 by default on this project**, with no legacy HS256 fallback available (confirmed directly in the dashboard — the "Legacy JWT Secret" panel explicitly states it can only verify, not sign, new tokens).

---

## 14. Known Risks

**Critical, unresolved:**
- **No real ERP has ever been connected.** Every assumption in the current architecture (polling frequency, rate-limit tolerance, data shape mapping) is untested against a real external system. This is, by consensus of the project owner, the AI developer, and an independent external architectural review, the single most important remaining risk in the project.
- RLS is enabled but not yet behaviorally proven (see section 6).

**Moderate:**
- No queue/event abstraction yet between a future ERPAdapter and the KPI Engine — if wired as a direct synchronous call, this becomes an expensive refactor once real polling load exists.
- `source_critere` whitelist gap (see section 12) — becomes exploitable the moment KPI definition writes are exposed beyond the core team.
- Single point of technical continuity: development has so far depended entirely on one AI developer instance working in credit-limited sessions with no independent human code review. Any handoff to a new engineer (this document's purpose) should include an actual code read-through, not just this document.
- Repo hygiene: duplicate/stale files could cause a future contributor to edit or deploy from a stale schema/ADR version by mistake.

**Lower priority (explicitly deferred by design, not oversight):**
- No caching layer (Redis) — deliberately not built ahead of real load.
- No message queue (Kafka/Celery) — deliberately not built ahead of a real event producer (see ADR-025's own admission that polling will eventually become one).
- No billing/subscription model — not needed before a pilot client discussion.

---

## 15. Future Roadmap

In dependency order:

1. Close RLS behavioral verification (section 6).
2. Finalize + confirm frontend prototype against real Supabase Auth.
3. Restrict CORS.
4. Add ERPAdapter↔KPIEngine abstraction boundary.
5. **Connect to a first real pilot client's ERP** — build the first concrete `ERPAdapter`. This step will validate or invalidate multiple architectural assumptions made without real data (polling design, rate limits, actual ERP data shapes).
6. Enforce `source_critere` whitelist (before the pilot client can edit definitions).
7. Real API hosting (Render or equivalent).
8. Fine-grained RLS policies (per `organisation_id`) — becomes higher priority immediately if the frontend or any client ever accesses Supabase directly (bypassing the FastAPI backend) rather than exclusively through the API.
9. `Recommendation` layer implementation, replacing `AI Advisor` for real (decision already made, ADR-029; only implementation is pending). Includes deciding rule-based vs. LLM-based generation, and the cost/latency/fallback strategy for the latter if chosen — not yet evaluated.
10. External market/competitor data collection (n8n, low frequency).
11. Billing/subscription model — needed before any real commercial launch.
12. Hardening pass: audit logging, API rate limiting, key rotation policy, data retention / GDPR posture if targeting EU-adjacent markets.

---

## 16. Recommended Next Step

**Do not start new feature work before doing this, in order:**

1. **Session-resume check (mandatory, permanent, per ADR-028):** before touching anything, verify the actual state of the last few files you're about to modify against what the changelog/ADR log claims was "done." Several past sessions were interrupted by credit exhaustion mid-task, leaving documentation slightly ahead of or behind actual code state. A short factual check (a few lines) is enough — don't skip it, and don't over-invest in it either.
2. Confirm the RLS behavioral test result (section 6) — if not done, do it before anything else security-related.
3. Confirm the frontend prototype works against a real Supabase login (owner-executed, per the structural sandbox constraint in section 13).
4. Only then proceed to the roadmap in section 15, starting with CORS restriction and the ERPAdapter abstraction boundary, before beginning real ERP integration work.

---

## 17. Important Files Every Engineer Must Read First

In priority order:

1. **`APEX_ADR.md`** — the full decision log. Non-negotiable first read. Do not make an architectural decision without checking whether it's already been made (or explicitly rejected) here.
2. **`APEX_CHANGELOG.md`** — chronological delivery log, cross-reference against the ADR log for the current actual state.
3. **This file, `PROJECT_HANDOFF.md`.**
4. `schema.sql` — the source of truth for the data model; read alongside the ADR entries documenting its 7+ deliberate gaps vs. the original conceptual model (ADR-021 and follow-ups).
5. `api/auth.py` — read this before touching anything related to authentication; the ES256/JWKS approach is non-obvious and documented reasoning matters (ADR-037).
6. `kpi_engine_py/extracteur.py` — read alongside the `source_critere` security note (sections 11/12) before extending KPI definition capabilities.
7. `.env.example` — confirms current expected environment variables (note: does NOT include `SUPABASE_JWT_SECRET`, which is obsolete since the ES256 migration — if you see code or docs referencing it, they're stale).

---

*This document is the official handoff record for the APEX project. It reflects the real, verified state of the project as of this writing — including what is not yet done — deliberately without a false sense of completeness. Update it as an explicit, reviewed step whenever a major milestone from the roadmap (section 15) is completed, not as an afterthought.*
