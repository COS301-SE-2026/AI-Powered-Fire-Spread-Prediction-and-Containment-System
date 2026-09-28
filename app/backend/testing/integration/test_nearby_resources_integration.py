from conftest import make_user
from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.water_resource import WaterResource

VALID = {
        "id": "res-1",
        "resource": "water_tank",
        "otherResource": "",
        "capacity": 5000,
        "capacityUnit": "liters",
        "otherCapacity": "",
        "status": "available",
        "availableFrom": "2026-09-20",
        "availableUntil": None,
        "location": "Farm on Old Warmbaths Rd, Pretoria North",
        "externalPin": {"lat": -25.7461, "lng": 28.1881},
        "name": "Pieter van der Merwe",
        "contact": "082 456 1234",
    }

HERE = {"lat": -25.7461, "lng": 28.1881}

def auth(user):
    token = create_access_token({"user_id": user.id})
    return {"Cookie": f"access_token={token}"}

def register(client, user, **overrides):
    res = client.post("/api/users/resources", json={**VALID, **overrides}, headers=auth(user))
    assert res.status_code == 201, res.text
    return res.json()

def nearby(client, user, **params):
    return client.get("/api/resources", params={**HERE, **params}, headers=auth(user))

# Test access control
def test_requires_login(client, db):
    res = client.get("/api/resources", params=HERE)
    assert res.status_code == 401
    
def test_regular_user_forbidden(client, db):
    user = make_user(db, role="user")
    res = nearby(client, user)
    assert res.status_code == 403
    
def test_firefighter_allowed(client, db):
    firefighter = make_user(db, role="firefighter")
    res = nearby(client, firefighter)
    assert res.status_code == 200
    
def test_admin_allowed(client, db):
    admin = make_user(db, role="admin")
    res = nearby(client, admin)
    assert res.status_code == 200
    
# Test data shape and sorting
def test_lists_available_resource_with_distance(client, db):
    owner = make_user(db, role="user")
    register(client, owner, name="Near Tank")
    firefighter = make_user(db, role="firefighter")
    
    res = nearby(client, firefighter)
    
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] == 1
    item = body["data"][0]
    assert item["name"] == "Near Tank"
    assert item["distance"] == 0.0
    assert item["externalPin"] == HERE
    assert set(item) == {
        "id", "resource", "otherResource", "capacity", "capacityUnit", "otherCapacity",
        "status", "availableFrom", "availableUntil", "location", "externalPin", "name",
        "contact", "distance",
    }
    
def test_sorted_nearest_first(client, db):
    owner = make_user(db, role="user")
    register(client, owner, name="Near", externalPin={"lat": -25.7461, "lng": 28.1881})
    register(client, owner, name="Far", externalPin={"lat": -26.5, "lng": 29.5})
    register(client, owner, name="Middle", externalPin={"lat": -25.9, "lng": 28.4})
    firefighter = make_user(db, role="firefighter")
    
    body = nearby(client, firefighter).json()
    
    names = [r["name"] for r in body["data"]]
    assert names == ["Near", "Middle", "Far"]
    distances = [r["distance"] for r in body["data"]]
    assert distances == sorted(distances)
    
# Test filters
def test_default_status_filter_excludes_non_available(client, db):
    owner = make_user(db, role="user")
    register(client, owner, name="Available One")
    unavailable = register(client, owner, name="Unavailable One")
    db.query(WaterResource).filter_by(id=unavailable["id"]).update({"status": "unavailable"})
    db.commit()
    firefighter = make_user(db, role="firefighter")
    
    body = nearby(client, firefighter).json()
    
    assert [r["name"] for r in body["data"]] == ["Available One"]
    
def test_status_filter_can_be_overridden(client, db):
    owner = make_user(db, role="user")
    dispatched = register(client, owner, name="Dispatched One")
    db.query(WaterResource).filter_by(id=dispatched["id"]).update({"status": "dispatched"})
    db.commit()
    firefighter = make_user(db, role="firefighter")
    
    body = nearby(client, firefighter, status="dispatched").json()
    
    assert [r["name"] for r in body["data"]] == ["Dispatched One"]
    
def test_radius_km_excludes_far_resources(client, db):
    owner = make_user(db, role="user")
    register(client, owner, name="Near", externalPin={"lat": -25.7461, "lng": 28.1881})
    register(client, owner, name="Far", externalPin={"lat": -26.5, "lng": 29.5})
    firefighter = make_user(db, role="firefighter")
    
    body = nearby(client, firefighter, radius_km=5).json()
    
    assert [r["name"] for r in body["data"]] == ["Near"]
    
def test_radius_km_must_be_positive(client, db):
    firefighter = make_user(db, role="firefighter")
    res = nearby(client, firefighter, radius_km=0)
    assert res.status_code == 422
    
def test_missing_lat_lng_is_422(client, db):
    firefighter = make_user(db, role="firefighter")
    res = client.get("/api/resources", headers=auth(firefighter))
    assert res.status_code == 422