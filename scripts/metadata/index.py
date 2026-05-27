"""
Central document index — one JSONL line per ingested doc.

Append-only on writes; read returns a generator of DocMetadata.
"""

import json
from pathlib import Path
from typing import Iterator

from .schema import DocMetadata

DEFAULT_INDEX_PATH = Path("/root/research-watchlist/config/document-index.jsonl")


def append_to_index(
    metadata: DocMetadata,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> None:
    """Append one JSON line to the index."""
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("a") as f:
        f.write(json.dumps(
            metadata.model_dump(mode="json", exclude_none=True),
            sort_keys=True,
        ))
        f.write("\n")


def read_index(
    index_path: Path = DEFAULT_INDEX_PATH,
) -> Iterator[DocMetadata]:
    """Yield DocMetadata for each line in the index."""
    if not index_path.exists():
        return
    with index_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            yield DocMetadata.model_validate(data)


def index_contains(
    doc_id: str,
    index_path: Path = DEFAULT_INDEX_PATH,
) -> bool:
    """True if doc_id already in index (for dedup)."""
    for entry in read_index(index_path):
        if entry.doc_id == doc_id:
            return True
    return False
