from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(slots=True)
class Customer:
    id: int
    x: float
    y: float
    demand: int = 0
    ready_time: Optional[float] = None
    due_time: Optional[float] = None
    service_time: float = 0.0


@dataclass(slots=True)
class VRPInstance:
    name: str
    source: str
    variant: str  # CVRP | CVRPTW
    capacity: int
    depot: Customer
    customers: list[Customer] = field(default_factory=list)
    vehicle_count: Optional[int] = None


@dataclass(slots=True)
class SolverResult:
    instance_name: str
    solver: str
    objective: Optional[float]
    runtime_sec: float
    status: str
    iteration_costs: list[tuple[int, float]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
