import uuid
from datetime import datetime, timedelta

import pytest

from app.backend.main import app
from app.backend.src.dependencies.auth import get_current_user
from app.backend.src.models.saved_location import SavedLocation
from app.backend.src.services.users.saved_location import MAX_SAVED_LOCATIONS
from app.backend.testing.integration.conftest import make_user

BASE = "/api/users/saved-locations"
VALID = {"label": "Home", "address": "1 Main St", "lat": -26.2, "lng": 28.0}

# --------------------------- helpers --------------------------------------
def url(location_id: str) -> str:
    return f"{BASE}/{location_id}"

def make_location(db, user, label="Home", address="1 Main St", lat=-26.2, lng=28.0, minutes=0):
    has_point = lat is not None and lng is not None
    location = SavedLocation(
        id=str(uuid.uuid4()),
        user_id=user.id,
        label=label,
        address=address,
        location_geom=f"SRID=4326;POINT({lng} {lat})" if has_point else None,
        created_at=datetime(2026, 1, 1, 12, 0) + timedelta(minutes=minutes),
    )
    db.add(location)
    db.commit()
    return location

def reload(db, location_id: str):
    db.expire_all()
    return db.get(SavedLocation, location_id)

@pytest.fixture
def me(db):
    return make_user(db, full_name="John Doe", email="john@example.com")

@pytest.fixture
def signed_in(client, me):
    app.dependency_overrides[get_current_user] = lambda: me
    yield me
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def other(db):
    return make_user(db, email="other@example.com")

# ------------------------------ auth ----------------------------
@pytest.mark.parametrize(
    "method, path, body",
    [
        ("GET", BASE, None), 
        ("POST", BASE, VALID), 
        ("GET", f"{BASE}/any-id", None), 
        ("PATCH", f"{BASE}/any-id", VALID),
        ("DELETE", f"{BASE}/any-id", None),
    ],
)

def test_endpoint_without_token_returns_401(client, method, path, body):
    assert client.request(method, path, json=body).status_code == 401

# --------------------------- list -------------------------------------------
def test_list_empty_returns_empty_list(client, signed_in):
    response = client.get(BASE)
    
    assert (response.status_code, response.json()) == (200, [])

def test_list_returns_only_my_locations_in_creation_order(client, db, signed_in, other):
    second = make_location(db, signed_in, label="Second", minutes=2)
    first = make_location(db, signed_in, label="First", minutes=1)
    make_location(db, other, label="Not mine")

    body = client.get(BASE).json()

    assert [item["id"] for item in body] == [first.id, second.id]

def test_list_item_exposes_only_the_documented_fields(client, db, signed_in):
    make_location (db, signed_in)

    item = client.get(BASE).json()[0]

    assert set(item) == {"id", "label", "address", "lat", "lng", "created_at"}

def test_list_returns_stored_coordinates(client, db, signed_in):
    make_location(db, signed_in, lat=-26.2, lng=28.0)

    item = client.get(BASE).json()[0]

    assert item["lat"] == pytest.approx(-26.2)
    assert item["lng"] == pytest.approx(28.0)

def test_list_location_without_coordinates_returns_nulls(client, db, signed_in):
    make_location(db, signed_in, lat=None, lng=None)
    
    item = client.get (BASE). json()[0]
    
    assert (item["lat"], item["lng"]) == (None, None)

# ---------------------------- get one ----------------------------------------------
def test_get_own_location_returns_200(client, db, signed_in):
    location = make_location(db, signed_in)

    response = client.get(url(location.id))

    assert response.status_code == 200
    assert response.json()["id"] == location.id

def test_get_other_users_location_returns_404(client, db, signed_in, other):
    foreign = make_location(db, other)

    response = client.get(url(foreign.id))

    assert response.status_code == 404
    assert response.json() == {"detail": f"Saved location {foreign.id} does not exist"}

def test_get_unknown_location_returns_404(client, signed_in):
    missing_id = str(uuid.uuid4())
    
    response = client.get(url(missing_id))
    
    assert response.status_code == 404
    assert response.json() == {"detail": f"Saved location {missing_id} does not exist"}

# ---------------------------- create -------------------------------------------------------
def test_create_returns_the_new_location(client, signed_in):
    response = client.post(BASE, json=VALID)

    assert response.status_code == 200
    body = response.json()
    assert (body["label"], body["address"]) == ("Home", "1 Main St")
    assert (body["lat"], body["lng"]) == (-26.2, 28.0)
    assert set(body) == {"id", "label", "address", "lat", "lng", "created_at"}


def test_create_persists_for_the_current_user(client, db, signed_in):
    body = client.post(BASE, json=VALID).json()

    stored = reload(db, body["id"])
    assert (stored.user_id, stored.label, stored.address) == (signed_in.id, "Home", "1 Main St")


def test_create_then_list_includes_it_with_stored_coordinates(client, signed_in):
    created = client.post(BASE, json=VALID).json()

    item = client.get(BASE).json()[0]

    assert item["id"] == created["id"]
    assert item["lat"] == pytest.approx(-26.2)
    assert item["lng"] == pytest.approx(28.0)

def test_create_with_null_coordinates_returns_nulls(client, signed_in):
    response = client.post(BASE, json={**VALID, "lat": None, "lng": None})

    assert response.status_code == 200
    assert (response.json()["lat"], response.json()["lng"]) == (None, None)


def test_create_boundary_values_are_accepted(client, signed_in):
    body = {"label": "x" * 50, "address": "x" * 225, "lat": 90, "lng": 180}

    assert client.post(BASE, json=body).status_code == 200


