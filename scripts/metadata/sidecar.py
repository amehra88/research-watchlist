"""
JSON sidecar I/O for document metadata.

Each source file has a sidecar at {source_path}.meta.json with the serialized
DocMetadata. Reads validate against the schema.
"""

import json
from pathlib import Path
from typing import Optional

from .schema import DocMetadata


def sidecar_path(source_path: Path) -> Path:
    """Returns the expected sidecar path for a source file."""
    return source_path.with_suffix(source_path.suffix + ".meta.json")


def write_sidecar(source_path: Path, metadata: DocMetadata) -> Path:
    """Writes metadata to {source_path}.meta.json. Returns the sidecar path."""
    target = sidecar_path(source_path)
    target.write_text(json.dumps(
        metadata.model_dump(mode="json", exclude_none=True),
        indent=2,
        sort_keys=True,
    ))
    return target


def read_sidecar(source_path: Path) -> Optional[DocMetadata]:
    """Reads sidecar JSON, returns DocMetadata. None if missing."""
    target = sidecar_path(source_path)
    if not target.exists():
        return None
    data = json.loads(target.read_text())
    return DocMetadata.model_validate(data)
