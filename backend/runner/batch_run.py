from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def write_results(results: list[dict[str, Any]], out_csv: str) -> None:
    output = Path(out_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["instance", "objective", "runtime_s", "vehicles"])
        writer.writeheader()
        writer.writerows(results)
