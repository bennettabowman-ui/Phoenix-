"""Content pipeline: fill a template + topic, draft via Claude, save artifact.

Examples:
    python -m content.pipeline list
    python -m content.pipeline draft --template thread --topic "AI resilience"
    python -m content.pipeline draft --template newsletter \\
        --topic "Why solopreneurs should ship one tool a quarter" \\
        --max-tokens 2500
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from phoenix_core.llm import call as llm_call
from phoenix_core.paths import ARTIFACTS_DIR, ensure_dirs

TEMPLATE_DIR = Path(__file__).parent / "templates"

SYSTEM = (
    "You are Phoenix's drafting assistant. Follow the supplied template "
    "exactly. Produce only the requested artifact — no preamble, no "
    "meta-commentary, no apologies. If the template forbids something, do "
    "not include it. If you must hedge, hedge honestly."
)


def list_templates() -> list[str]:
    return sorted(p.stem for p in TEMPLATE_DIR.glob("*.md"))


def cmd_list(_args) -> int:
    for name in list_templates():
        print(name)
    return 0


def _slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s[:60] or "untitled"


def cmd_draft(args) -> int:
    tpl_path = TEMPLATE_DIR / f"{args.template}.md"
    if not tpl_path.exists():
        print(f"Unknown template: {args.template}. Available: {list_templates()}",
              file=sys.stderr)
        return 2
    template = tpl_path.read_text()
    user_prompt = (
        f"{template.replace('{topic}', args.topic)}\n\n"
        "Now produce the artifact."
    )
    text, meta = llm_call(
        system=SYSTEM,
        user=user_prompt,
        label=f"content/{args.template}",
        max_tokens=args.max_tokens,
    )
    ensure_dirs()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    slug = _slugify(args.topic)
    out = ARTIFACTS_DIR / f"{ts}_{args.template}_{slug}.md"
    header = (
        f"<!-- phoenix artifact\n"
        f"template: {args.template}\n"
        f"topic: {args.topic}\n"
        f"model: {meta['model']}\n"
        f"input_tokens: {meta['input_tokens']}\n"
        f"output_tokens: {meta['output_tokens']}\n"
        f"estimated_usd: {meta['estimated_usd']:.6f}\n"
        f"generated_at: {ts}\n"
        f"-->\n\n"
    )
    out.write_text(header + text)
    print(f"Saved draft -> {out}")
    print(f"Cost ~${meta['estimated_usd']:.4f} | "
          f"tokens in/out: {meta['input_tokens']}/{meta['output_tokens']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="content", description="Phoenix content pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List available templates").set_defaults(func=cmd_list)

    sp = sub.add_parser("draft", help="Draft an artifact from a template + topic")
    sp.add_argument("--template", required=True, help="template stem, e.g. 'thread'")
    sp.add_argument("--topic", required=True)
    sp.add_argument("--max-tokens", type=int, default=2000)
    sp.set_defaults(func=cmd_draft)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
