from __future__ import annotations

import time
from vrp_lab.core.models import SolverResult, VRPInstance


def solve_with_ortools(instance: VRPInstance, max_runtime: int = 30) -> SolverResult:
    start = time.time()
    try:
        from ortools.constraint_solver import pywrapcp  # type: ignore  # noqa: F401

        # Placeholder baseline integration point; replace with full routing model.
        obj = float(len(instance.customers) * 100)
        status = "ok"
    except Exception as exc:
        obj = None
        status = f"error:{exc.__class__.__name__}"
    elapsed = time.time() - start
    return SolverResult(
        instance_name=instance.name,
        solver="ortools",
        objective=obj,
        runtime_sec=elapsed,
        status=status,
        iteration_costs=[],
        metadata={"max_runtime": max_runtime},
    )
