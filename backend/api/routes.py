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
    return {"supported": ["vrplib", "solomon", "homberger"]}


@router.post("/runs")
async def create_run(config: ExperimentConfig) -> dict:
    run_id = str(uuid.uuid4())
    RUNS[run_id] = {"status": "running", "results": [], "config": config.model_dump()}

    async def _work() -> None:
        try:
            loader = _loader(config.dataset)
            problems = [loader.load(name) for name in config.instances]
            solver = PyVRPSolver()

            for problem in problems:
                result = solver.solve(
                    problem,
                    time_limit_s=config.time_limit_s,
                    population_size=config.population_size,
                    on_iteration=lambda s: asyncio.create_task(bus.publish(run_id, {"type": "iteration", "payload": to_point(s)})),
                )
                RUNS[run_id]["results"].append(result)
                await bus.publish(run_id, {"type": "instance_done", "payload": result})

            write_results(RUNS[run_id]["results"], f"results/{run_id}.csv")
            RUNS[run_id]["status"] = "done"
            await bus.publish(run_id, {"type": "run_done", "payload": {"run_id": run_id}})
        except asyncio.CancelledError:
            RUNS[run_id]["status"] = "stopped"
            await bus.publish(run_id, {"type": "run_stopped", "payload": {"run_id": run_id}})
            raise
        except Exception as exc:  # noqa: BLE001
            RUNS[run_id]["status"] = "failed"
            RUNS[run_id]["error"] = str(exc)
            await bus.publish(run_id, {"type": "run_failed", "payload": {"error": str(exc)}})

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
