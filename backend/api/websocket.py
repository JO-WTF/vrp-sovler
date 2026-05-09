from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

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
            try:
                message = await asyncio.wait_for(queue.get(), timeout=1.0)
                await websocket.send_json(message)
            except asyncio.TimeoutError:
                if websocket.client_state.name != "CONNECTED":
                    break
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        bus.unsubscribe(run_id, queue)
