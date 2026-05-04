# Resilience Stack — Product Outline (v1)

> Status: **draft, awaiting Orchestrator approval.** No public commitments
> until this is signed off.

## One-line promise

A practical kit for thinking and operating with high agency when things get
weird — without the doom theater.

## Target user (who actually buys this in 2026)

The Resilience Stack is for one specific person. We will not pretend it's
for everyone.

**Primary buyer — "the calm operator":**
- Age 28–55, knowledge worker or solopreneur, technically comfortable.
- Already uses AI tools weekly. Reads Stratechery / The Diff / Astral Codex
  Ten / individual Substacks. Probably owns a Notion or Obsidian setup.
- Has watched the last three years (pandemic, banking wobbles, war, AI
  shock waves) and concluded: *the future is non-stationary; my decision
  quality matters more than my plan.*
- Repelled by both naïve techno-optimism and prepper-aesthetic doom.
- Is willing to pay for a clear-headed system the way they'd pay for a
  good knife or a good chair.

**Secondary buyer — "the household captain":**
- Same psychographic, but optimizing for a partner + kids or a small
  community. Buys the household tier.

**Explicitly not for:** people looking for bunker porn, end-times
prophecy, financial-survival-investment hype, or politicized prepping.

## Core modules

The product is **modular** by design. Each module stands alone; together
they compound. Eight modules in v1:

### 1. The Resilience Operating System (foundation)
A 25-page essay defining the philosophy: high agency over hoarding,
decision quality over prediction, networks over fortresses. Sets the
voice and frame for the whole product so buyers don't drift into doomerism.

### 2. The Capability Audit
A structured worksheet (Notion + printable) that maps:
- What you can do alone, today, with no internet.
- What your immediate household can do.
- What your 1st-degree network can do.
- What you depend on but cannot replicate.
The output is a single page: your current resilience posture.

### 3. The Dependency Inventory
A structured Notion database template:
- Every critical dependency (electricity, water, banking, prescription
  meds, employer, single-platform income, single cloud provider, etc.).
- Per dependency: outage horizon you can survive, current fallback,
  cost to upgrade fallback, priority.
Includes a 1-page "fallback budget" template.

### 4. The Five Playbooks
Each playbook is a 6–10 page operational guide for a specific scenario:
1. **Income halves overnight.** (90-day cash + revenue plan.)
2. **A platform you depend on bans you.** (Identity & audience portability.)
3. **Internet flakes for a week.** (Offline workflow continuity.)
4. **Household emergency / health event.** (Decisions, comms, money.)
5. **Local disruption (weather, grid, civic).** (72-hour to 30-day ladder.)
Each playbook ends with a one-page **decision card** to print and stash.

### 6. The Skill-Stack Planner
A 90-day skill-acquisition planner template focused on offline-deliverable
skills. Includes a curated "ten skills worth a weekend each" list with
honest disclaimers about what one weekend actually buys you.

### 7. The Prompt Library
~80 prompts grouped by playbook:
- **Decision-making prompts** (red-team a plan; pre-mortem; steelman the
  opposite).
- **Audit prompts** (interview-yourself prompts for the capability /
  dependency exercises).
- **Operations prompts** (drafting the awkward email, the ban-appeal
  letter, the family briefing).
