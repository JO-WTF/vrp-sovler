from __future__ import annotations

import argparse
from pathlib import Path

from vrp_lab.data.sources import URLS, download_file


def main():
    parser = argparse.ArgumentParser(description="Download benchmark instances")
    parser.add_argument("--source", choices=["vrplib", "solomon", "homberger"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--files", nargs="+", default=[])
    args = parser.parse_args()

    base = URLS[args.source]
    args.output.mkdir(parents=True, exist_ok=True)
    for name in args.files:
        download_file(f"{base}/{name}", args.output / name)


if __name__ == "__main__":
    main()
