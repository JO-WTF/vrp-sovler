from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.express as px


def convergence_plot(convergence_jsonl: Path):
    df = pd.read_json(convergence_jsonl, lines=True)
    if df.empty:
        return None
    fig = px.line(df, x="iter", y="cost", color="solver", line_dash="instance", title="Convergence Curve")
    return fig


def performance_plot(results_csv: Path):
    df = pd.read_csv(results_csv)
    fig = px.bar(df, x="instance", y="objective", color="solver", barmode="group", title="Solution Quality")
    return fig
