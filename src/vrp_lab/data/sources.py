from __future__ import annotations

from pathlib import Path
import requests

URLS = {
    "vrplib": "https://raw.githubusercontent.com/PyVRP/VRPLIB/master/instances",
    "solomon": "https://www.sintef.no/globalassets/project/top/vrptw/solomon",
    "homberger": "https://www.sintef.no/globalassets/project/top/vrptw/homberger",
}


def download_file(url: str, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    output.write_bytes(resp.content)
    return output
