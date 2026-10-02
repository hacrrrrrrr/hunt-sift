"""Small, dependency-free configuration layer for Hunt Sift."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass(frozen=True)
class Config:
    max_findings: int = 10_000
    max_field_bytes: int = 20_000
    workspace_max_bytes: int = 5_000_000
    follow_symlinks: bool = False
    redact_evidence: bool = True

    def validate(self) -> "Config":
        if not 1 <= self.max_findings <= 1_000_000:
            raise ValueError("max_findings must be between 1 and 1,000,000")
        if not 128 <= self.max_field_bytes <= 1_000_000:
            raise ValueError("max_field_bytes must be between 128 and 1,000,000")
        if not 1_024 <= self.workspace_max_bytes <= 1_000_000_000:
            raise ValueError("workspace_max_bytes must be between 1 KiB and 1 GiB")
        return self


def load(path: str | Path | None = None) -> Config:
    candidate = Path(path).expanduser() if path else Path(".hunt-sift.json")
    if not candidate.exists():
        return Config()
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Hunt Sift configuration must be a JSON object")
    allowed = {k: v for k, v in payload.items() if k in Config.__dataclass_fields__}
    return Config(**allowed).validate()


def save(path: str | Path, config: Config) -> None:
    config.validate()
    Path(path).write_text(json.dumps(asdict(config), indent=2) + "\n", encoding="utf-8")
