from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Customer:
    idx: int
    x: float
    y: float
    demand: int = 0
    ready_time: int | None = None
    due_time: int | None = None
    service_time: int | None = None


@dataclass(slots=True)
class VRPProblem:
    name: str
    depot: Customer
    customers: list[Customer]
    capacity: int
    vehicle_count: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_time_window(self) -> bool:
        return any(c.ready_time is not None for c in self.customers)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "capacity": self.capacity,
            "vehicle_count": self.vehicle_count,
            "customer_count": len(self.customers),
            "is_time_window": self.is_time_window,
            "metadata": self.metadata,
        }
