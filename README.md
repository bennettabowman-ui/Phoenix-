# Phoenix

> A practical, evolving agent stack for building durable, diversified income —
> so the Orchestrator can stop thinking about money and focus on humanity-scale
> work.

## Vision

Phoenix is a personal financial operating system. The long-term goal: enough
reliable, ethical, scalable income across at least six uncorrelated pillars
that the Orchestrator never has to think about money again. See
[`PHOENIX.md`](./PHOENIX.md) for the full guiding constitution.

## Current Reality

Day zero. This repo contains:

- **Constitution** (`PHOENIX.md`) — the north star.
- **Architecture** (`ARCHITECTURE.md`) — the realistic agent-stack design and
  maturity ladder.
- **90-day plan** (`LAUNCH_90_DAY.md`) — concrete weekly milestones.
- **Tools** — small, working components:
  - `ledger/` — income/expense ledger CLI (SQLite + Python stdlib).
  - `portfolio/` — net-worth and allocation tracker.
  - `content/` — content pipeline scaffold (templates + Claude-powered drafter).
  - `research/` — research agent that pulls + summarizes opportunities.

No revenue yet. No fake dashboards. Everything in this repo either runs or is
labeled clearly as a plan.

## Quick start

```bash
# 1. (Optional) put your Anthropic API key in a .env or shell env
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Install minimal deps (only needed for content/research agents)
pip install -r requirements.txt

# 3. Initialize the ledger
python -m ledger.cli init
python -m ledger.cli add-income --source "first sale" --amount 0 --category seed

# 4. Track expenses / project burn
python -m ledger.cli add-expense --category rent --amount 1500
python -m ledger.cli report --month current

# 5. Snapshot your portfolio
python -m portfolio.tracker snapshot

# 6. Draft content from a template
python -m content.pipeline draft --template thread --topic "AI resilience"

# 7. Research an opportunity
python -m research.agent scan "AI tools for solopreneurs"
```

The ledger and portfolio tracker run with **no API key** — pure stdlib.
The content and research tools require `ANTHROPIC_API_KEY`.

Run the test suite:

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -q
```

## Roadmap

The architecture defines five maturity rungs. We are at **Rung 1**.

| Rung | Name | Status |
|------|------|--------|
| 1 | Toolkit (manual + Claude-assisted) | **now** |
| 2 | Daily-loop agents (scheduled scripts, dashboards) | next |
| 3 | Multi-pillar revenue (≥3 pillars producing) | quarter 2 |
| 4 | Six pillars + autonomous reinvestment | year 1 |
| 5 | FU-money resilience (12–18 mo runway, analog fallback) | year 3 |

See [`LAUNCH_90_DAY.md`](./LAUNCH_90_DAY.md) for the next 90 days in detail.

## Principles

- **No theater.** Every "automated" claim is backed by code that runs.
- **Reputation is a moat.** Nothing scammy, illegal, or low-integrity.
- **Compound, don't sprint.** Small, durable steps beat heroic launches.
- **Time > money.** Optimize for the Orchestrator's attention, always.
