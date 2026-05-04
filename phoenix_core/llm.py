"""Thin Anthropic wrapper with cost logging.

Imports the SDK lazily so the rest of the toolkit (ledger, portfolio) works
with zero dependencies.
"""
from __future__ import annotations

import csv
import os
from datetime import datetime, timezone
from typing import Any

from .paths import LLM_COST_LOG, ensure_dirs

DEFAULT_MODEL = os.environ.get("PHOENIX_MODEL", "claude-sonnet-4-6")

# Conservative public list-price estimates per million tokens (USD). Adjust
# when Anthropic publishes updated pricing. Used only for the local cost log.
_PRICE_PER_MTOK = {
    "claude-opus-4-7":   {"in": 15.0, "out": 75.0},
    "claude-sonnet-4-6": {"in":  3.0, "out": 15.0},
    "claude-haiku-4-5":  {"in":  1.0, "out":  5.0},
}


def _price(model: str) -> dict[str, float]:
    for key, price in _PRICE_PER_MTOK.items():
        if model.startswith(key):
            return price
    return {"in": 3.0, "out": 15.0}


def _log_cost(model: str, in_tok: int, out_tok: int, label: str) -> float:
    p = _price(model)
    cost = (in_tok / 1_000_000) * p["in"] + (out_tok / 1_000_000) * p["out"]
    ensure_dirs()
    new = not LLM_COST_LOG.exists()
    with LLM_COST_LOG.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "label", "model", "in_tok", "out_tok", "usd"])
        w.writerow([
            datetime.now(timezone.utc).isoformat(),
            label, model, in_tok, out_tok, f"{cost:.6f}",
        ])
    return cost


def call(
    *,
    system: str,
    user: str,
    label: str,
    model: str | None = None,
    max_tokens: int = 2000,
) -> tuple[str, dict[str, Any]]:
    """Single-shot Claude call. Returns (text, meta).

    Raises RuntimeError with a friendly message if the SDK or key is missing.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add "
            "your key, or export it in your shell."
        )
    try:
        from anthropic import Anthropic
    except ImportError as e:
        raise RuntimeError(
            "The 'anthropic' package is not installed. Run: "
            "pip install -r requirements.txt"
        ) from e

    model = model or DEFAULT_MODEL
    client = Anthropic(api_key=api_key)
    resp = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    in_tok = getattr(resp.usage, "input_tokens", 0)
    out_tok = getattr(resp.usage, "output_tokens", 0)
    cost = _log_cost(model, in_tok, out_tok, label)
    return text, {
        "model": model,
        "input_tokens": in_tok,
        "output_tokens": out_tok,
        "estimated_usd": cost,
    }
