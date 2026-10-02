# krakow-transit-delays

A master's thesis project about public transport in Kraków (AI & Data Analysis specialisation):
an app that shows buses and trams live on a map, predicts delays probabilistically
(e.g. *"median 3 min, 90% chance it is under 7 min"*), and plans A→B journeys with
the probability of arriving on time and of catching each transfer.

## Current stage: data collection

Kraków's realtime feed only shows the current state, so the history of delays
needed to train the model has to be collected by us. The collection stage includes:

- a lightweight logger running 24/7 on a small VPS, saving GTFS-Realtime snapshots
  every 60 s to hourly gzipped CSV files,
- daily download of the GTFS schedule, keeping only new versions,
- a daily health check (is data growing? how much disk is left?),
- transfer of the data off the VPS and conversion to Parquet for analysis.

## Data source

Open data from ZTP Kraków at <https://gtfs.ztp.krakow.pl>:

| Group | Operator | Static schedule | Realtime |
|---|---|---|---|
| `A` | MPK buses | `GTFS_KRK_A.zip` | `VehiclePositions_A.pb`, `TripUpdates_A.pb`, `ServiceAlerts_A.pb` |
| `T` | MPK trams | `GTFS_KRK_T.zip` | `..._T.pb` |
| `M` | Mobilis buses | `GTFS_KRK_M.zip` | `..._M.pb` |

The realtime files refresh about every 10 s. The license is still being clarified with ZTP
(see [docs/decisions.md](docs/decisions.md)).

## Repository layout

```
scripts/     one-off exploration tools (feed inspection, storage estimates)
docs/        decision log (decisions.md) and observations for later stages
collector/   logger and schedule downloader that run on the VPS     (coming next)
deploy/      cron entries and VPS setup notes                       (coming next)
data/        local data, never committed to git
```

## Quick start

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv run --with requests --with gtfs-realtime-bindings scripts/inspect_feed.py A
```
