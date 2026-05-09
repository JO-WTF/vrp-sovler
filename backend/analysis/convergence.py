from __future__ import annotations

from backend.solvers.callbacks import IterationState


def to_point(state: IterationState) -> dict:
    return {
        "iteration": state.iteration,
        "best_cost": state.best_cost,
        "current_cost": state.current_cost,
        "elapsed_s": state.elapsed_s,
    }
