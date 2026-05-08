from __future__ import annotations

from pathlib import Path
from typing import Iterable

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from vrp_lab.core.models import VRPInstance
from vrp_lab.data.parsers import parse_solomon_like, parse_vrplib
from vrp_lab.runner.batch import write_results
from vrp_lab.solvers.ortools_solver import solve_with_ortools
from vrp_lab.solvers.pyvrp_solver import solve_with_pyvrp

app = FastAPI(title="VRP Lab WebUI")


def _iter_instance_files(data_dir: Path) -> Iterable[Path]:
    patterns = ("*.vrp", "*.txt", "*.sol")
    for pattern in patterns:
        for p in data_dir.rglob(pattern):
            if p.is_file():
                yield p


def _detect_and_parse(path: Path) -> VRPInstance:
    if path.suffix.lower() == ".vrp":
        return parse_vrplib(path)
    source = "solomon" if "solomon" in path.as_posix().lower() else "homberger"
    return parse_solomon_like(path, source=source)


@app.get("/api/instances")
def list_instances(data_dir: str = "data") -> list[dict[str, str]]:
    root = Path(data_dir)
    if not root.exists():
        return []

    out: list[dict[str, str]] = []
    for p in sorted(set(_iter_instance_files(root))):
        out.append({"name": p.stem, "path": str(p)})
    return out


@app.websocket("/ws/run")
async def ws_run(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        payload = await websocket.receive_json()
        instance_path = Path(payload["instance_path"])
        solvers = payload.get("solvers", ["pyvrp", "ortools"])
        max_runtime = int(payload.get("max_runtime", 30))
        out_dir = Path(payload.get("output_dir", "outputs/webui"))

        instance = _detect_and_parse(instance_path)
        results = []
        total = len(solvers)

        await websocket.send_json({"type": "start", "instance": instance.name, "total": total})

        for idx, solver in enumerate(solvers, start=1):
            await websocket.send_json({"type": "progress", "message": f"Running {solver}...", "step": idx, "total": total})
            if solver == "pyvrp":
                result = solve_with_pyvrp(instance, max_runtime=max_runtime)
            elif solver == "ortools":
                result = solve_with_ortools(instance, max_runtime=max_runtime)
            else:
                await websocket.send_json({"type": "warning", "message": f"Unknown solver: {solver}"})
                continue
            results.append(result)
            await websocket.send_json(
                {
                    "type": "solver_result",
                    "solver": result.solver,
                    "objective": result.objective,
                    "runtime_sec": result.runtime_sec,
                    "status": result.status,
                    "iteration_costs": result.iteration_costs,
                }
            )

        csv_path, conv_path = write_results(results, out_dir)
        await websocket.send_json(
            {
                "type": "done",
                "results": [r.model_dump() for r in results],
                "artifacts": {"csv": str(csv_path), "convergence": str(conv_path)},
            }
        )
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": f"{exc.__class__.__name__}: {exc}"})


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    ui_file = Path(__file__).with_name("index.html")
    return ui_file.read_text(encoding="utf-8")


def main() -> None:
    import uvicorn

    uvicorn.run("vrp_lab.webui.server:app", host="0.0.0.0", port=8765, reload=False)
