import asyncio
import json
from collections import defaultdict

from fastapi import WebSocket

class ConnectionManager:
    """
    Tracks live WebSocket connections per user id
    
    A user can have multiple open connections (eg. two browser tabs) so each user id maps to a set of sockets
    """
    
    def __init__(self):
        self._conections: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
        
    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._conections[user_id].add(websocket)
            
    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            sockets = self._conections.get(user_id)
            if sockets is not None:
                sockets.discard(websocket)
            if not sockets:
                del self._conections[user_id]
                
    async def send_to_user(self, user_id: str, payload: dict) -> None:
        sockets = list(self._conections.get(user_id, ()))
        if not sockets:
            return  # user not connected rn. they will see it via REST on next load
        
        message = json.dumps(payload)
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
                
        if dead:
            async with self._lock:
                for ws in dead:
                    self._conections[user_id].discard(ws)
                    
    async def broadcast_to_users(self, user_ids: list[str], payload: dict) -> None:
        await asyncio.gather(*(self.send_to_user(uid, payload) for uid in user_ids))
        
manager = ConnectionManager()