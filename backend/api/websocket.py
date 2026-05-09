from __future__ import annotations

from fastapi import APIRouter, WebSocket

from backend.events.event_bus import EventBus
from backend.state import RUNS

router = APIRouter()
bus = EventBus()


@router.websocket("/ws/{run_id}")
async def run_stream(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    queue = bus.subscribe(run_id)
    try:
        if run_id in RUNS:
            for evt in RUNS[run_id].get("events", []):
                await websocket.send_json(evt)
        while True:
            message = await queue.get()
            await websocket.send_json(message)
    finally:
        bus.unsubscribe(run_id, queue)
