#!/usr/bin/env python3
"""Shared Postgres connection for the chunk store (step 5b managed-pgvector).

DATABASE_URL resolution mirrors embed.py's key loading: prefer the value already
in the environment, else read /root/podcasts/.env (this system's canonical secret
store — the same file embed.py reads GEMINI_API_KEY from, and the news-digest
crons `set -a && . /root/podcasts/.env`). The URL is never committed: .env is
gitignored AND lives outside the repo tree entirely.

register_vector() makes `vector` columns round-trip as numpy float32 arrays, so
PgStore loads embeddings into the SAME in-memory shape FileStore uses.
"""
from __future__ import annotations

import os
from pathlib import Path

_ENV_FILE = Path("/root/podcasts/.env")


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url and _ENV_FILE.exists():
        for line in _ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line.startswith(("DATABASE_URL=", "export DATABASE_URL=")):
                url = line.split("=", 1)[1].strip().strip("\"'")
                break
    if not url:
        raise RuntimeError(
            "no DATABASE_URL (checked env + /root/podcasts/.env); "
            "required for CHUNK_STORE_BACKEND=pg")
    return url


def connect():
    """A pgvector-aware psycopg2 connection."""
    import psycopg2
    from pgvector.psycopg2 import register_vector
    conn = psycopg2.connect(database_url())
    register_vector(conn)
    return conn
