# Periodic re-check of fire proximity so stationary user still gets notified when a 
# fire's boundary creeps closer on it's own

from __future__ import annotations

import asyncio
import logging

from app.backend.db import SessionLocal
from app.backend.src.services.firefighter.fire_merge import check_and_merge_active_fires
from app.backend.src.services.notifications.notifications import (
    check_proximity_for_all_users,
)

logger = logging.getLogger(__name__)

# how often to re-evaluate creeping fire boundaries against every user's
# last known location.
PROXIMITY_CHECK_INTERVAL_S = 60

def run_proximity_sweep() -> None:
    """
    One synchronous pass: merge-check then proximity re-check. 
    Runs its own db session so it can be called from a plain thread
    """
    db = SessionLocal()
    try:
        check_and_merge_active_fires(db)
        check_proximity_for_all_users(db)
    finally:
        db.close()
        
async def run_proximity_check_loop(interval_s: float = PROXIMITY_CHECK_INTERVAL_S) -> None:
    """
    Long-running background task: call from FastAPI lifespan and cancel it on shutdown.
    Never lets one bad iteration kill the loop (logs and tries again next interval)
    """
    while True:
        try:
            await asyncio.to_thread(run_proximity_sweep)
        except Exception:
            logger.exception("Proximity check sweep failed")
        await asyncio.sleep(interval_s)