@pytest.mark.parametrize(
    "override",
    [
        {"lat": 91}, {"lat": -91}, {"lng": 181}, {"lng": -181},
        {"label": ""}, {"label": "x" * 51}, {"label": None},
        {"address": ""}, {"address": "x" * 226},
    ],
)

def test_create_invalid_payload_returns_422_and_saves_nothing(client, db, signed_in, override):
    response = client.post(BASE, json={**VALID, **override})

    assert response.status_code == 422
    db.expire_all()
    assert db.query(SavedLocation).filter_by(user_id=signed_in.id).count() == 0

@pytest.mark.parametrize("missing", ["label", "address", "lat", "lng"])
def test_create_missing_field_returns_422(client, signed_in, missing):
    body = {k: v for k, v in VALID.items() if k != missing}

    assert client.post(BASE, json=body).status_code == 422


def test_create_over_limit_returns_409(client, db, signed_in):
    for i in range(MAX_SAVED_LOCATIONS):
        make_location(db, signed_in, label=f"L{i}", minutes=i)

    response = client.post(BASE, json=VALID)

    assert response.status_code == 409
    assert response.json()["detail"] == f"You can save at most {MAX_SAVED_LOCATIONS} locations"


def test_create_limit_is_per_user(client, db, signed_in, other):
    for i in range(MAX_SAVED_LOCATIONS):
        make_location(db, other, label=f"L{i}", minutes=i)

    assert client.post(BASE, json=VALID).status_code == 200


def test_create_after_delete_frees_a_slot(client, db, signed_in):
    locations = [
        make_location(db, signed_in, label=f"L{i}", minutes=i)
        for i in range(MAX_SAVED_LOCATIONS)
    ]
    client.delete(url(locations[0].id))

    assert client.post(BASE, json=VALID).status_code == 200

# ---------------------------- upsate -----------------------------------------------------------------
def test_patch_updates_label_and_address_and_persists(client, db, signed_in):
    location = make_location(db, signed_in)

    response = client.patch(url(location.id), json={**VALID, "label": "Work", "address": "2 Side St"})

    assert response.status_code == 200
    assert (response.json()["label"], response.json()["address"]) == ("Work", "2 Side St")
    stored = reload(db, location.id)
    assert (stored.label, stored.address) == ("Work", "2 Side St")


def test_patch_coordinates_updates_the_point(client, db, signed_in):
    location = make_location(db, signed_in)

    body = client.patch(url(location.id), json={**VALID, "lat": 10.5, "lng": 20.5}).json()

    assert body["lat"] == pytest.approx(10.5)
    assert body["lng"] == pytest.approx(20.5)


def test_patch_null_coordinates_clear_the_point(client, db, signed_in):
    location = make_location(db, signed_in)

    body = client.patch(url(location.id), json={**VALID, "lat": None, "lng": None}).json()

    assert (body["lat"], body["lng"]) == (None, None)


# current behaviour: PATCH needs the full body (the 'deafult' typo).
# If the typo is ever fixed, a partial body should return 200 instead.
@pytest.mark.parametrize("missing", ["label", "address", "lat", "lng"])
def test_patch_partial_body_returns_422_and_changes_nothing(client, db, signed_in, missing):
    location = make_location(db, signed_in)
    body = {k: v for k, v in VALID.items() if k != missing}

    assert client.patch(url(location.id), json=body).status_code == 422
    assert reload(db, location.id).label == "Home"


@pytest.mark.parametrize(
    "override",
    [
        {"label": ""}, {"label": "x" * 51}, {"label": None},
        {"address": ""}, {"address": "x" * 226},
        {"lat": 91}, {"lng": 181},
    ],
)
def test_patch_invalid_value_returns_422_and_changes_nothing(client, db, signed_in, override):
    location = make_location(db, signed_in)

    response = client.patch(url(location.id), json={**VALID, **override})

    assert response.status_code == 422
    assert reload(db, location.id).label == "Home"


def test_patch_other_users_location_returns_404_and_leaves_it_unchanged(
    client, db, signed_in, other
):
    foreign = make_location(db, other)

    response = client.patch(url(foreign.id), json={**VALID, "label": "Hacked"})

    assert response.status_code == 404
    assert reload(db, foreign.id).label == "Home"


def test_patch_unknown_location_returns_404(client, signed_in):
    assert client.patch(url(str(uuid.uuid4())), json=VALID).status_code == 404

# ------------------------- deleted -------------------------------------------------------
def test_delete_own_location_removes_it(client, db, signed_in):
    location = make_location(db, signed_in)

    response = client.delete(url(location.id))

    assert response.status_code == 200
    assert response.json() == {"detail": "Saved location deleted"}
    assert reload(db, location.id) is None


def test_delete_only_removes_the_requested_location(client, db, signed_in):
    keep = make_location(db, signed_in, label="Keep", minutes=1)
    remove = make_location(db, signed_in, label="Remove", minutes=2)

    client.delete(url(remove.id))

    assert reload(db, keep.id) is not None


def test_delete_other_users_location_returns_404_and_keeps_it(client, db, signed_in, other):
    foreign = make_location(db, other)

    response = client.delete(url(foreign.id))

    assert response.status_code == 404
    assert reload(db, foreign.id) is not None


def test_delete_unknown_location_returns_404(client, signed_in):
    assert client.delete(url(str(uuid.uuid4()))).status_code == 404


def test_delete_twice_second_call_returns_404(client, db, signed_in):
    location = make_location(db, signed_in)
    client.delete(url(location.id))

    assert client.delete(url(location.id)).status_code == 404