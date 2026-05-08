from __future__ import annotations

from pathlib import Path
from vrp_lab.core.models import Customer, VRPInstance


def parse_vrplib(path: Path) -> VRPInstance:
    # lightweight parser: supports common CVRP fields
    name = path.stem
    coords: dict[int, tuple[float, float]] = {}
    demands: dict[int, int] = {}
    capacity = 0
    section = None

    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("CAPACITY"):
            capacity = int(line.split(":")[-1].strip())
        elif line == "NODE_COORD_SECTION":
            section = "coords"
        elif line == "DEMAND_SECTION":
            section = "demands"
        elif line.startswith("DEPOT_SECTION") or line.startswith("EOF"):
            section = None
        elif section == "coords":
            i, x, y = line.split()[:3]
            coords[int(i)] = (float(x), float(y))
        elif section == "demands":
            i, d = line.split()[:2]
            demands[int(i)] = int(d)

    depot = Customer(1, *coords.get(1, (0.0, 0.0)), demand=0)
    customers = [
        Customer(i, xy[0], xy[1], demand=demands.get(i, 0))
        for i, xy in sorted(coords.items())
        if i != 1
    ]
    return VRPInstance(name=name, source="vrplib", variant="CVRP", capacity=capacity, depot=depot, customers=customers)


def parse_solomon_like(path: Path, source: str) -> VRPInstance:
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    name = path.stem
    cap = int(lines[4].split()[-1]) if len(lines) > 4 else 200
    data_lines = lines[9:]

    rows = []
    for ln in data_lines:
        parts = ln.split()
        if len(parts) < 7:
            continue
        i, x, y, d, rt, dt, st = parts[:7]
        rows.append((int(i), float(x), float(y), int(d), float(rt), float(dt), float(st)))
    if not rows:
        raise ValueError(f"No customer records found in {path}")

    depot_row = rows[0]
    depot = Customer(depot_row[0], depot_row[1], depot_row[2], 0, depot_row[4], depot_row[5], depot_row[6])
    customers = [
        Customer(i, x, y, d, rt, dt, st)
        for i, x, y, d, rt, dt, st in rows[1:]
    ]
    return VRPInstance(name=name, source=source, variant="CVRPTW", capacity=cap, depot=depot, customers=customers)
