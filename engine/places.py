"""Birth places for true solar time (GeoNames cities15000, CC BY 4.0; built into web/geo/cities.json).

A place gives the longitude (solar time runs 4 minutes per degree) and the IANA time zone (the clock
offset on the birth date, daylight saving and historical changes included). No place, or Singapore,
keeps the original Singapore path so those charts never change.
"""
from __future__ import annotations

import functools
import json
from pathlib import Path

CITIES = Path(__file__).resolve().parents[1] / "web/geo/cities.json"
SINGAPORE_ID = 1880252


@functools.lru_cache(maxsize=1)
def _data() -> dict:
    return json.loads(CITIES.read_text("utf8"))


@functools.lru_cache(maxsize=None)
def place(pid) -> dict | None:
    """City by GeoNames id: {id, name, cc, country, lat, lon, tz}, or None."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return None
    d = _data()
    for c in d["cities"]:
        if c[0] == pid:
            return {"id": c[0], "name": c[1], "cc": c[2], "country": d["countries"].get(c[2], c[2]),
                    "lat": c[3], "lon": c[4], "tz": c[5]}
    return None


if __name__ == "__main__":
    assert place(SINGAPORE_ID)["tz"] == "Asia/Singapore" and place("x") is None
    print(len(_data()["cities"]), "cities ok")
