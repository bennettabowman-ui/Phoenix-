# Phoenix — 90-Day Launch Sequence

Realistic, executable, no hype. Revenue numbers are **conservative**, not
goals — beating them is fine; the plan stands either way. Hours are estimates
of *Orchestrator time*; Claude/Phoenix work is unmetered.

The plan has three phases: **Foundation (days 1–30), First Revenue
(31–60), Compounding (61–90)**.

---

## Phase 1 — Foundation (days 1–30)

**Goal:** infrastructure works, one product is shipping, one channel is alive.

### Week 1 — Wire the toolkit
- [ ] Run `ledger init`, log last 30 days of expenses honestly. *Phoenix helps
      categorize.* (1 hr)
- [ ] First portfolio snapshot. Honest numbers. (30 min)
- [ ] Pick one digital product idea (Pillar A) the Orchestrator could defend
      with their real expertise. Write 1-paragraph thesis. (1 hr)
- [ ] Pick one channel for Pillar B (newsletter OR X OR YouTube). One. (15 min)
- [ ] Set monthly burn target & 6-month emergency-fund target in `data/`. (15 min)

**Revenue this week:** $0. **Outputs:** ledger populated, target set.

### Week 2 — Build `phoenix_core/`
- [ ] Implement `phoenix_core/llm.py` (Anthropic wrapper + cost log). *Claude
      writes; Orchestrator reviews.*
- [ ] Add prompt caching to content + research pipelines.
- [ ] Pick name + outline for the digital product. (2 hrs)

**Revenue this week:** $0.

### Week 3 — Draft the product
- [ ] Phoenix drafts every section of the product. Orchestrator edits for voice
      (4 hrs).
- [ ] Phoenix drafts sales-page copy + 5 thread variants for launch.
- [ ] Set up Gumroad / Lemon Squeezy account. (30 min)

**Revenue this week:** $0.

### Week 4 — Soft launch
- [ ] Ship the product (price $29–$49). Soft launch to personal network only.
- [ ] First newsletter post / first X thread (Pillar B). One per week minimum
      from here on.
- [ ] Run `ledger report` + first monthly Wealth Pulse (under 400 words).

**Revenue target (conservative):** **$50–$300** from 2–8 friend-of-friend
sales. This is validation, not income.

---

## Phase 2 — First real revenue (days 31–60)

**Goal:** one paid client OR public product launch with traction.

### Week 5
- [ ] Public launch of the product on relevant communities (HN, Reddit niches,
      Indie Hackers, Product Hunt — pick 2). *Phoenix drafts launch posts.*
- [ ] Define the **single productized service** for Pillar C (e.g., "Custom
      Claude agent — $1,500 fixed scope"). One-page offer.
- [ ] Reach out to 10 warm contacts about the service. (2 hrs)

**Revenue:** $100–$600 product sales. 0–1 service leads.

### Week 6
- [ ] Iterate product based on feedback (Phoenix drafts changelog + email to
      buyers).
- [ ] Pillar D: pick one tiny tool to ship. Phoenix scaffolds MVP this week.
- [ ] First **service proposal** sent if a lead replied.

**Revenue:** $50–$300 product. Pipeline forming.

### Week 7
- [ ] Land first service client OR pivot the offer. Decide based on signal,
      not feelings.
- [ ] Ship Pillar D MVP behind a $0 waitlist or $9/mo paywall.
- [ ] Newsletter / X subscriber count check: should be ≥50.

**Revenue:** $0–$1,500 (if first service client closes).

### Week 8
- [ ] Deliver first service contract (Phoenix does heavy lifting; Orchestrator
      QA's and presents).
- [ ] Pillar E: write the **Investment Policy Statement** (1 page) before any
      capital is moved. No deployment yet.
- [ ] Monthly Wealth Pulse #2.

**Phase-2 cumulative revenue (conservative):** **$200–$2,500**.

---

## Phase 3 — Compounding (days 61–90)

**Goal:** ≥3 pillars producing *something*; rung 2 promotion for ledger and
content.

### Week 9
- [ ] Promote `ledger` and `content` to rung 2: schedule weekly drafts +
      monthly report (cron or GitHub Actions).
- [ ] Second product idea drafted in parallel (Phoenix outlines).
- [ ] Pillar B: switch on a second distribution channel.

### Week 10
- [ ] Land second service client OR raise the price 25% on the existing offer.
- [ ] Pillar D: real users on the micro-SaaS. Goal: 5 paying.
- [ ] Begin DCA into the IPS-defined portfolio (Pillar E) once 3 months of
      expenses are in cash reserves.

### Week 11
- [ ] Second product ships.
- [ ] Pillar F: publish one free framework / essay that demonstrates real
      thinking. Distribution = same channels as Pillar B.
- [ ] Refresh `ARCHITECTURE.md` with what we learned. Constitution amends here
      if reality demands.

### Week 12
- [ ] Quarterly review: which pillar produced per hour spent? Double down on
      top 2, sunset bottom 1.
- [ ] Plan days 91–180 with the same honesty.
- [ ] Monthly Wealth Pulse #3.

**Phase-3 cumulative revenue (conservative):** **$1,500–$7,000** total over
90 days, with monthly run-rate at day 90 of **$500–$3,000/mo** depending on
service-client conversion.

---

## Honest disclaimers

- These ranges assume the Orchestrator already has *some* warm network and
  domain credibility. Cold-start with neither pushes timelines out 30–60 days.
- "Conservative" means **what is reasonable to expect if you execute the plan
  and nothing goes wrong**. Plenty goes wrong. Cut estimates by half on a
  first-time-founder cold start.
- No revenue numbers in this document are guaranteed. They are projections
  used to set expectations and to check whether reality is exceeding or
  missing the model.
- Phoenix tracks **actuals** in `data/phoenix.db` so the next iteration of
  this plan is calibrated, not vibes-based.

## What success at day 90 looks like

- Ledger reflects every dollar in/out. Burn rate known to ±5%.
- ≥1 product live with paying customers.
- ≥1 active distribution channel with weekly cadence.
- ≥1 service offer with at least one closed deal or 3 qualified leads.
- Investment policy written; emergency fund growing.
- A clear, evidence-based picture of which pillars deserve year-1 investment.

That is the foundation. Year 1 compounds it. Year 3 is the constitution's
target. Phoenix earns each rung.
