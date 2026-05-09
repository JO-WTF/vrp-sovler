from __future__ import annotations

from pathlib import Path

import vrplib

from backend.problems.base import Customer
from backend.problems.cvrp import CVRPProblem


class VRPLibLoader:
    def __init__(self, cache_dir: str = "data_cache/vrplib") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def load(self, name: str) -> CVRPProblem:
        file = self.cache_dir / f"{name}.vrp"
        if not file.exists():
            raise FileNotFoundError(f"VRPLIB instance not found: {file}")

        inst = vrplib.read_instance(str(file))
        coords = inst["node_coord"]
        demands = inst.get("demand", [])
        capacity = int(inst["capacity"])

        depot_id = 1  # VRPLIB uses 1-based node ids with depot typically at 1.
        depot = Customer(idx=0, x=float(coords[depot_id][0]), y=float(coords[depot_id][1]), demand=0)

        customers: list[Customer] = []
        for node_id, xy in coords.items():
            if int(node_id) == depot_id:
                continue
            demand = int(demands[node_id]) if len(demands) > node_id else 0
            customers.append(Customer(idx=int(node_id), x=float(xy[0]), y=float(xy[1]), demand=demand))

        return CVRPProblem(name=name, depot=depot, customers=customers, capacity=capacity)

    def load_solution(self, name: str) -> dict:
        sol_file = self.cache_dir / f"{name}.sol"
        if not sol_file.exists():
            raise FileNotFoundError(f"VRPLIB solution not found: {sol_file}")
        return vrplib.read_solution(str(sol_file))
