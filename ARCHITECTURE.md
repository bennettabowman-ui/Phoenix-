# Phoenix — Architecture

This document defines the realistic technical and operational architecture of
Phoenix. It is honest about what is automated, what is human-in-the-loop, and
what is still aspirational.

## Design tenets

1. **Composable scripts > monolithic agent.** Each component does one thing
   well and is callable from CLI, cron, or a higher-level orchestrator.
2. **Local-first data.** Ledger, portfolio, and content drafts live in plain
   files / SQLite in this repo. No third-party SaaS lock-in for core records.
3. **Claude as the brain, scripts as the hands.** LLM calls go through a thin
   wrapper that handles retries, cost tracking, and prompt caching.
4. **Progressive autonomy.** Each maturity rung must be earned. No component
   gets scheduled execution until it has produced correct output by hand.
5. **Auditable.** Every LLM-generated artifact is saved with the prompt,
   model, and timestamp. Every financial entry has a source.

## Maturity ladder

| Rung | Capability | Trust level |
|------|-----------|-------------|
| 1 | **Toolkit.** CLIs the human runs on demand. | None — human reviews everything. |
| 2 | **Daily loops.** Scheduled scripts (cron / GitHub Actions) drafting content, scanning markets, snapshotting portfolio. Drafts await human approval. | Low — human approves each output. |
| 3 | **Pillar operators.** Dedicated agents per revenue pillar (content, products, services). Auto-publish low-risk artifacts; flag high-risk for review. | Medium — bounded autonomy, capped spend. |
| 4 | **Treasury & reinvestment.** Autonomous reinvestment within written rules; tax/CPA integration; multi-pillar dashboard. | High — within tight rule boxes. |
| 5 | **Doomsday-resilient.** Offline fallback streams, encrypted backups, multi-region keys, analog capabilities. | High + survivable. |

We start at Rung 1 and only promote a component when it has demonstrably
produced correct outputs in manual mode for a sustained period.

## System diagram (current — Rung 1)

```
┌───────────────────────────────────────────────────────────┐
│                     Orchestrator (human)                  │
└─────────────┬───────────────────────────────┬─────────────┘
              │ runs CLIs                     │ reviews drafts
              ▼                               ▼
┌────────────────────────┐         ┌────────────────────────┐
│  Local tools (stdlib)  │         │  Claude-powered tools  │
│  - ledger/ (SQLite)    │         │  - content/pipeline    │
│  - portfolio/tracker   │         │  - research/agent      │
└──────────┬─────────────┘         └──────────┬─────────────┘
           │                                  │
           ▼                                  ▼
   data/phoenix.db                   data/artifacts/*.md
   data/portfolio.json               (every draft saved with
                                      prompt + model + ts)
```

## Components

### `ledger/` — bookkeeping
- SQLite-backed double-entry-lite ledger.
- Tables: `accounts`, `transactions`, `categories`.
- CLI: `init`, `add-income`, `add-expense`, `report`, `export`.
- Outputs: monthly burn rate, runway estimate, category breakdown, CSV export
  for an accountant.
- **Promotion criteria** to rung 2: import-from-CSV (bank statements) and
  scheduled monthly report.

### `portfolio/` — net worth & allocation
- JSON-backed snapshots: `data/portfolio.json` is a list of dated snapshots.
- Tracks: cash, brokerage, retirement, crypto, real-estate, other.
- CLI: `snapshot`, `set`, `report`, `history`.
- Outputs: total net worth, allocation %, drift from target, history table.
- **Promotion criteria** to rung 2: API pull from Plaid / brokerage / on-chain.

### `content/` — drafting pipeline
- Templates in `content/templates/*.md` for: thread, newsletter, product
  description, sales page, video script.
- `content/pipeline.py` reads a template, fills a topic, calls Claude, saves
  draft + prompt + metadata to `data/artifacts/`.
- Drafts are **never published automatically** at rung 1. The human reviews
  and posts.
- **Promotion criteria** to rung 2: A/B variant generation + scheduled queue.

### `research/` — opportunity scanner
- `research/agent.py` takes a query, calls Claude with structured output, saves
  a markdown summary with: opportunity, evidence (links if web tool used), TAM
  estimate, distribution channels, conservative revenue range, top 3 risks,
  next 3 concrete steps.
