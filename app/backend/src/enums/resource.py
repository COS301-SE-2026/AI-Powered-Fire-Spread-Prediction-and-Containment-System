from enum import Enum

class ResourceType(str, Enum):
    water_tank = "water_tank"
    borehole = "borehole"
    trailer = "trailer"
    dam = "dam"
    aircraft = "aircraft"
    crew = "crew"
    other = "other"
    
class CapacityUnit(str, Enum):
    liters = "liters"
    members = "members"
    other = "other"
    
class ResourceStatus(str, Enum):
    available = "available"
    dispatched = "dispatched"
    unavailable = "unavailable"
    
def capacity_unit_for(resource_type: ResourceType) -> CapacityUnit:
    """
    This unit is fully determined by the resource type, so server derives it instead of trusting the client
    """
    if resource_type == ResourceType.other:
        return CapacityUnit.other
    if resource_type == ResourceType.crew:
        return CapacityUnit.members
    return CapacityUnit.liters