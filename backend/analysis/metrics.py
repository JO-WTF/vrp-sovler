from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RunMetrics:
    instance: str
    objective: float
    runtime_s: float
    vehicles: int
