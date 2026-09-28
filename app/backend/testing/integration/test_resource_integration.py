from conftest import make_user
from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.models.water_resource import WaterResource

VALID = {
    "resource": "water_tank",
    "otherResource": "",
    "otherCapacity": "",
    "capacity": 5000,
    "capacityUnit": "liters",
    "availableFrom": "2026-09-20",
    "availableUntil": "",
    "location": "Farm on Old Warmbaths Rd, Pretoria North",
    "externalPin": {"lat": -25.7461, "lng": 28.1881},
    "name": "Pieter van der Merwe",
    "contact": "082 456 1234",
}

def auth(user):
    token = create_access_token({'user_id': user.id})
    return {"Cookie": f"access_token={token}"}

def register(client, user, **overrides):
    return client.post("/api/users/resources", json={**VALID, **overrides}, headers=auth(user))

# Test POST /api/users/resources
def test_register_requires_login(client, db):
    res = client.post("/api/users/resources", json=VALID)
    assert res.status_code == 401
    assert db.query(WaterResource).count() == 0
    
def test_resgister_persists_resource_and_location(client, db):
    user = make_user(db)
    res = register(client, user)
    
    assert res.status_code == 201, res.text
    body = res.json()
    row = db.query(WaterResource).filter_by(id=body["id"]).one()
    assert row.user_id == user.id
    assert row.name == "Pieter van der Merwe"
    assert row.capacity == 5000
    assert row.status.value == "available"
    assert row.available_from.isoformat() == "2026-09-20"
    assert row.available_until is None
    
    from sqlalchemy import func
    
    lat, lng = db.query(func.ST_Y(WaterResource.location_geom), func.ST_X(WaterResource.location_geom)).filter_by(id=body["id"]).one()
    assert (round(lat, 4), round(lng, 4)) == (-25.7461, 28.1881)
    assert body["externalPin"] == {"lat": -25.7461, "lng": 28.1881}
    
def test_every_role_can_register(client, db):
    for role in ("user", "firefighter", "admin"):
        res = register(client, make_user(db, role=role))
        assert res.status_code == 201, f"{role}: {res.text}"
        
def test_register_all_resource_types(client, db):
    user = make_user(db)
    expected_units = {
        "water_tank": "liters",
        "borehole": "liters",
        "trailer": "liters",
        "dam": "liters",
        "aircraft": "liters",
        "crew": "members",
    }
    for rtype, unit in expected_units.items():
        capacity = 8 if rtype == "crew" else 1000
        res = register(client, user, resource=rtype, capacity=capacity)
        assert res.status_code == 201, f"{rtype}: {res.text}"
        assert res.json()["capacityUnit"] == unit
        
def test_register_other_resource(client, db):
    user = make_user(db)
    res = register(
        client,
        user,
        resource="other",
        otherResource="Diesel generator + 500L fuel supply",
        otherCapacity="L of fuel",
        capacity=500,
        capacityUnit="other",
    )
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["capacityUnit"] == "other"
    assert body["otherResource"] == "Diesel generator + 500L fuel supply"
    assert body["otherCapacity"] == "L of fuel"
    
def test_register_with_end_date(client, db):
    user = make_user(db)
    res = register(client, user, availableUntil="2026-09-25")
    assert res.status_code == 201, res.text
    assert res.json()["availableUntil"] == "2026-09-25"
    
def test_register_ignores_unknown_fields(client, db):
    user = make_user(db)
    res = register(client, user, fireRef="FR-2026-ABC123")
    assert res.status_code == 201, res.text
    assert "fireRef" not in res.json()
    
def test_register_rejects_invalid_input(client, db):
    user = make_user(db)
    for bad in (
        {"name": "1234"},
        {"contact": "123"},
        {"capacity": 0},
        {"externalPin": {"lat": 0, "lng": 0}},
        {"resource": "other", "otherResource": ""},
        {"availableFrom": "2026-09-20", "availableUntil": "2026-09-01"},
    ):
        res = register(client, user, **bad)
        assert res.status_code == 422, f"{bad} -> {res.status_code}"
    assert db.query(WaterResource).count() == 0
    
# Test GET /api/users/resources
def test_list_requires_login(client, db):
    assert client.get("/api/users/resources").status_code == 401
    
def test_list_rejects_bad_paging_params(client, db):
    user = make_user(db)
    for query in ("limit=0", "limit=101", "offset=-1"):
        res = client.get(f"/api/users/resources?{query}", headers=auth(user))
        assert res.status_code == 422, query

def test_list_empty(client, db):
    user = make_user(db)
    res = client.get("/api/users/resources", headers=auth(user))
    assert res.status_code == 200
    assert res.json() == {"data": [], "total": 0}
    
def test_regular_user_only_sees_own_resources(client, db):
    alice, bob = make_user(db), make_user(db)
    register(client, alice, name="Alice Tank")
    register(client, bob, name="Bob Tank")
    
    res = client.get("/api/users/resources", headers=auth(alice))
    
    assert res.status_code == 200
    body = res.json()
    assert body["total"] == 1
    assert [r["name"] for r in body["data"]] == ["Alice Tank"]
    
def test_firefighter_and_admin_see_everything(client, db):
    alice, bob = make_user(db), make_user(db)
    register(client, alice, name="Alice Tank")
    register(client, bob, name="Bob Tank")
    
    for role in ("firefighter", "admin"):
        res = client.get("/api/users/resources", headers=auth(make_user(db, role=role)))
        assert res.status_code == 200
        assert res.json()["total"] == 2, role
        
def test_list_shape_matches_frontend_type(client, db):
    user = make_user(db)
    register(client, user)
    item = client.get("/api/users/resources", headers=auth(user)).json()["data"][0]
    assert set(item) == {
        "id", "resource", "otherResource", "capacity", "capacityUnit", "otherCapacity",
        "status", "availableFrom", "availableUntil", "location", "externalPin", "name",
        "contact"
    }
    assert item["externalPin"] == {"lat": -25.7461, "lng": 28.1881}
    
def test_list_pagination_newest_first(client, db):
    user = make_user(db)
    for n in range(3):
        register(client, user, name=f"Resource {n}")
        
    page1 = client.get("/api/users/resources?limit=2", headers=auth(user)).json()
    page2 = client.get("/api/users/resources?limit=2&offset=2", headers=auth(user)).json()
    
    assert page1["total"] == 3
    assert [r["name"] for r in page1["data"]] == ["Resource 2", "Resource 1"]
    assert [r["name"] for r in page2["data"]] == ["Resource 0"]
    



