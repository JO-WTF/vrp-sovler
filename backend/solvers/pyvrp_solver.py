from __future__ import annotations

import random
import time
from collections.abc import Callable

from backend.problems.base import VRPProblem
from backend.solvers.callbacks import IterationState


class PyVRPSolver:
    """Thin wrapper scaffold; replace fake loop with real pyvrp integration."""

    def solve(
        self,
        problem: VRPProblem,
        time_limit_s: int = 10,
        population_size: int = 100,
        on_iteration: Callable[[IterationState], None] | None = None,
    ) -> dict:
        start = time.perf_counter()
        best = 1e9
        curr = best
        iteration = 0

        while time.perf_counter() - start < time_limit_s:
            iteration += 1
            curr *= random.uniform(0.96, 0.999)
            best = min(best, curr)
            if on_iteration:
                on_iteration(
                    IterationState(
                        iteration=iteration,
                        best_cost=best,
                        current_cost=curr,
                        elapsed_s=time.perf_counter() - start,
                    )
                )
            time.sleep(0.03)

        return {
            "instance": problem.name,
            "objective": round(best, 3),
            "runtime_s": round(time.perf_counter() - start, 3),
            "vehicles": max(1, len(problem.customers) // max(1, population_size // 25)),
        }
