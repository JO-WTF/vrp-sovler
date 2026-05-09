from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ExperimentConfig
from backend.api.websocket import bus
from backend.analysis.convergence import to_point
from backend.data.homberger_loader import HombergerLoader
from backend.data.solomon_loader import SolomonLoader
from backend.data.vrplib_loader import VRPLibLoader
from backend.runner.batch_run import write_results
from backend.solvers.pyvrp_solver import PyVRPSolver

router = APIRouter(prefix="/api")
RUNS: dict[str, dict[str, Any]] = {}
RUN_TASKS: dict[str, asyncio.Task[None]] = {}

CATALOG = {
    "vrplib": ["A-n32-k5", "A-n37-k6", "B-n35-k5"],
    "solomon": ["C101", "R101", "RC101"],
    "homberger": ["C1_2_1", "R1_2_1", "RC1_2_1"],
}


def _loader(dataset: str):
    if dataset == "vrplib":
        return VRPLibLoader()
    if dataset == "solomon":
        return SolomonLoader()
    if dataset == "homberger":
        return HombergerLoader()
    raise HTTPException(status_code=400, detail=f"Unsupported dataset: {dataset}")


@router.get("/datasets")
def datasets() -> dict:
    return {"supported": list(CATALOG), "instances": CATALOG}


@router.post("/runs")
async def create_run(config: ExperimentConfig) -> dict:
    run_id = str(uuid.uuid4())
    RUNS[run_id] = {"status": "running", "results": [], "config": config.model_dump(), "events": []}

    async def emit(event_type: str, payload: dict[str, Any]) -> None:
        evt = {"type": event_type, "payload": payload}
        RUNS[run_id]["events"].append(evt)
        await bus.publish(run_id, evt)

    async def _work() -> None:
        try:
            await emit("run_started", {"run_id": run_id})
            loader = _loader(config.dataset)
            await emit("dataset_prepare_started", {"dataset": config.dataset})

            problems = []
            for name in config.instances:
                await emit("download_started", {"instance": name})
                try:
                    problem = loader.load(name)
                    await emit("download_succeeded", {"instance": name})
                    problems.append(problem)
                except Exception as exc:  # noqa: BLE001
                    await emit("download_failed", {"instance": name, "error": str(exc)})

            if not problems:
                RUNS[run_id]["status"] = "failed"
                await emit("run_failed", {"error": "No instance loaded successfully"})
                return

            solver = PyVRPSolver()
            for problem in problems:
                await emit("solve_started", {"instance": problem.name})
                result = solver.solve(
                    problem,
                    time_limit_s=config.time_limit_s,
                    population_size=config.population_size,
                    on_iteration=lambda s: asyncio.create_task(emit("iteration", to_point(s))),
                )
                RUNS[run_id]["results"].append(result)
                await emit("solve_succeeded", result)

            write_results(RUNS[run_id]["results"], f"results/{run_id}.csv")
            RUNS[run_id]["status"] = "done"
            await emit("results_saved", {"path": f"results/{run_id}.csv"})
            await emit("run_done", {"run_id": run_id})
        except asyncio.CancelledError:
            RUNS[run_id]["status"] = "stopped"
            await emit("run_stopped", {"run_id": run_id})
            raise
        except Exception as exc:  # noqa: BLE001
            RUNS[run_id]["status"] = "failed"
            RUNS[run_id]["error"] = str(exc)
            await emit("run_failed", {"error": str(exc)})

    task = asyncio.create_task(_work())
    RUN_TASKS[run_id] = task
    return {"run_id": run_id}


@router.post("/runs/{run_id}/stop")
def stop_run(run_id: str) -> dict:
    task = RUN_TASKS.get(run_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if not task.done():
        task.cancel()
    return {"run_id": run_id, "status": "stopping"}


@router.get("/runs/{run_id}")
def run_status(run_id: str) -> dict:
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    return RUNS[run_id]
