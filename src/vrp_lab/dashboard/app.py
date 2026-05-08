from __future__ import annotations

import argparse
from pathlib import Path
import streamlit as st
import pandas as pd

from vrp_lab.analysis.plots import convergence_plot, performance_plot


def run_dashboard(results: Path, convergence: Path | None = None):
    st.set_page_config(page_title="VRP Lab Dashboard", layout="wide")
    st.title("VRP Experiment Dashboard")

    df = pd.read_csv(results)
    st.subheader("Raw Results")
    st.dataframe(df, use_container_width=True)

    st.subheader("Objective Comparison")
    st.plotly_chart(performance_plot(results), use_container_width=True)

    if convergence and convergence.exists():
        fig = convergence_plot(convergence)
        if fig is not None:
            st.subheader("Convergence")
            st.plotly_chart(fig, use_container_width=True)


def main():
    parser = argparse.ArgumentParser(description="Launch streamlit dashboard")
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--convergence", type=Path)
    args = parser.parse_args()
    run_dashboard(args.results, args.convergence)


if __name__ == "__main__":
    main()
