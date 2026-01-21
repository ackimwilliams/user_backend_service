from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass(frozen=True, slots=True)
class User:
    id: int
    name: str
    email: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
