import argparse

from .build_ignition_dataset import load_detections, cluster_fire_events, build_fire_events

def inspect_fire_events(
    csv_path: str,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    date_col: str = "acq_date",
    time_col: str = "acq_time",
    max_gap_km: float = 5.0,
    max_gap_days: float = 4.0,
    limit: int | None = 20,
) -> list:
    detections = load_detections(csv_path, lat_col, lon_col, date_col, time_col)
    print(f"{len(detections):,} total detections loaded form {csv_path}")

    fire_ids = cluster_fire_events(detections, max_gap_km=max_gap_km, max_gap_days=max_gap_days)
    events = build_fire_events(detections, fire_ids)

    print(f"{len(events)} distinct fires")

    to_show = events if limit is None else events[:limit]

    for e in to_show:
        print(f"Fire ID = {e.fire_id} " f"bbox({e.min_lon:.3f}, {e.min_lat:.3f})-({e.max_lon:.3f},{e.max_lat:.3f})" f"ticks = {len(e.ticks)}")

    if limit is not None and len(events) > limit:
        print(f"... ({len(events) - limit} more not shown but you can use --limit to see more)")

    return events

def main():
    ap = argparse.ArgumentParser(description=__doc__)

    ap.add_argument("--csv", required=True, help="raw VIIRS/FIRMS detections CSV")
    ap.add_argument("--lat-col", default="latitude")
    ap.add_argument("--lon-col", default="longitude")
    ap.add_argument("--date-col", default="acq_date")
    ap.add_argument("--time-col", default="acq_time")
    ap.add_argument("--max-gap-km", type=float, default=5.0)
    ap.add_argument("--max-gap-days", type=float, default=4.0)
    ap.add_argument("--limit", type=int, default=20, help="max fire events to print 0 = all fires")
    args = ap.parse_args()

    limit = None if args.limit == 0 else args.limit
    inspect_fire_events(args.csv, args.lat_col, args.lon_col, args.date_col, args.time_col, args.max_gap_km, args.max_gap_days, limit)

if __name__ == "__main__":
    main()