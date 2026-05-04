"""Tests for the bank-statement importer: format support + dedupe contract."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ledger import import_csv as imp
from ledger import store


CHASE_CSV = textwrap.dedent("""\
    Transaction Date,Post Date,Description,Category,Type,Amount,Memo
    04/15/2026,04/16/2026,AMAZON.COM,Shopping,Sale,-45.99,
    04/20/2026,04/21/2026,GUMROAD PAYOUT,Income,Credit,127.50,
    04/22/2026,04/22/2026,WHOLE FOODS,Groceries,Sale,-83.21,
""")

AMEX_CSV = textwrap.dedent("""\
    Date,Description,Amount
    04/12/2026,STARBUCKS,5.75
    04/14/2026,DELTA AIR LINES,289.40
    04/30/2026,PAYMENT RECEIVED,-300.00
""")


def _write(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body)
    return p


def test_chase_import_classifies_signs(tmp_ledger, tmp_path):
    csv = _write(tmp_path, "chase.csv", CHASE_CSV)
    result = imp.import_csv(csv, imp.PROFILES["chase"], account="checking")
    assert result.errors == []
    assert (result.inserted, result.duplicates, result.skipped) == (3, 0, 0)

    with store.connect() as c:
        rows = c.execute(
            "SELECT kind, amount FROM transactions ORDER BY ts, id"
        ).fetchall()
    pairs = [(r["kind"], r["amount"]) for r in rows]
    assert pairs == [
        ("expense", 45.99),
        ("income", 127.50),
        ("expense", 83.21),
    ]


def test_amex_import_inverts_sign(tmp_ledger, tmp_path):
    csv = _write(tmp_path, "amex.csv", AMEX_CSV)
    result = imp.import_csv(csv, imp.PROFILES["amex"], account="platinum")
    assert result.errors == []
    assert result.inserted == 3

    with store.connect() as c:
        rows = c.execute(
            "SELECT kind, amount FROM transactions ORDER BY ts, id"
        ).fetchall()
    # On Amex, positive amount is a charge (expense); negative is a payment
    # (income / refund).
    assert (rows[0]["kind"], rows[0]["amount"]) == ("expense", 5.75)
    assert (rows[1]["kind"], rows[1]["amount"]) == ("expense", 289.40)
    assert (rows[2]["kind"], rows[2]["amount"]) == ("income", 300.00)


def test_reimport_is_fully_deduplicated(tmp_ledger, tmp_path):
    """The headline dedupe contract: re-importing the exact same statement
    must produce zero inserts and N duplicates."""
    csv = _write(tmp_path, "chase.csv", CHASE_CSV)
    first = imp.import_csv(csv, imp.PROFILES["chase"], account="checking")
    second = imp.import_csv(csv, imp.PROFILES["chase"], account="checking")

    assert (first.inserted, first.duplicates) == (3, 0)
    assert (second.inserted, second.duplicates) == (0, 3)

    with store.connect() as c:
        n = c.execute("SELECT COUNT(*) AS n FROM transactions").fetchone()["n"]
    assert n == 3, "row count must not grow on idempotent re-import"


def test_dedupe_is_per_account(tmp_ledger, tmp_path):
    """Same CSV under a different --account label must NOT be deduped — those
    are economically different transactions on different cards."""
    csv = _write(tmp_path, "chase.csv", CHASE_CSV)
    a = imp.import_csv(csv, imp.PROFILES["chase"], account="checking")
    b = imp.import_csv(csv, imp.PROFILES["chase"], account="savings")
    assert a.inserted == 3 and b.inserted == 3 and b.duplicates == 0


def test_dedupe_distinguishes_amount_and_description(tmp_ledger, tmp_path):
    """Different amount or different description -> different external_id."""
    base = (
        "Transaction Date,Post Date,Description,Category,Type,Amount,Memo\n"
        "04/15/2026,04/16/2026,AMAZON.COM,Shopping,Sale,-45.99,\n"
    )
    diff_amount = base + "04/15/2026,04/16/2026,AMAZON.COM,Shopping,Sale,-46.00,\n"
    diff_desc = (
        "Transaction Date,Post Date,Description,Category,Type,Amount,Memo\n"
        "04/15/2026,04/16/2026,AMAZON FRESH,Shopping,Sale,-45.99,\n"
    )
    p1 = _write(tmp_path, "a.csv", diff_amount)
    p2 = _write(tmp_path, "b.csv", diff_desc)
    r1 = imp.import_csv(p1, imp.PROFILES["chase"], account="checking")
    r2 = imp.import_csv(p2, imp.PROFILES["chase"], account="checking")
    # First file: 2 distinct rows. Second file: the AMAZON FRESH row is new
    # because the description differs from AMAZON.COM.
    assert r1.inserted == 2
    assert r2.inserted == 1


def test_zero_amount_rows_are_skipped(tmp_ledger, tmp_path):
    csv_body = (
        "Date,Description,Amount\n"
        "04/12/2026,REFUND,0\n"
        "04/13/2026,COFFEE,3.50\n"
    )
    csv = _write(tmp_path, "amex.csv", csv_body)
    r = imp.import_csv(csv, imp.PROFILES["amex"], account="plat")
    assert r.inserted == 1 and r.skipped == 1


def test_generic_profile_with_custom_columns(tmp_ledger, tmp_path):
    csv_body = (
        "When,What,Amt\n"
        "2026-04-15,COFFEE,4.25\n"
        "2026-04-16,REFUND,-4.25\n"
    )
    csv = _write(tmp_path, "g.csv", csv_body)
    profile = imp.make_generic_profile(
        date_col="When", desc_col="What", amount_col="Amt",
        sign="expense-positive",
    )
    r = imp.import_csv(csv, profile, account="custom")
    assert r.inserted == 2 and r.errors == []

    with store.connect() as c:
        rows = c.execute("SELECT kind FROM transactions ORDER BY ts").fetchall()
    assert [r["kind"] for r in rows] == ["expense", "income"]


def test_generic_profile_rejects_invalid_sign():
    with pytest.raises(ValueError):
        imp.make_generic_profile(
            date_col="d", desc_col="x", amount_col="a", sign="weird",
        )


def test_unparseable_date_is_recorded_as_error(tmp_ledger, tmp_path):
    csv_body = (
        "Transaction Date,Post Date,Description,Category,Type,Amount,Memo\n"
        "not-a-date,,COFFEE,,Sale,-4.25,\n"
        "04/15/2026,,COFFEE,,Sale,-3.00,\n"
    )
    csv = _write(tmp_path, "bad.csv", csv_body)
    r = imp.import_csv(csv, imp.PROFILES["chase"], account="checking")
    assert r.inserted == 1
    assert r.skipped == 1
    assert any("line 2" in e for e in r.errors)


def test_external_id_is_stable_for_normalized_descriptions():
    """Whitespace/case changes in the description must not break dedupe."""
    a = imp._external_id("chase", "checking", "2026-04-15", 4599, "AMAZON.COM   ")
    b = imp._external_id("chase", "checking", "2026-04-15", 4599, "amazon.com")
    assert a == b
