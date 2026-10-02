"""Offline project workspace indexing and search helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    kind: str
    size: int
    sha256: str


def classify(path: Path) -> str:
    names = {".har": "har", ".xml": "xml", ".json": "json", ".txt": "text", ".html": "html", ".htm": "html", ".js": "javascript", ".ts": "typescript", ".py": "python", ".yaml": "config", ".yml": "config"}
    return names.get(path.suffix.lower(), "other")


def index_directory(root: str | Path, max_bytes: int = 5_000_000, follow_symlinks: bool = False) -> list[ArtifactRecord]:
    base = Path(root).expanduser().resolve()
    if not base.is_dir():
        raise ValueError(f"Workspace must be a local directory: {base}")
    records: list[ArtifactRecord] = []
    ignored = {".git", ".venv", "__pycache__", "node_modules"}
    for path in sorted(p for p in base.rglob("*") if p.is_file()):
        if any(part in ignored for part in path.parts):
            continue
        if not follow_symlinks and path.is_symlink():
            continue
        size = path.stat().st_size
        if size > max_bytes:
            continue
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        records.append(ArtifactRecord(str(path.relative_to(base)), classify(path), size, digest.hexdigest()))
    return records


def search_records(records: list[ArtifactRecord], query: str) -> list[ArtifactRecord]:
    needle = query.casefold()
    return [r for r in records if needle in r.path.casefold() or needle in r.kind.casefold()]


def write_index(records: list[ArtifactRecord], output: str | Path) -> None:
    Path(output).write_text(json.dumps([asdict(r) for r in records], indent=2) + "\n", encoding="utf-8")
