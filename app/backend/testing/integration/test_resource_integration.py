from conftest import make_user
from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.water_resource import WaterResource

VALID = {
    "resource": "water_tank",
    "otherResource": "",
    "otherCapacity": "",
    "capacity": 5000,
    "capacityUnit": "liters",
    
}