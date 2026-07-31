import argparse

from .build_ignition_dataset import (
    build_fire_events,
    cluster_fire_events,
    load_detections,
)


def inspect_fire_events(
    csv_path: str,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    date_col: str = "acq_date",
    time_col: str = "acq_time",
    max_gap_km: float = 5.0,
    max_gap_days: float = 4.0,
    min_ticks: int = 2,
    limit: int | None = 20,
) -> list:
    detections = load_detections(csv_path, lat_col, lon_col, date_col, time_col)
    print(f"{len(detections):,} total detections loaded form {csv_path}")

    fire_ids = cluster_fire_events(
        detections, max_gap_km=max_gap_km, max_gap_days=max_gap_days
    )
    events = build_fire_events(detections, fire_ids)

    print(f"{len(events)} distinct fires")

    # get fires that can be used for training
    usable_fires = [e for e in events if len(e.ticks) >= min_ticks]
    print(f"{len(usable_fires):,} fires that have more than {min_ticks} ticks")

    usable_fires.sort(key=lambda e: -len(e.ticks))
    to_show = usable_fires if limit is None else usable_fires[:limit]

    for e in to_show:
        print(
            f"Fire ID = {e.fire_id} "
            f"bbox({e.min_lon:.3f}, {e.min_lat:.3f})-({e.max_lon:.3f},{e.max_lat:.3f})"
            f"ticks = {len(e.ticks)}"
        )

    if limit is not None and len(usable_fires) > limit:
        print(
            f"... ({len(usable_fires) - limit} more not shown but you can use --limit to see more)"
        )

    return usable_fires


def main():
    ap = argparse.ArgumentParser(description=__doc__)

    ap.add_argument("--csv", required=True, help="raw VIIRS/FIRMS detections CSV")
    ap.add_argument("--lat-col", default="latitude")
    ap.add_argument("--lon-col", default="longitude")
    ap.add_argument("--date-col", default="acq_date")
    ap.add_argument("--time-col", default="acq_time")
    ap.add_argument("--max-gap-km", type=float, default=5.0)
    ap.add_argument("--max-gap-days", type=float, default=4.0)
    ap.add_argument("--min-ticks", type=int, default=2)
    ap.add_argument(
        "--limit", type=int, default=20, help="max fire events to print 0 = all fires"
    )
    args = ap.parse_args()

    limit = None if args.limit == 0 else args.limit
    inspect_fire_events(
        args.csv,
        args.lat_col,
        args.lon_col,
        args.date_col,
        args.time_col,
        args.max_gap_km,
        args.max_gap_days,
        args.min_ticks,
        limit,
    )


if __name__ == "__main__":
    main()
