import hashlib
import json
import zlib
import os
import numpy as np
import redis
from shapely import wkt as shapely_wkt
from shapely.geometry import box
from typing import Any, Dict, Optional, List


VALKEY_HOST = os.getenv("VALKEY_HOST", "valkey-cache")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))

client = redis.Redis(host=VALKEY_HOST, port=VALKEY_PORT, db=0)


def filter_containment_lines(
    lat: float,
    lng: float,
    containment_lines: List[str],
    extent_buffer_deg: float = 0.15,
) -> List[str]:
    """
    Filters the containment lines and only picks the ones that intersect with a bounding box
    """

    if not containment_lines:
        return []

    fire_bounds = box(
        lng - extent_buffer_deg,
        lat - extent_buffer_deg,
        lng + extent_buffer_deg,
        lat + extent_buffer_deg,
    )

    relevent_lines: List[str] = []
    for line in containment_lines:
        trimmed = line.strip()

        if not trimmed:
            continue

        try:
            geom = shapely_wkt.loads(trimmed)

            if fire_bounds.intersects(geom):
                relevent_lines.append(trimmed)
        except Exception as exc:
            relevent_lines.append(trimmed)

    return sorted(relevent_lines)


def build_fire_cache_key(
    ref: str,
    lat: float,
    lng: float,
    boundary_radius_m: float,
    n_steps: int,
    cell_size_m: float,
    containment_lines: Optional[List[str]] = None,
    model_version: str = "dca-v1",
) -> str:
    """This function builds a deterministic sha-256 key for a specific fire simulation run"""
    raw_lines = containment_lines or []

    locationially_relevent_lines = filter_containment_lines(lat, lng, raw_lines)

    payload = {
        "ref": ref,
        "lat": round(lat, 5),
        "lng": round(lng, 5),
        "radius_m": round(boundary_radius_m, 2),
        "n_steps": n_steps,
        "cell_size_m": round(cell_size_m, 2),
        "version": model_version,
        "containment_lines": locationially_relevent_lines,
    }

    encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
    hash = hashlib.sha256(encoded).hexdigest()[:16]
    return f"sim:fire:{ref}:{hash}"


def get_cached_prediction(key: str) -> dict | None:
    """Retrieve and decompress the cached data"""
    try:
        data = client.hgetall(key)
        if not data:
            return None

        meta = json.loads(data[b"meta"].decode("utf-8"))
        compressed_hist = data[b"history"]

        raw_bytes = zlib.decompress(compressed_hist)
        history_arr = np.frombuffer(raw_bytes, dtype=np.int64).reshape(
            meta["n_steps"], meta["grid_h"], meta["grid_w"]
        )

        meta["history"] = [g.ravel().tolist() for g in history_arr]
        return meta
    except Exception:
        None


def cache_prediction(key: str, prediction_data: dict, ttl_seconds: int = 3600):
    """Stores the prediction metadata and compressed grid history in valkey"""

    try:
        history_arr = np.array(prediction_data["history"], dtype=np.int64).reshape(
            len(prediction_data["history"]),
            prediction_data["grid_h"],
            prediction_data["grid_w"],
        )

        compressed_hist = zlib.compress(history_arr.tobytes(), level=6)

        meta = {
            "ref": prediction_data["ref"],
            "lat": prediction_data["lat"],
            "lng": prediction_data["lng"],
            "burned_cells": prediction_data["burned_cells"],
            "radius_m": prediction_data["radius_m"],
            "truncated": prediction_data["truncated"],
            "lat_extent_deg": prediction_data["lat_extent_deg"],
            "lon_extent_deg": prediction_data["lon_extent_deg"],
            "grid_h": prediction_data["grid_h"],
            "grid_w": prediction_data["grid_w"],
            "cell_size_m": prediction_data["cell_size_m"],
            "n_steps": len(prediction_data["history"]),
        }

        client.hset(key, mapping={"meta": json.dumps(meta), "history": compressed_hist})
        client.expire(key, ttl_seconds)
    except Exception:
        pass
