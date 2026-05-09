from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from backend.api.schemas import ExperimentConfig
from backend.api.websocket import bus
from backend.analysis.convergence import to_point
from backend.data.homberger_loader import HombergerLoader
from backend.data.solomon_loader import SolomonLoader
from backend.data.vrplib_loader import VRPLibLoader
from backend.solvers.pyvrp_solver import PyVRPSolver

logger = logging.getLogger("backend.api.routes")
router = APIRouter(prefix="/api")
RUNS: dict[str, dict[str, Any]] = {}

CATALOG = {
    "vrplib": ["A-n32-k5", "A-n37-k6", "B-n35-k5"],
    "solomon": ["C101", "R101", "RC101"],
    "homberger": ["C1_2_1", "R1_2_1", "RC1_2_1"],
}


def _loader(dataset: str):
    logger.info("select loader dataset=%s", dataset)
    if dataset == "vrplib":
        return VRPLibLoader()
    if dataset == "solomon":
        return SolomonLoader()
    if dataset == "homberger":
        return HombergerLoader()
    logger.error("unsupported dataset=%s", dataset)
    raise HTTPException(status_code=400, detail=f"Unsupported dataset: {dataset}")


@router.get("/datasets")
def datasets() -> dict:
    logger.info("list datasets")
    return {"supported": list(CATALOG), "instances": CATALOG}


@router.post("/runs")
async def create_run(config: ExperimentConfig) -> dict:
    run_id = str(uuid.uuid4())
    logger.info("create run run_id=%s dataset=%s instance=%s", run_id, config.dataset, config.instance)
    RUNS[run_id] = {"status": "running", "results": [], "config": config.model_dump(), "events": [], "next_seq": 1}

    async def emit(event_type: str, payload: dict[str, Any]) -> None:
        logger.info("run_id=%s event=%s payload=%s", run_id, event_type, payload)
        seq = RUNS[run_id]["next_seq"]
        RUNS[run_id]["next_seq"] += 1
        evt = {"seq": seq, "type": event_type, "payload": payload}
        RUNS[run_id]["events"].append(evt)
        await bus.publish(run_id, evt)

    try:
        await emit("run_started", {"run_id": run_id})
        loader = _loader(config.dataset)
        await emit("dataset_prepare_started", {"dataset": config.dataset})

        problems = []
        await emit("download_started", {"instance": config.instance})
        try:
            problem = loader.load(config.instance)
            await emit("download_succeeded", {"instance": config.instance})
        except Exception as exc:  # noqa: BLE001
            logger.exception("download failed run_id=%s instance=%s", run_id, config.instance)
            RUNS[run_id]["status"] = "failed"
            await emit("download_failed", {"instance": config.instance, "error": str(exc)})
            await emit("run_failed", {"error": "Instance load failed"})
            return {"run_id": run_id}

        solver = PyVRPSolver()
        await emit("solve_started", {"instance": problem.name})
        result = await solver.solve(
            problem,
            time_limit_s=config.time_limit_s,
            population_size=config.population_size,
            on_iteration=lambda s: emit("iteration", to_point(s)),
        )
        RUNS[run_id]["results"].append(result)
        await emit("solve_succeeded", result)
        RUNS[run_id]["status"] = "done"
        await emit("results_ready", {"count": len(RUNS[run_id]["results"])})
        await emit("run_done", {"run_id": run_id})
        logger.info("run completed run_id=%s", run_id)
    except Exception as exc:  # noqa: BLE001
        RUNS[run_id]["status"] = "failed"
        RUNS[run_id]["error"] = str(exc)
        await emit("run_failed", {"error": str(exc)})
        logger.exception("run failed run_id=%s", run_id)

    return {"run_id": run_id}


@router.post("/runs/{run_id}/stop")
def stop_run(run_id: str) -> dict:
    logger.warning("stop endpoint disabled run_id=%s", run_id)
    return {"run_id": run_id, "status": "unsupported", "detail": "Task-based stop disabled by design"}


@router.get("/runs/{run_id}")
def run_status(run_id: str) -> dict:
    logger.info("query run status run_id=%s", run_id)
    if run_id not in RUNS:
        logger.error("run status not found run_id=%s", run_id)
        raise HTTPException(status_code=404, detail="Run not found")
    return RUNS[run_id]
