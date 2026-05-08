from __future__ import annotations

from pathlib import Path
import json
import pandas as pd

from vrp_lab.core.models import VRPInstance, SolverResult
from vrp_lab.solvers.pyvrp_solver import solve_with_pyvrp
from vrp_lab.solvers.ortools_solver import solve_with_ortools


def run_batch(instances: list[VRPInstance], solvers: list[str], max_runtime: int = 30) -> list[SolverResult]:
    out: list[SolverResult] = []
    for inst in instances:
        for solver in solvers:
            if solver == "pyvrp":
                out.append(solve_with_pyvrp(inst, max_runtime=max_runtime))
            elif solver == "ortools":
                out.append(solve_with_ortools(inst, max_runtime=max_runtime))
            else:
                out.append(
                    SolverResult(
                        instance_name=inst.name,
                        solver=solver,
                        objective=None,
                        runtime_sec=0,
                        status="error:unknown_solver",
                    )
                )
    return out


def write_results(results: list[SolverResult], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    flat = [
        {
            "instance": r.instance_name,
            "solver": r.solver,
            "objective": r.objective,
            "runtime_sec": r.runtime_sec,
            "status": r.status,
        }
        for r in results
    ]
    df = pd.DataFrame(flat)
    csv_path = output_dir / "results.csv"
    df.to_csv(csv_path, index=False)

    conv = output_dir / "convergence.jsonl"
    with conv.open("w", encoding="utf-8") as f:
        for r in results:
            for it, cost in r.iteration_costs:
                f.write(json.dumps({"instance": r.instance_name, "solver": r.solver, "iter": it, "cost": cost}) + "\n")
    return csv_path, conv