- **Promotion criteria** to rung 2: integrate web search / RSS / X API; weekly
  scheduled scan.

### Shared: `phoenix_core/` (planned, week 2)
- `llm.py` — thin Anthropic SDK wrapper with prompt caching, retries, and
  cost logging to `data/llm_costs.csv`.
- `paths.py` — repo-relative path helpers.
- `safety.py` — guardrails: spend caps, publication caps, redaction.

## Six revenue pillars — as real, executable projects

Each pillar is described as **what we actually do**, not what runs itself.

### Pillar A — Signature Digital Products
- **Real project:** ship one $29–$79 digital product on Gumroad / Lemon Squeezy
  in 30 days. Topic: an asset the Orchestrator can defend (e.g., AI resilience
  toolkit, agent-building handbook).
- **Phoenix's role:** Claude drafts outline, copy, sales page, and prompt-pack
  contents. Orchestrator reviews voice, ships.
- **Conservative target:** 10 sales × $39 = $390 in month 1 with zero ad spend.

### Pillar B — Audience Flywheel
- **Real project:** one newsletter (Substack / Beehiiv) + one platform (X or
  YouTube). 2 posts/week.
- **Phoenix's role:** content pipeline drafts; Orchestrator edits & posts;
  ledger tracks subscriber count weekly.
- **Conservative target:** 200 subscribers in 90 days. Monetization deferred
  until 1k subs.

### Pillar C — AI Service Agency
- **Real project:** offer a single, productized service (e.g., "Custom Claude
  agent for your business — $1,500 fixed"). Land 1 client in first 60 days
  through warm network.
- **Phoenix's role:** Claude drafts proposals, scopes, and delivers code
  artifacts. Orchestrator handles client calls.
- **Conservative target:** 1 client × $1,500 in 90 days.

### Pillar D — Micro-SaaS / Tools
- **Real project:** ship one tiny paid tool ($5–$20/mo) solving one problem
  the Orchestrator personally has. Hosted cheaply (Cloudflare Workers / Fly).
- **Phoenix's role:** Claude codes the MVP; Orchestrator names, prices, ships.
- **Conservative target:** 5 paying users × $9 = $45 MRR by day 90 (validation,
  not income).

### Pillar E — Smart Capital Allocation
- **Real project:** define a **written investment policy statement (IPS)**
  before deploying $1. Then automate a monthly DCA into a 3-fund portfolio.
- **Phoenix's role:** portfolio tracker; rebalance reminder; tax-lot notes.
- **Conservative target:** none in revenue. Goal is to not lose money and to
  build the habit + 6-month emergency fund first.

### Pillar F — IP & Licensing
- **Real project:** publish one free framework / essay that is genuinely
  useful and licensable. Defer monetization.
- **Phoenix's role:** drafting, distribution; track inbound interest.

### Pillar G — Offline Backup
- **Real project:** identify one local skill-based service the Orchestrator
  could deliver in a week without internet (consulting, workshop, tutoring).
  Document the playbook. Don't run it yet.
- **Phoenix's role:** documentation + contact list maintenance.

## Operating loop

**Daily (5 min, human):** glance at ledger; capture any new income/expense.
**Weekly (45 min, human + Phoenix):** review drafted content, ship at least
one piece per active pillar; portfolio snapshot.
**Monthly (90 min, human + Phoenix):** generate Wealth Pulse report from
ledger + portfolio data; review pillars; update `LAUNCH_90_DAY.md` actuals
column.

## Risks & how we contain them

| Risk | Mitigation |
|------|------------|
| LLM output is wrong / hallucinated | Every artifact human-reviewed at rung 1; saved with metadata for audit. |
| API key leak | `.env` gitignored; key never in code; rotate quarterly. |
| Spend creep on LLM costs | `phoenix_core/llm.py` logs every call; daily cap configurable. |
| Solo bus-factor (Orchestrator unavailable) | All data is plain files in git; any successor can read it. |
| Platform dependence | Local-first storage; pillars span ≥3 distribution channels by rung 3. |
| Tax/legal | Ledger flags any transaction > threshold for CPA review at year-end. |

## What this architecture is **not**

- It is not a trading bot. It does not place trades.
- It is not a payment processor. It records what you tell it.
- It is not autonomous. At rung 1, nothing runs without you.
- It is not a get-rich engine. It is a compounding system that needs years.
