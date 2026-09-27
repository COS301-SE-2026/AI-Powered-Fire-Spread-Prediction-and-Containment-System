from pydantic import BaseModel

class BearingFactor(BaseModel):
    bearing_deg: float
    factor: float
    
class TerrainBias(BaseModel):
    bias: list[BearingFactor]
    