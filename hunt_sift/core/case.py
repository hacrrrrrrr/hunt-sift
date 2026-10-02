"""Portable case manifests for offline Hunt Sift workspaces."""

from __future__ import annotations

import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from .workspace import ArtifactRecord


SCHEMA = "hunt-sift.case.v1"


def fingerprint(records: list[ArtifactRecord]) -> str:
    material = "\n".join(f"{r.path}\0{r.size}\0{r.sha256}" for r in records)
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def create_case(records: list[ArtifactRecord]) -> dict[str, object]:
    return {
        "schema": SCHEMA,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.system(),
        "artifact_count": len(records),
        "fingerprint": fingerprint(records),
        "artifacts": [r.__dict__ for r in records],
        "offline_only": True,
    }


def write_case(path: str | Path, records: list[ArtifactRecord]) -> None:
    Path(path).write_text(json.dumps(create_case(records), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_case(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema") != SCHEMA:
        raise ValueError("Unsupported Hunt Sift case schema")
    if payload.get("offline_only") is not True:
        raise ValueError("Case is missing the offline_only safety marker")
    return payload
