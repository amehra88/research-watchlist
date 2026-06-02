"""
identity — load config/ticker_identity.yaml (spec §2).

Maps each digest ticker to {name, factset_id, google}. The `google` field is the
ready-to-use Google News RSS query; `factset_id` is the FactSet regional id.
"""
from __future__ import annotations

import os
import yaml

_DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "config", "ticker_identity.yaml",
)


class Identity:
    __slots__ = ("ticker", "name", "factset_id", "google")

    def __init__(self, ticker: str, name: str, factset_id: str, google: str):
        self.ticker = ticker
        self.name = name
        self.factset_id = factset_id
        self.google = google

    def __repr__(self) -> str:
        return f"Identity({self.ticker!r}, name={self.name!r})"


def load_identities(path: str | None = None) -> dict[str, Identity]:
    """Return {TICKER: Identity}. Raises if a required field is missing."""
    path = path or _DEFAULT_PATH
    with open(path) as fh:
        raw = yaml.safe_load(fh) or {}

    out: dict[str, Identity] = {}
    for ticker, fields in raw.items():
        if not isinstance(fields, dict):
            raise ValueError(f"ticker_identity.yaml: {ticker} is not a mapping")
        missing = [k for k in ("name", "factset_id", "google") if not fields.get(k)]
        if missing:
            raise ValueError(f"ticker_identity.yaml: {ticker} missing {missing}")
        out[ticker] = Identity(ticker, fields["name"], fields["factset_id"], fields["google"])
    return out
