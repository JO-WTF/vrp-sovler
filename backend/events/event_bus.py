from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any


class EventBus:
    def __init__(self) -> None:
        self._channels: dict[str, list[asyncio.Queue[dict[str, Any]]]] = defaultdict(list)

    def subscribe(self, channel: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._channels[channel].append(queue)
        return queue

    async def publish(self, channel: str, payload: dict[str, Any]) -> None:
        for queue in self._channels[channel]:
            await queue.put(payload)

    def unsubscribe(self, channel: str, queue: asyncio.Queue[dict[str, Any]]) -> None:
        if queue in self._channels[channel]:
            self._channels[channel].remove(queue)
