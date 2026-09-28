# For push notifications via VAPID
from pydantic import BaseModel

class PushSubscriptionKeys(BaseModel):
    p256dh: str
    auth: str
    
class PushSubscribeIn(BaseModel):
    endpoint: str
    keys: PushSubscriptionKeys
    
