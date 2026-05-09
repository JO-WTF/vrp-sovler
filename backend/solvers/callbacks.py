from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class IterationState:
    iteration: int
    best_cost: float
    current_cost: float
    elapsed_s: float
