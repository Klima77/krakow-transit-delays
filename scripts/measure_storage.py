"""Estimate daily storage for different ways of saving GTFS-Realtime data.

Takes one snapshot of each feed, writes it to gzipped CSV in three variants
and extrapolates to a full day using the chosen polling intervals:
  - VehiclePositions, every 60 s
  - TripUpdates, next stop only, every 60 s
  - TripUpdates, all stops (benchmark of ZTP predictions), every 5 min

Run:
    uv run --with requests --with gtfs-realtime-bindings scripts/measure_storage.py
"""

import csv
import gzip
import io
import time

import requests
from google.transit import gtfs_realtime_pb2

BASE_URL = "https://gtfs.ztp.krakow.pl"
GROUPS = ["A", "T", "M"]
SNAPSHOTS_PER_DAY_60S = 24 * 60
SNAPSHOTS_PER_DAY_5MIN = 24 * 12


def fetch_feed(name: str, attempts: int = 5) -> gtfs_realtime_pb2.FeedMessage:
    """Download and parse a feed, retrying when the file is empty or half-written."""
    for _ in range(attempts):
        try:
            resp = requests.get(f"{BASE_URL}/{name}", timeout=15)
            resp.raise_for_status()
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(resp.content)
            if feed.entity:
                return feed
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError(f"Could not fetch a valid {name}")


def gzipped_size(rows: list[list]) -> tuple[int, int]:
    """Return (raw CSV bytes, gzipped bytes) for the given rows."""
    buf = io.StringIO()
    csv.writer(buf).writerows(rows)
    raw = buf.getvalue().encode("utf-8")
    return len(raw), len(gzip.compress(raw))


def vp_rows(feed, ts):
    rows = []
    for e in feed.entity:
        v = e.vehicle
        rows.append([ts, v.vehicle.id, v.trip.route_id, v.trip.trip_id,
                     round(v.position.latitude, 6), round(v.position.longitude, 6),
                     int(v.position.bearing), v.current_stop_sequence, v.current_status,
                     v.stop_id, v.timestamp])
    return rows


def tu_rows(feed, ts, next_stop_only: bool):
    rows = []
    for e in feed.entity:
        t = e.trip_update
        updates = t.stop_time_update[:1] if next_stop_only else t.stop_time_update
        for s in updates:
            rows.append([ts, t.trip.trip_id, t.trip.route_id, t.vehicle.id,
                         s.stop_sequence, s.stop_id, s.arrival.time, s.departure.time])
    return rows


totals = {"vp": [0, 0], "tu_next": [0, 0], "tu_full": [0, 0]}
for g in GROUPS:
    ts = int(time.time())
    vp = fetch_feed(f"VehiclePositions_{g}.pb")
    tu = fetch_feed(f"TripUpdates_{g}.pb")
    for key, rows in [("vp", vp_rows(vp, ts)),
                      ("tu_next", tu_rows(tu, ts, next_stop_only=True)),
                      ("tu_full", tu_rows(tu, ts, next_stop_only=False))]:
        n_rows = len(rows)
        raw, gz = gzipped_size(rows)
        totals[key][0] += n_rows
        totals[key][1] += gz
        print(f"{g} {key:8} rows={n_rows:5}  csv={raw / 1024:7.1f} KB  gzip={gz / 1024:6.1f} KB")

print("\nPer day (all groups, current traffic level):")
per_day = {
    "VehiclePositions every 60 s": totals["vp"][1] * SNAPSHOTS_PER_DAY_60S,
    "TripUpdates next stop every 60 s": totals["tu_next"][1] * SNAPSHOTS_PER_DAY_60S,
    "TripUpdates all stops every 5 min": totals["tu_full"][1] * SNAPSHOTS_PER_DAY_5MIN,
}
for label, size in per_day.items():
    print(f"  {label:36} {size / 1024**2:7.1f} MB/day  {size * 120 / 1024**3:5.2f} GB/120 days")
total = sum(per_day.values())
print(f"  {'TOTAL':36} {total / 1024**2:7.1f} MB/day  {total * 120 / 1024**3:5.2f} GB/120 days")
