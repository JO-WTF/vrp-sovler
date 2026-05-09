from __future__ import annotations

from pathlib import Path

from backend.problems.base import Customer
from backend.problems.cvrp import CVRPProblem


class VRPLibLoader:
    def __init__(self, cache_dir: str = "data_cache/vrplib") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load(self, name: str) -> CVRPProblem:
        # Placeholder parser: assumes a pre-downloaded simplified CSV-like format.
        file = self.cache_dir / f"{name}.csv"
        if not file.exists():
            raise FileNotFoundError(f"Instance not found in cache: {file}")

        lines = [ln.strip() for ln in file.read_text().splitlines() if ln.strip()]
        capacity = int(lines[0].split(",")[1])
        depot_parts = lines[1].split(",")
        depot = Customer(idx=0, x=float(depot_parts[0]), y=float(depot_parts[1]))

        customers: list[Customer] = []
        for i, ln in enumerate(lines[2:], start=1):
            x, y, d = ln.split(",")
            customers.append(Customer(idx=i, x=float(x), y=float(y), demand=int(d)))

        return CVRPProblem(name=name, depot=depot, customers=customers, capacity=capacity)
