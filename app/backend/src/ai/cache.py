import hashlib
import json
import blosc2
import os
import numpy as np
import redis

VALKEY_HOST = os.getenv("VALKEY_HOST", "localhost")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))

client = redis.Redis(host=VALKEY_HOST, port=VALKEY_PORT, db=0)

def build_fire_cache_key(
        ref: str,
        lat: float,
        lng: float,
        boundary_radius_m: float,
        n_steps: int,
        cell_size_m: float,
        model_version: str = "dca-v1"
) -> str:
    """ This function builds a deterministic sha-256 key for a specific fire simulation run"""
    payload = {
        "ref": ref,
        "lat": round(lat, 5),
        "lng": round(lng, 5),
        "radius_m": round(boundary_radius_m, 2),
        "n_steps": n_steps,
        "cell_size_m": round(cell_size_m, 2),
        "version": model_version
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

        raw_bytes = blosc2.decompress(compressed_hist)
        history_arr = np.frombuffer(raw_bytes, dtype=np.int64).reshape(meta["n_steps"], meta["grid_h"], meta["grid_w"])

        meta["history"] = [g.ravel.tolist() for g in history_arr]
        return meta
    except Exception:
        None