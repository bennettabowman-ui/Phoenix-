"""Phoenix ledger CLI.

Examples:
    python -m ledger.cli init
    python -m ledger.cli add-income --source "gumroad sale" --amount 39 --pillar A
    python -m ledger.cli add-expense --category rent --amount 1500
    python -m ledger.cli set-target cash_on_hand 8000
    python -m ledger.cli report --month current
    python -m ledger.cli export --csv data/ledger_export.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import date
from pathlib import Path

from . import store
from . import import_csv as imp


def _resolve_month(arg: str) -> tuple[int, int]:
    today = date.today()
    if arg in ("current", "this", ""):
        return today.year, today.month
    if arg == "previous" or arg == "last":
        m = today.month - 1 or 12
        y = today.year - (1 if today.month == 1 else 0)
        return y, m
    try:
        y_str, m_str = arg.split("-")
        return int(y_str), int(m_str)
    except ValueError as e:
        raise SystemExit(f"--month must be 'current', 'last', or YYYY-MM (got {arg!r})") from e


def cmd_init(_args) -> int:
    store.init_db()
    print(f"Ledger initialized at {store.LEDGER_DB}")
    return 0


def _add(kind: str, args) -> int:
    tx_id = store.add_tx(
        kind=kind,
        amount=args.amount,
        category=args.category or ("uncategorized" if kind == "expense" else "sales"),
        source=args.source,
        pillar=args.pillar,
        note=args.note,
        ts=args.date,
    )
    print(f"Recorded {kind} #{tx_id}: ${args.amount:.2f} [{args.category or 'uncategorized'}]")
    return 0


def cmd_report(args) -> int:
    y, m = _resolve_month(args.month)
    rep = store.report(y, m)
    print(f"== Phoenix ledger {rep['period']} ==")
    print(f"  Income:  ${rep['income']:>10,.2f}")
    print(f"  Expense: ${rep['expense']:>10,.2f}")
    print(f"  Net:     ${rep['net']:>10,.2f}")
    if rep["by_category"]:
        print("\n  Breakdown:")
        for r in rep["by_category"]:
            print(f"    {r['kind']:<7} {r['category']:<20} ${float(r['total']):>10,.2f}")
    runway = store.runway_months()
    if runway is not None:
        print(f"\n  Estimated runway: {runway:.1f} months "
              "(cash_on_hand / avg 3-mo burn)")
    else:
        print("\n  Runway: set 'cash_on_hand' target and log "
              "≥1 full month of expenses to compute.")
    return 0


def cmd_set_target(args) -> int:
    store.set_target(args.key, args.value)
    print(f"Target {args.key} = {args.value}")
    return 0


def cmd_export(args) -> int:
    with store.connect() as c:
        rows = c.execute(
            "SELECT id, ts, kind, amount, category, source, pillar, note "
            "FROM transactions ORDER BY ts, id"
        ).fetchall()
    with open(args.csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "date", "kind", "amount", "category", "source", "pillar", "note"])
        for r in rows:
            w.writerow([r[k] for k in r.keys()])
    print(f"Exported {len(rows)} rows to {args.csv}")
    return 0


def cmd_import(args) -> int:
    path = Path(args.path)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        return 2
    if args.bank == "generic":
        missing = [n for n in ("date_col", "desc_col", "amount_col", "sign")
                   if getattr(args, n) is None]
        if missing:
            print(f"--bank generic requires: {', '.join('--' + m.replace('_','-') for m in missing)}",
                  file=sys.stderr)
            return 2
        profile = imp.make_generic_profile(
            date_col=args.date_col,
            desc_col=args.desc_col,
            amount_col=args.amount_col,
            sign=args.sign,
        )
    else:
        profile = imp.PROFILES[args.bank]
    result = imp.import_csv(
        path, profile, account=args.account, default_pillar=args.pillar
    )
    print(f"Imported from {args.bank}:{args.account}")
    print(f"  inserted:   {result.inserted}")
    print(f"  duplicates: {result.duplicates}")
    print(f"  skipped:    {result.skipped}")
    if result.errors:
        print("  errors:")
        for e in result.errors[:10]:
            print(f"    - {e}")
        if len(result.errors) > 10:
            print(f"    ... and {len(result.errors) - 10} more")
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ledger", description="Phoenix ledger CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Initialize the ledger database").set_defaults(func=cmd_init)

    for kind in ("income", "expense"):
        sp = sub.add_parser(f"add-{kind}", help=f"Record {kind}")
        sp.add_argument("--amount", type=float, required=True)
        sp.add_argument("--category")
        sp.add_argument("--source")
        sp.add_argument("--pillar", choices=list("ABCDEFG"))
        sp.add_argument("--note")
        sp.add_argument("--date", help="YYYY-MM-DD (default today)")
        sp.set_defaults(func=lambda a, k=kind: _add(k, a))

    sp = sub.add_parser("report", help="Monthly report")
    sp.add_argument("--month", default="current",
                    help="'current', 'last', or YYYY-MM")
    sp.set_defaults(func=cmd_report)

    sp = sub.add_parser("set-target", help="Set a numeric target (e.g. cash_on_hand)")
    sp.add_argument("key")
    sp.add_argument("value", type=float)
    sp.set_defaults(func=cmd_set_target)

    sp = sub.add_parser("export", help="Export all transactions to CSV")
    sp.add_argument("--csv", default="data/ledger_export.csv")
    sp.set_defaults(func=cmd_export)

    sp = sub.add_parser("import", help="Import a bank/card CSV statement")
    sp.add_argument("path", help="Path to CSV file")
    sp.add_argument("--bank", choices=["chase", "amex", "generic"], default="chase")
    sp.add_argument("--account", required=True,
                    help="A short label for this account, e.g. 'checking', 'amex-plat'")
    sp.add_argument("--pillar", choices=list("ABCDEFG"),
                    help="Default pillar for income rows")
    # Generic-only flags:
    sp.add_argument("--date-col")
    sp.add_argument("--desc-col")
    sp.add_argument("--amount-col")
    sp.add_argument("--sign", choices=["expense-negative", "expense-positive"])
    sp.set_defaults(func=cmd_import)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
