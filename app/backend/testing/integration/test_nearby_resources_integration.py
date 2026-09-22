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