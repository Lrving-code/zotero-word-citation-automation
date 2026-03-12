from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceSeed:
    cite_key: str
    doi: str
    forced_year: int | None = None
