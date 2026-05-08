from __future__ import annotations

import argparse
from pathlib import Path
import yaml

from vrp_lab.data.parsers import parse_solomon_like, parse_vrplib
from vrp_lab.runner.batch import run_batch, write_results


def _load_instance(path: Path, source: str):
    if source == "vrplib":
        return parse_vrplib(path)
    return parse_solomon_like(path, source=source)


def main():
    parser = argparse.ArgumentParser(description="Run batch VRP experiments")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()

    cfg = yaml.safe_load(args.config.read_text())
    instances = [_load_instance(Path(e["path"]), e["source"]) for e in cfg["instances"]]
    results = run_batch(instances, solvers=cfg.get("solvers", ["pyvrp", "ortools"]), max_runtime=cfg.get("max_runtime", 30))
    out_dir = Path(cfg.get("output_dir", "results/runs/latest"))
    csv_path, conv_path = write_results(results, out_dir)
    print(f"results={csv_path}")
    print(f"convergence={conv_path}")


if __name__ == "__main__":
    main()
