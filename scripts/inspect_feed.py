"""Preview GTFS-Realtime data from ZTP Krakow (step 1 - data reconnaissance).

Downloads one VehiclePositions and one TripUpdates file, prints a few records
and the statistics needed to choose the storage format and polling interval.

Run (without installing anything permanently):
    uv run --with requests --with gtfs-realtime-bindings scripts/inspect_feed.py [A|T|M]
"""

import sys
from collections import Counter
from datetime import datetime, timezone

import requests
from google.transit import gtfs_realtime_pb2

BASE_URL = "https://gtfs.ztp.krakow.pl"
GROUP = sys.argv[1] if len(sys.argv) > 1 else "A"  # A = buses, T = trams, M = ?


def fetch_feed(name: str) -> gtfs_realtime_pb2.FeedMessage:
    """Download a .pb file and decode it from protobuf."""
    resp = requests.get(f"{BASE_URL}/{name}", timeout=15)
    resp.raise_for_status()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    print(f"\n=== {name}: {len(resp.content)} bytes, {len(feed.entity)} entities ===")
    print(f"Header: version={feed.header.gtfs_realtime_version}, "
          f"feed time (UTC)={utc(feed.header.timestamp)}")
    return feed


def utc(ts: int) -> str:
    """Convert a Unix timestamp to a readable UTC datetime."""
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if ts else "-"


# --- Vehicle positions ---
vp = fetch_feed(f"VehiclePositions_{GROUP}.pb")
print(f"{'vehicle id':>12} {'route':>6} {'trip id':>28} {'lat':>9} {'lon':>9}  time (UTC)")
for e in vp.entity[:8]:
    v = e.vehicle
    print(f"{v.vehicle.id:>12} {v.trip.route_id:>6} {v.trip.trip_id:>28} "
          f"{v.position.latitude:9.5f} {v.position.longitude:9.5f}  {utc(v.timestamp)}")

# Which fields are actually populated (speed, label, current_stop_sequence, ...)
print("\nSample full VehiclePositions entity:\n", vp.entity[0])

# --- Predictions / delays ---
tu = fetch_feed(f"TripUpdates_{GROUP}.pb")
stops_per_trip = [len(e.trip_update.stop_time_update) for e in tu.entity]
print(f"Trips: {len(stops_per_trip)}, stops per trip: min={min(stops_per_trip, default=0)}, "
      f"avg={sum(stops_per_trip) / max(len(stops_per_trip), 1):.1f}, max={max(stops_per_trip, default=0)}")
print("Trip-level delay present (trip_update.delay):",
      Counter(e.trip_update.HasField("delay") for e in tu.entity))
print("\nSample TripUpdates entity (truncated to 3 stops):")
sample = tu.entity[0]
del sample.trip_update.stop_time_update[3:]
print(sample)
