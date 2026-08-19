# Converts PostGIS location data into distance in kn so app can figure out how far user is from fire to see if they get alerted
from math import asin, cos, radians, sin, sqrt

from geoalchemy2.shape import to_shape

EARTH_RADIUS_KM = 6371.0

# haversine maths formula
def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Great-circle distance between two lat/lon points in km
    """
    
    lat1_r, lon1_r, lat2_r, lon2_r = map(radians, (lat1, lon1, lat2, lon2))
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    
    a = sin(dlat/2) ** 2 + cos(lat1_r) * sin(dlon/2) ** 2
    c = 2 * asin(sqrt(a))
    
    return EARTH_RADIUS_KM * c

def point_to_latlng(geom) -> tuple[float, float] | None:
    """
    Unpack a geoalchemy2 Geometry(POINT) col value into (lat, lng), matching `to_shape(...).y/.x`
    pattern used in services/firefighter/firefighter_reports.py
    
    Returns None if geom is unset (eg. user who hasn't shared location)
    """
    
    if geom is None:
        return None
    shape = to_shape(geom)
    
    return shape.y, shape.x