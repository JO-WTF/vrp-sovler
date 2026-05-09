from __future__ import annotations

from pathlib import Path

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

        lines = [ln.rstrip() for ln in file.read_text().splitlines()]
        capacity = self._parse_capacity(lines)
        coords = self._parse_coord_section(lines)
        demands = self._parse_demand_section(lines)
        depot_id = self._parse_depot(lines)

        depot = Customer(idx=0, x=coords[depot_id][0], y=coords[depot_id][1], demand=0)
        customers: list[Customer] = []
        for node_id, (x, y) in coords.items():
            if node_id == depot_id:
                continue
            customers.append(Customer(idx=node_id, x=x, y=y, demand=demands.get(node_id, 0)))

        return CVRPProblem(name=name, depot=depot, customers=customers, capacity=capacity)

    @staticmethod
    def _parse_capacity(lines: list[str]) -> int:
        for ln in lines:
            if ln.startswith("CAPACITY"):
                return int(ln.split(":")[-1].strip())
        raise ValueError("CAPACITY not found")

    @staticmethod
    def _parse_coord_section(lines: list[str]) -> dict[int, tuple[float, float]]:
        coords: dict[int, tuple[float, float]] = {}
        in_section = False
        for ln in lines:
            if ln.startswith("NODE_COORD_SECTION"):
                in_section = True
                continue
            if in_section:
                if ln.startswith(("DEMAND_SECTION", "DEPOT_SECTION", "EOF")):
                    break
                parts = ln.split()
                if len(parts) >= 3:
                    coords[int(parts[0])] = (float(parts[1]), float(parts[2]))
        if not coords:
            raise ValueError("NODE_COORD_SECTION not found or empty")
        return coords

    @staticmethod
    def _parse_demand_section(lines: list[str]) -> dict[int, int]:
        demands: dict[int, int] = {}
        in_section = False
        for ln in lines:
            if ln.startswith("DEMAND_SECTION"):
                in_section = True
                continue
            if in_section:
                if ln.startswith(("DEPOT_SECTION", "EOF")):
                    break
                parts = ln.split()
                if len(parts) >= 2:
                    demands[int(parts[0])] = int(parts[1])
        return demands

    @staticmethod
    def _parse_depot(lines: list[str]) -> int:
        in_section = False
        for ln in lines:
            if ln.startswith("DEPOT_SECTION"):
                in_section = True
                continue
            if in_section:
                val = ln.strip()
                if val == "-1":
                    break
                if val and val != "EOF":
                    return int(val)
        raise ValueError("DEPOT_SECTION not found")
