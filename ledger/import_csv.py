"""Bank-statement CSV importer for the Phoenix ledger.

Supports common formats out of the box:

- Chase (checking & credit cards): columns 'Transaction Date'/'Posting Date',
  'Description', 'Amount' (negative = expense).
- American Express: columns 'Date', 'Description', 'Amount' (positive =
  charge/expense, negative = payment/refund).
- Generic: any CSV with date, description, amount; specify columns via flags.

Dedupe: each row gets a deterministic external_id =
sha1("{bank}|{account}|{iso_date}|{cents}|{normalized_desc}"). Re-importing
the same statement is a no-op.

Examples:
    python -m ledger.cli import --bank chase   --account checking statement.csv
    python -m ledger.cli import --bank amex    --account platinum  statement.csv
    python -m ledger.cli import --bank generic --account custom \
        --date-col Date --desc-col Memo --amount-col Amt --sign expense-positive \
        statement.csv
"""
from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

from . import store


@dataclass
class BankProfile:
    name: str
    date_col: str
    desc_col: str
    amount_col: str
    # 'expense-negative': negative amount = expense (Chase, most banks)
    # 'expense-positive': positive amount = expense (Amex card statements)
    sign: str
    date_formats: tuple[str, ...] = ("%m/%d/%Y", "%Y-%m-%d", "%m/%d/%y")


PROFILES: dict[str, BankProfile] = {
    "chase": BankProfile(
        name="chase",
        date_col="Transaction Date",
        desc_col="Description",
        amount_col="Amount",
        sign="expense-negative",
    ),
    "amex": BankProfile(
        name="amex",
        date_col="Date",
        desc_col="Description",
        amount_col="Amount",
        sign="expense-positive",
    ),
}


def _norm_desc(s: str) -> str:
    s = s.upper().strip()
    s = re.sub(r"\s+", " ", s)
    return s[:80]


def _parse_date(raw: str, formats: Iterable[str]) -> str:
    raw = raw.strip()
    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    # Last-ditch: ISO prefix like "2026-04-15T..."
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        try:
            datetime.strptime(raw[:10], "%Y-%m-%d")
            return raw[:10]
        except ValueError:
            pass
    raise ValueError(f"Could not parse date: {raw!r}")


def _parse_amount(raw: str) -> float:
    raw = raw.replace(",", "").replace("$", "").strip()
    if raw.startswith("(") and raw.endswith(")"):
        raw = "-" + raw[1:-1]
    return float(raw)


def _external_id(bank: str, account: str, iso_date: str, cents: int, desc: str) -> str:
    key = f"{bank}|{account}|{iso_date}|{cents}|{_norm_desc(desc)}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def _resolve_col(headers: list[str], wanted: str) -> str:
    """Match column name case/whitespace-insensitively, with common aliases."""
    if wanted in headers:
        return wanted
    norm = {h.strip().lower(): h for h in headers}
    if wanted.strip().lower() in norm:
        return norm[wanted.strip().lower()]
    # Aliases for tricky banks
    aliases = {
        "transaction date": ["transaction date", "post date", "posting date", "date"],
        "description": ["description", "memo", "details", "name"],
        "amount": ["amount", "amt", "debit", "credit"],
    }
    for actual_norm, alias_list in aliases.items():
        if wanted.strip().lower() == actual_norm:
            for a in alias_list:
                if a in norm:
                    return norm[a]
    raise KeyError(f"Column {wanted!r} not found in headers: {headers}")


@dataclass
class ImportResult:
    inserted: int = 0
    duplicates: int = 0
    skipped: int = 0
    errors: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


def import_csv(
    path: Path,
    profile: BankProfile,
    *,
    account: str,
    default_pillar: str | None = None,
) -> ImportResult:
    result = ImportResult()
    store.init_db()
    with path.open(newline="", encoding="utf-8-sig") as f, store.connect() as conn:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            result.errors.append("CSV has no header row")
            return result
        try:
            date_col = _resolve_col(reader.fieldnames, profile.date_col)
            desc_col = _resolve_col(reader.fieldnames, profile.desc_col)
            amt_col = _resolve_col(reader.fieldnames, profile.amount_col)
        except KeyError as e:
            result.errors.append(str(e))
            return result

        for i, row in enumerate(reader, start=2):  # header is line 1
            try:
                iso = _parse_date(row[date_col], profile.date_formats)
                amt = _parse_amount(row[amt_col])
                desc = (row[desc_col] or "").strip()
            except (ValueError, KeyError) as e:
                result.errors.append(f"line {i}: {e}")
                result.skipped += 1
                continue

            if amt == 0:
                result.skipped += 1
                continue

            if profile.sign == "expense-negative":
                kind = "expense" if amt < 0 else "income"
            elif profile.sign == "expense-positive":
                kind = "expense" if amt > 0 else "income"
            else:
                result.errors.append(f"line {i}: unknown sign {profile.sign!r}")
                result.skipped += 1
                continue

            magnitude = abs(amt)
            cents = round(magnitude * 100)
            ext_id = _external_id(profile.name, account, iso, cents, desc)

            tx_id = store.add_tx(
                kind=kind,
                amount=magnitude,
                category="imported",
                source=f"{profile.name}:{account}",
                pillar=default_pillar,
                note=desc[:200],
                ts=iso,
                external_id=ext_id,
                conn=conn,
            )
            if tx_id is None:
                result.duplicates += 1
            else:
                result.inserted += 1
    return result


def make_generic_profile(
    *, date_col: str, desc_col: str, amount_col: str, sign: str
) -> BankProfile:
    if sign not in ("expense-negative", "expense-positive"):
        raise ValueError("--sign must be 'expense-negative' or 'expense-positive'")
    return BankProfile(
        name="generic",
        date_col=date_col,
        desc_col=desc_col,
        amount_col=amount_col,
        sign=sign,
    )
