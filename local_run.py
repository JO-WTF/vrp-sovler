from __future__ import annotations

import asyncio
import json
from dataclasses import asdict

from backend.analysis.convergence import to_point
from backend.data.homberger_loader import HombergerLoader
from backend.data.solomon_loader import SolomonLoader
from backend.data.vrplib_loader import VRPLibLoader
from backend.solvers.callbacks import IterationState
from backend.solvers.pyvrp_solver import PyVRPSolver

# ===== local debug config =====
DATASET = "vrplib"  # vrplib | solomon | homberger
INSTANCE = "A-n32-k5"
TIME_LIMIT_S = 5
POPULATION_SIZE = 80
# ==============================


def get_loader(dataset: str):
    if dataset == "vrplib":
        return VRPLibLoader()
    if dataset == "solomon":
        return SolomonLoader()
    if dataset == "homberger":
        return HombergerLoader()
    raise ValueError(f"Unsupported dataset: {dataset}")


async def main() -> None:
    loader = get_loader(DATASET)
    problem = loader.load(INSTANCE)
    solver = PyVRPSolver()

    history: list[dict] = []

    async def on_iteration(state: IterationState) -> None:
        point = to_point(state)
        history.append(point)
        if state.iteration % 20 == 0:
            print(f"iter={state.iteration} best={state.best_cost:.2f} elapsed={state.elapsed_s:.2f}s")

    result = await solver.solve(
        problem,
        time_limit_s=TIME_LIMIT_S,
        population_size=POPULATION_SIZE,
        on_iteration=on_iteration,
    )

    print("\n=== Solve Finished ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"iterations: {len(history)}")
    if history:
        print(f"first: {history[0]}")
        print(f"last:  {history[-1]}")


if __name__ == "__main__":
    asyncio.run(main())
