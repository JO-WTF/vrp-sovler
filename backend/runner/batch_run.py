from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from backend.solvers.pyvrp_solver import PyVRPSolver


def run_batch(instances: list[Any], solver: PyVRPSolver, out_csv: str, **solver_kwargs: Any) -> list[dict]:
    results: list[dict] = []
    for problem in instances:
        results.append(solver.solve(problem, **solver_kwargs))

    output = Path(out_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["instance", "objective", "runtime_s", "vehicles"])
        writer.writeheader()
        writer.writerows(results)

    return results