- **Resilience-research prompts** (structured templates for evaluating
  one's own hot takes).
Each prompt is model-agnostic (works on any frontier LLM) and ships with a
"why this works" sentence.

### 8. The Quarterly Review Ritual
A 90-minute quarterly review template that walks the buyer through:
- Re-running the Capability Audit.
- Updating the Dependency Inventory.
- Logging "weirdness signals" they noticed this quarter.
- Adjusting one fallback.
- Choosing one skill to develop.
This is the durability mechanism — it's how the product keeps producing
value six months in.

> **Design rule:** every module must work on paper. The Notion stuff is a
> convenience layer, not the core. If the internet is down, the printed
> PDFs and decision cards still run.

## Pricing tiers

| Tier | Price | Audience | What's inside |
|---|---|---|---|
| **Resilience Stack — Solo** | **$49 one-time** | Default tier. Individual operator. | All 8 modules. Notion duplicate template. Print-ready PDF (~120 pages). Prompt library (.md and Notion). |
| **Resilience Stack — Household** | **$99 one-time** | Couples, small families, small co-ops. | Solo tier + household-edition worksheets, family-comms playbook, 3 additional Notion seats, "household captain" decision cards. |
| **Resilience Stack — Quarterly Membership** | **$79/yr add-on** (any tier) | Buyers who want continued evolution. | New playbook every quarter; updated prompt library; quarterly review livestream / async briefing; private "operator log" newsletter (subscriber-only). |
| **Group License** | **$299 one-time** | Communities, study groups, mutual-aid co-ops up to 15 members. | Solo tier + facilitator guide for group quarterly review. |

**Refund policy:** 30 days, no questions asked. Plain English in the
receipt email.

**Pricing rationale:**
- $49 anchors against a quality book ($25–35), enough margin to fund
  iteration, low enough that the recommendation friction is small.
- The **$79/yr membership is the long-term engine** — it converts a one-time
  product into a quarterly relationship without locking the buyer's data
  to us.
- Group license is intentionally simple, not enterprise-y.

## Delivery format

1. **Notion duplicate template** (single click) — interactive workspace
   containing all worksheets, databases, and the prompt library.
2. **PDF master document** (~120 pages, designed for both screen and
   print) — the canonical artifact, model-/platform-independent.
3. **Print-ready decision cards** — five 4×6" cards, one per playbook,
   designed to be wallet-stashable.
4. **Prompt pack** — `.md` and `.json` exports of the prompt library so
   buyers can drop it into any LLM front-end they already use.
5. **`README` and update log** — version-stamped, so members can see what's
   new.

**Delivery mechanics:**
- Sold via Gumroad (primary) and a self-hosted backup link as a Pillar G
  hedge.
- Payment processor: Gumroad → Stripe.
- Email delivery handled by Gumroad. Membership tier handled via a private
  Beehiiv newsletter list keyed to the buyer's email.

## v1 → v2 roadmap (next 60 days)

### v1.0 — ship date target: **Day 28** of the 90-day plan
Modules included: 1, 2, 3, 4 (playbooks 1, 2, 4 only — i.e., income halve,
platform ban, household emergency). Prompt library at ~50 prompts.
Decision cards: 3 of 5 finalized. PDF + Notion template.
**This is the soft-launch product.** $49 / $99 tiers only. Membership
not yet open.

### v1.1 — ship date target: **Day 45**
- Adds remaining playbooks (3 and 5: internet flake, local disruption).
- Decision cards complete (5 of 5).
- Prompt library expands to ~80.
- Quarterly review module (#8) added.
- **Public launch.** Indie Hackers, Hacker News, niche subreddits.

### v2.0 — ship date target: **Day 60**
- Skill-Stack Planner (#6) shipped.
- Membership tier opens. First quarterly briefing scheduled.
- Group License available.
- One field-tested case study added to the front matter (anonymized;
  buyer-volunteered).

### v2.x and beyond (parked, not promised)
- Audio companion (read-aloud playbooks).
- Local-language translations (community-driven).
- Optional integrations: Obsidian template port, plain-text-only
  zip for the no-Notion crowd.

## What this product is **not**
- Not a bunker manual, weapons guide, or political tract.
- Not financial advice (we say so explicitly in module 1).
- Not a productivity system pretending to be resilience theater.
- Not vendor-locked: every essential artifact works without Notion or any
  specific LLM.

## Defensibility

The moat is **voice + judgment**, not features. The Resilience Stack
should read like nothing else on the market because:
- It refuses doomer aesthetics *and* refuses techno-optimism's hand-waving.
- It treats the buyer as an adult.
- It is opinionated about decision quality, not gear.
- It comes from an operator who is using it themselves.

That voice is the thing competitors cannot copy quickly. Everything else is
table stakes.
