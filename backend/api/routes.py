from __future__ import annotations

import asyncio
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ExperimentConfig
from backend.data.homberger_loader import HombergerLoader
from backend.data.solomon_loader import SolomonLoader
from backend.data.vrplib_loader import VRPLibLoader
from backend.runner.batch_run import run_batch
from backend.solvers.pyvrp_solver import PyVRPSolver

router = APIRouter(prefix="/api")
RUNS: dict[str, dict[str, Any]] = {}


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
    RUNS[run_id] = {"status": "running", "results": []}

    async def _work() -> None:
        loader = _loader(config.dataset)
        problems = [loader.load(name) for name in config.instances]
        solver = PyVRPSolver()
        out_csv = f"results/{run_id}.csv"
        RUNS[run_id]["results"] = run_batch(
            problems,
            solver,
            out_csv,
            time_limit_s=config.time_limit_s,
            population_size=config.population_size,
        )
        RUNS[run_id]["status"] = "done"

    asyncio.create_task(_work())
    return {"run_id": run_id}


@router.get("/runs/{run_id}")
def run_status(run_id: str) -> dict:
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    return RUNS[run_id]
