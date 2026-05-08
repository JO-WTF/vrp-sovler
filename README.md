# VRP Experiment Framework

A modular experiment framework for CVRP/CVRPTW research with:

- Multi-source benchmark ingestion (VRPLIB, Solomon, Homberger)
- Unified problem interface
- Solvers: PyVRP (primary) and OR-Tools (baseline)
- Batch experiments with structured CSV outputs
- Convergence logging and visualization
- Streamlit dashboard for interactive comparison

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
vrp-bench fetch --source vrplib --output data/raw/vrplib
vrp-batch --config configs/experiments.yaml
vrp-dashboard --results results/runs/latest/results.csv
```

## Project layout

- `src/vrp_lab/data/`: ingestion + normalization
- `src/vrp_lab/core/`: data models and adapters
- `src/vrp_lab/solvers/`: PyVRP and OR-Tools runners
- `src/vrp_lab/runner/`: batch execution and metrics persistence
- `src/vrp_lab/analysis/`: convergence and performance plots
- `src/vrp_lab/dashboard/`: Streamlit dashboard

## Notes

- PyVRP is used as the primary solver; OR-Tools is a baseline.
- CVRP and CVRPTW are both represented in one normalized schema.
- If a solver is unavailable at runtime, the framework records the failure and keeps batch execution running.
