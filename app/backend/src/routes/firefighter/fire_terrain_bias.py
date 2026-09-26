from fastapi import APIRouter, HTTPException

from app.backend.src.schemas.fire_terrain_bias import TerrainBias
from app.backend.src.services.firefighter import fire_terrain_bias

router = APIRouter(prefix="/api/firefighter", tags=["Firefighter"])

# real slope/aspect/landcover derived directional growth bias for fire's live-map. 
# Terrain doesn't change over a fire's lifetime so frontend should fetch this once per fire and cache
# it client-side rather than repolling.
@router.get(
    "/terrain-bias",
    response_model=TerrainBias,
    responses={503: {"description": "Terrain data unavailable for this location"}},
)
def get_terrain_bias(lat: float, lng: float):
    try:
        return {"bias": fire_terrain_bias.compute_terrain_bias(lat, lng)}
    except Exception as error:
        raise HTTPException(status_code=503, detail=str(error))