from enum import Enum

class WorkerStatus(str, Enum):


    # where set
    # meaning
    # colour in UI


    # backend on WS handshake
    # connected, jealthy, idle in Valkey pool, ready for jobs
    # green UI
    active = "active"

    # backend on task dispatch
    # actively processing fire spread
    # blue UI
    busy = "busy"

    # watchdog on heartbeat loss
    # WS closed or ping.pong timed out (>15s)
    # greay UI
    offline = "offline"

    # local runner/ backend during registration
    # hardware check failed
    # red UI
    rejected = "rejected" 

    # backend watchdog on simulation timeout or crash
    # failed mid-run / exceeded 10s, backoff 15 min
    # orange UI
    quarantined = "quarantined"

    # volunteer user via dashboard
    # volunteer opts out / pauses their runner
    # slate UI
    deactivated = "deactivated"

    # admin via detail modal
    # admin revoked / blacklisted node; stores removal reason
    # red badge
    removed = "removed"