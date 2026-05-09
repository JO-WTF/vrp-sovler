from __future__ import annotations

from pathlib import Path

from backend.problems.base import Customer
from backend.problems.cvrptw import CVRPTWProblem


class SolomonLoader:
    def __init__(self, cache_dir: str = "data_cache/solomon") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load(self, name: str) -> CVRPTWProblem:
        file = self.cache_dir / f"{name}.csv"
        if not file.exists():
            raise FileNotFoundError(f"Instance not found in cache: {file}")

        rows = [ln.strip().split(",") for ln in file.read_text().splitlines() if ln.strip()]
        capacity = int(rows[0][1])
        depot = Customer(idx=0, x=float(rows[1][0]), y=float(rows[1][1]), ready_time=0, due_time=999999, service_time=0)

        customers = [
            Customer(
                idx=i,
                x=float(r[0]),
                y=float(r[1]),
                demand=int(r[2]),
                ready_time=int(r[3]),
                due_time=int(r[4]),
                service_time=int(r[5]),
            )
            for i, r in enumerate(rows[2:], start=1)
        ]
        return CVRPTWProblem(name=name, depot=depot, customers=customers, capacity=capacity)
