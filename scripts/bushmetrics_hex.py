"""Classifies the BushMetrics card's hexagons from BushMetrics v2 data.

    python scripts/bushmetrics_hex.py /path/to/bushmetrics/backend/app_data

Needs geopandas (the card build itself does not). Each hexagon is protected
when at least half its area lies in CAPAD 2024 protected areas; it counts as
Traditional Owner managed when IPAs and jointly managed parks make up most of
that protected area. Hexagons whose centre falls in the Sturt Plateau bioregion
are flagged as the gap. Writes data/bushmetrics_hex.json.
"""
import json
import math
import os
import sys

import geopandas as gpd
from shapely.geometry import Point, Polygon

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_assets import BM_K, BM_S, ROOT, bushmetrics_grid  # noqa: E402

src = sys.argv[1]
pa = gpd.read_file(os.path.join(src, "protected_areas.geojson")).to_crs(3577)
bio = gpd.read_file(os.path.join(src, "bioregions.geojson")).to_crs(4326)
sturt = bio[bio.name == "Sturt Plateau"].geometry.union_all()
to_mask = pa[pa.governance.isin(["ipa", "joint"])].geometry.union_all()
all_pa = pa.geometry.union_all()

r = (BM_S + 0.45) / BM_K  # hexagon radius in degrees, gaps included
out = {}
for key, x, y, lon, lat in bushmetrics_grid():
    hexagon = Polygon([(lon + r * math.cos(math.radians(60 * k + 30)),
                        lat - r * math.sin(math.radians(60 * k + 30))) for k in range(6)])
    h = gpd.GeoSeries([hexagon], crs=4326).to_crs(3577).iloc[0]
    prot = h.intersection(all_pa).area / h.area
    c = "none"
    if prot >= 0.5:
        c = "to" if h.intersection(to_mask).area >= 0.5 * h.intersection(all_pa).area else "other"
    rec = {"c": c}
    if sturt.contains(Point(lon, lat)):
        rec["gap"] = 1
    out[key] = rec
with open(os.path.join(ROOT, "data", "bushmetrics_hex.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, separators=(",", ":"), sort_keys=True)
n = len(out)
print(n, "hexagons;", {k: sum(v["c"] == k for v in out.values()) for k in ("to", "other", "none")},
      "gap", sum("gap" in v for v in out.values()))
