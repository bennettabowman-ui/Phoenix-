"""Research agent: turn a topic into a structured opportunity brief.

Output is markdown with explicit fields. The agent is told to refuse to
fabricate evidence — it hedges or marks 'unknown' instead of making up
numbers. Web/data tools are not yet wired in; this is a structured-thinking
pass over the model's training data.

Examples:
    python -m research.agent scan "AI tools for solopreneurs"
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone

from phoenix_core.llm import call as llm_call
from phoenix_core.paths import ARTIFACTS_DIR, ensure_dirs

SYSTEM = """You are Phoenix's research analyst. Produce sober, hedged
opportunity briefs. Never invent statistics. If you don't have a number,
write 'unknown' or give a defensible range with reasoning. If a claim is
based on training data that may be stale, flag it.

Output exactly this markdown structure, no preamble:

# Opportunity: <one-line title>

## Thesis
<2-3 sentence claim about why this could produce revenue for a solo
operator using AI tooling.>

## Evidence (with confidence)
- <bullet> (confidence: low|med|high; basis: training data | reasoning | etc.)
- ...

## Conservative revenue model
- Unit price range: $X – $Y
- Realistic conversion assumption: ...
- Year-1 revenue range (solo operator): $X – $Y
- Show the math in one short paragraph.

## Distribution channels (ranked)
1. ...
2. ...
3. ...

## Top 3 risks
1. ...
2. ...
3. ...

## Next 3 concrete steps (this week)
1. ...
2. ...
3. ...

## Disqualifiers
<When this opportunity should be dropped: e.g. CAC > LTV, regulatory, etc.>
"""


def _slug(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:60] or "topic"


def cmd_scan(args) -> int:
    user = (
        f"Topic to investigate: {args.topic}\n\n"
        "Operator profile: one human + Claude. Houston, TX. Limited starting "
        "capital. Optimizing for durable, ethical, recurring revenue.\n\n"
        "Produce the brief now."
    )
    text, meta = llm_call(
        system=SYSTEM,
        user=user,
        label="research/scan",
        max_tokens=args.max_tokens,
    )
    ensure_dirs()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ARTIFACTS_DIR / f"{ts}_research_{_slug(args.topic)}.md"
    header = (
        f"<!-- phoenix research\n"
        f"topic: {args.topic}\n"
        f"model: {meta['model']}\n"
        f"input_tokens: {meta['input_tokens']}\n"
        f"output_tokens: {meta['output_tokens']}\n"
        f"estimated_usd: {meta['estimated_usd']:.6f}\n"
        f"generated_at: {ts}\n"
        f"NOTE: training-data only; verify any fact before acting.\n"
        f"-->\n\n"
    )
    out.write_text(header + text)
    print(f"Saved brief -> {out}")
    print(f"Cost ~${meta['estimated_usd']:.4f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="research", description="Phoenix research agent")
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("scan", help="Generate an opportunity brief")
    sp.add_argument("topic")
    sp.add_argument("--max-tokens", type=int, default=2500)
    sp.set_defaults(func=cmd_scan)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
