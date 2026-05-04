"""Net-worth and allocation tracker. Manual input, JSON-backed snapshots.

Examples:
    python -m portfolio.tracker set cash 5000
    python -m portfolio.tracker set brokerage 12000
    python -m portfolio.tracker snapshot
    python -m portfolio.tracker report
    python -m portfolio.tracker history
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from typing import Any

from phoenix_core.paths import PORTFOLIO_JSON, ensure_dirs

DEFAULT_BUCKETS = [
    "cash", "brokerage", "retirement", "crypto", "real_estate", "other",
]


def _load() -> dict[str, Any]:
    ensure_dirs()
    if not PORTFOLIO_JSON.exists():
        return {"current": {b: 0.0 for b in DEFAULT_BUCKETS}, "snapshots": []}
    return json.loads(PORTFOLIO_JSON.read_text())


def _save(state: dict[str, Any]) -> None:
    ensure_dirs()
    PORTFOLIO_JSON.write_text(json.dumps(state, indent=2))


def cmd_set(args) -> int:
    state = _load()
    state["current"][args.bucket] = float(args.amount)
    _save(state)
    print(f"Set {args.bucket} = ${args.amount:,.2f}")
    return 0


def cmd_snapshot(_args) -> int:
    state = _load()
    snap = {"date": date.today().isoformat(), **state["current"]}
    state["snapshots"].append(snap)
    _save(state)
    total = sum(v for k, v in snap.items() if k != "date")
    print(f"Snapshot {snap['date']}: net worth ${total:,.2f}")
    return 0


def cmd_report(_args) -> int:
    state = _load()
    cur = state["current"]
    total = sum(cur.values()) or 1e-9
    print("== Portfolio (current) ==")
    for b in sorted(cur, key=lambda k: -cur[k]):
        v = cur[b]
        pct = 100 * v / total
        print(f"  {b:<12} ${v:>12,.2f}  {pct:>5.1f}%")
    print(f"  {'TOTAL':<12} ${sum(cur.values()):>12,.2f}")
    return 0


def cmd_history(_args) -> int:
    state = _load()
    if not state["snapshots"]:
        print("No snapshots yet. Run: python -m portfolio.tracker snapshot")
        return 0
    print(f"{'date':<12} {'net_worth':>14}")
    for s in state["snapshots"]:
        total = sum(v for k, v in s.items() if k != "date")
        print(f"{s['date']:<12} ${total:>12,.2f}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="portfolio", description="Phoenix portfolio tracker")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("set", help="Set the current value of a bucket")
    sp.add_argument("bucket", help=f"one of: {', '.join(DEFAULT_BUCKETS)} (or any custom name)")
    sp.add_argument("amount", type=float)
    sp.set_defaults(func=cmd_set)

    sub.add_parser("snapshot", help="Append a dated snapshot of current values"
                   ).set_defaults(func=cmd_snapshot)
    sub.add_parser("report", help="Show current allocation"
                   ).set_defaults(func=cmd_report)
    sub.add_parser("history", help="Show historical net worth"
                   ).set_defaults(func=cmd_history)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
