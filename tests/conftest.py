"""Shared pytest fixtures: redirect ledger storage to a temp DB per test."""
from __future__ import annotations

import pytest

from ledger import store
from phoenix_core import paths


@pytest.fixture
def tmp_ledger(tmp_path, monkeypatch):
    """Point the ledger at a temp SQLite DB and an isolated data dir."""
    db = tmp_path / "phoenix.db"
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()

    # The store module captured LEDGER_DB at import; patch both bindings.
    monkeypatch.setattr(paths, "LEDGER_DB", db, raising=True)
    monkeypatch.setattr(store, "LEDGER_DB", db, raising=True)
    monkeypatch.setattr(paths, "DATA_DIR", tmp_path, raising=True)
    monkeypatch.setattr(paths, "ARTIFACTS_DIR", artifacts, raising=True)

    store.init_db()
    return db
