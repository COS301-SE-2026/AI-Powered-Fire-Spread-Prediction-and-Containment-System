import os
import redis

VALKEY_HOST = os.getenv("VALKEY_HOST", "valkey")
VALKEY_PORT = int(os.getenv("VALKEY_PORT", 6379))

try:
    cache_client = redis.Redis(
        host=VALKEY_HOST,
        port=VALKEY_PORT,
        db=0,
        decode_responses=True,
        socket_connect_timeout=2.0,
        socket_timeout=2.0,
    )

    cache_client.ping()
except Exception:
    cache_client = None