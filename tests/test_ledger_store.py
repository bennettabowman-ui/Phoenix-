"""Tests for ledger.store: insert, dedupe contract, reporting."""
from __future__ import annotations

import pytest

from ledger import store


def test_add_income_and_expense(tmp_ledger):
    assert store.add_tx(kind="income", amount=39.0, category="sales") is not None
    assert store.add_tx(kind="expense", amount=1500.0, category="rent") is not None
    rep = store.report(2026, 5)  # current month for the test environment
    # Don't assume current month — check via a wide-window report instead.
    with store.connect() as c:
        rows = c.execute("SELECT kind, SUM(amount) AS total FROM transactions GROUP BY kind").fetchall()
    by_kind = {r["kind"]: float(r["total"]) for r in rows}
    assert by_kind == {"income": 39.0, "expense": 1500.0}


def test_negative_amount_rejected(tmp_ledger):
    with pytest.raises(ValueError):
        store.add_tx(kind="income", amount=-1, category="x")


def test_invalid_kind_rejected(tmp_ledger):
    with pytest.raises(ValueError):
        store.add_tx(kind="transfer", amount=1, category="x")


def test_external_id_dedupes(tmp_ledger):
    """The dedupe contract: a second insert with the same external_id is a
    no-op and returns None (rather than raising). Different external_id with
    otherwise identical fields inserts normally."""
    first = store.add_tx(
        kind="expense", amount=10.0, category="imported",
        ts="2026-04-15", external_id="abc123",
    )
    assert first is not None

    dupe = store.add_tx(
        kind="expense", amount=10.0, category="imported",
        ts="2026-04-15", external_id="abc123",
    )
    assert dupe is None, "duplicate external_id must return None"

    distinct = store.add_tx(
        kind="expense", amount=10.0, category="imported",
        ts="2026-04-15", external_id="abc124",
    )
    assert distinct is not None and distinct != first


def test_null_external_id_does_not_dedupe(tmp_ledger):
    """The unique index is partial (WHERE external_id IS NOT NULL), so manual
    entries without an external_id can repeat freely."""
    a = store.add_tx(kind="expense", amount=5, category="coffee")
    b = store.add_tx(kind="expense", amount=5, category="coffee")
    assert a is not None and b is not None and a != b


def test_targets_and_runway_unset(tmp_ledger):
    assert store.get_target("cash_on_hand") is None
    store.set_target("cash_on_hand", 8000)
    assert store.get_target("cash_on_hand") == 8000.0
    # Runway is None until at least one full prior month of expenses exists.
    assert store.runway_months() is None
