from datetime import datetime 
from types import SimpleNamespace 
from unittest. mock import MagicMock, patch

import pytest
from fastapi import HTTPException 
from pydantic import ValidationError 
from sqlalchemy.exc import SQLAlchemyError

import app.backend.src.models.users  
from app.backend.src.models.saved_location import SavedLocation 
from app.backend.src.routes.users import saved_location as routes 
from app.backend.src.schemas.saved_locations import (
    SavedLocationCreate, 
    SavedLocationUpdate,
)
from app.backend.src.services.users import saved_location as service

SERVICE_PATCH = "saved_location_service"
USER_ID = "user-1"
CREATED = datetime (2026, 1, 1, 12, 0)
POINT = "SRID=4326;POINT(28.0 -26.2)"

@pytest.fixture
def user():
    return SimpleNamespace(id=USER_ID)

@pytest.fixture 
def location ():
    return SimpleNamespace(
        id="loc-1",
        user_id=USER_ID, 
        label="Home",
        address="1 Main St", 
        location_geom=POINT, 
        created_at=CREATED,
    )

def db_with_first(result) -> MagicMock:
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = result
    return db

def db_with_count(count: int) -> MagicMock:
    db = MagicMock()
    db.query.return_value.filter.return_value.count.return_value = count
    return db

def create_payload(**overrides) -> SavedLocationCreate:
    data = {"label": "Home", "address": "1 Main St", "lat": -26.2, "lng": 28.0}
    data.update(overrides)
    return SavedLocationCreate(**data)

def update_payload(**overrides) -> SavedLocationUpdate:
    data = {"label": "Home", "address": "1 Main St", "lat": -26.2, "lng": 28.0}
    data.update(overrides)
    return SavedLocationUpdate(**data)

# ----------------------------------- schemas --------------------------------------------
def test_create_schema_valid_payload():
    payload = create_payload()

    assert (payload.label, payload.address, payload.lat, payload.lng) == (
        "Home", "1 Main St", -26.2, 28.0,
    )

@pytest.mark.parametrize("missing", ["label", "address", "lat", "lng"])
def test_create_schema_requires_every_field_today(missing):
    data = {"label": "Home", "address": "1 Main St", "lat": 1.0, "lng": 2.0}
    data.pop(missing)

    with pytest.raises(ValidationError):
        SavedLocationCreate(**data)

def test_create_schema_allows_null_coordinates():
    payload = create_payload (lat=None, lng=None)
    
    assert (payload. lat, payload.lng) == (None, None)

@pytest.mark.parametrize(
    "override",
    [
        {"lat": 90.1}, {"lat": -90.1}, {"lng": 180.1}, {"lng": -180.1},
        {"label": ""}, {"label": "x" * 51}, {"label": None},
        {"address": ""}, {"address": "x" * 226}, {"address": None},
    ],
)

def test_create_schema_rejects_invalid_values(override):
    with pytest.raises(ValidationError):
        create_payload (**override)

def test_create_schema_accepts_boundary_values():
    payload = create_payload(lat=90, lng=-180, label="x" * 50, address="x" * 225)

    assert (payload.lat, payload.lng) == (90, -180)

@pytest.mark.parametrize("missing", ["label", "address", "lat", "lng"])
def test_update_schema_requires_every_field_today(missing):
    data = {"label": "Home", "address": "1 Main St", "lat": 1.0, "lng": 2.0}
    data.pop(missing)

    with pytest.raises(ValidationError):
        SavedLocationUpdate(**data)

@pytest.mark.parametrize(
    "override",
    [
        {"label": ""}, {"label": "x" * 51}, {"label": None},
        {"address": ""}, {"address": "x" * 226}, {"address": None},
        {"lat": 91}, {"lat": -91}, {"lng": 181}, {"lng": -181},
    ],
)

def test_update_schema_rejects_invalid_values(override):
    with pytest.raises(ValidationError):
        update_payload (**override)

def test_update_schema_allows_null_coordinates() :
    payload = update_payload (lat=None, lng=None)

    assert (payload.lat, payload. lng) == (None, None)

# --------------- service: get_saved_locations -------------------------
def test_get_saved_locations_formats_each_row(location):
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
        (location, -26.2, 28.0)
    ]

    assert service.get_saved_locations(db, USER_ID) == [
        {
            "id": "loc-1",
            "label": "Home",
            "address": "1 Main St",
            "lat": -26.2,
            "lng": 28.0,
            "created_at": CREATED,
        }
    ]

def test_get_saved_locations_empty_returns_empty_list():
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

    assert service.get_saved_locations(db, USER_ID) == []

# ---------------------- servoce: get_my_saved_locations -----------------------------------------
def test_get_my_saved_location_returns_formatted_location(location):
    result = service.get_my_saved_locations(
        "loc-1", USER_ID, db_with_first ((location, -26.2, 28.0))
    )

    assert (result["id"], result["lat"], result["lng"]) == ("loc-1", -26.2, 28.0)

def test_get_my_saved_location_missing_raises_value_error():
    with pytest.raises(ValueError, match="Saved location nope does not exist"):
        service.get_my_saved_locations ("nope", USER_ID, db_with_first(None))

# ------------------------------ service: create ------------------------------------------------
def test_create_below_limit_adds_commits_and_refreshes():
    db = db_with_count(service.MAX_SAVED_LOCATIONS - 1)
    
    service.create_saved_location(create_payload(), USER_ID, db)
    
    order = [c[0] for c in db.method_calls if c[0] in ("add", "commit", "refresh")]
    assert order == ["add", "commit", "refresh"]

def test_create_at_limit_raises_and_does_not_add() :
    db = db_with_count (service.MAX_SAVED_LOCATIONS)
    
    with pytest.raises (ValueError, match="at most"):
        service. create_saved_location(create_payload(), USER_ID, db)
    
    db.add.assert_not_called()
    db.commit.assert_not_called()

def test_create_stores_owner_label_address_and_uuid():
    db = db_with_count(0)

    service.create_saved_location(create_payload(), USER_ID, db)

    saved = db.add.call_args.args[0]
    assert isinstance(saved, SavedLocation)
    assert (saved.user_id, saved.label, saved.address) == (USER_ID, "Home", "1 Main St")
    assert len(saved.id) == 36

def test_create_point_is_written_longitude_first ():
    db = db_with_count(0)

    service.create_saved_location(create_payload(lat=-26.2, lng=28.0), USER_ID, db)
    
    assert db.add.call_args.args[0].location_geom == POINT

def test_create_without_coordinates_stores_no_geometry():
    db = db_with_count(0)
    
    result = service.create_saved_location(
        create_payload(lat=None, lng=None), USER_ID, db
    )

    assert db.add.call_args.args[0].location_geom is None
    assert (result["lat"], result["lng"]) == (None, None)

@pytest.mark.parametrize("override", [{"lat": None}, {"lng": None}]) 
def test_create_with_only_one_coordinate_stores_no_geometry(override):
    db = db_with_count(0)
    
    service.create_saved_location(create_payload(**override), USER_ID, db)
    
    assert db.add.call_args.args[0].location_geom is None

def test_create_returns_formatted_location_with_payload_coordinates() :
    result = service. create_saved_location(create_payload(), USER_ID, db_with_count(0))
    
    assert (result["label"], result["lat"], result["lng"]) == ("Home", -26.2, 28.0)

def test_create_commit_failure_propagates_and_skips_refresh():
    db = db_with_count(0)
    db.commit.side_effect = SQLAlchemyError("connection lost")
    
    with pytest.raises(SQLAlchemyError):
        service.create_saved_location(create_payload(), USER_ID, db)
    
    db.refresh.assert_not_called()

# --------------------------- service: update --------------------------------------------
@patch.object(service, "get_my_saved_locations")
def test_update_changes_label_and_address(mock_get, location):
    service.update_saved_location(
        "loc-1", USER_ID, update_payload(label="Work", address="2 Side St"),
        db_with_first(location),
    )

    assert (location.label, location.address) == ("Work", "2 Side St")

@patch.object(service, "get_my_saved_locations")
def test_update_rewrites_geometry_longitude_first(mock_get, location):
    service.update_saved_location(
    "loc-1", USER_ID, update_payload(lat=1.5, lng=2.5), db_with_first(location)
    )

    assert location.location_geom == "SRID=4326;POINT(2.5 1.5)"

@patch.object(service, "get_my_saved_locations")
def test_update_null_coordinates_clear_geometry(mock_get, location):
    service. update_saved_location(
        "loc-1", USER_ID, update_payload(lat=None, lng=None), db_with_first(location)
    )
    
    assert location. location_geom is None

@patch.object (service, "get_my_saved_locations")
def test_update_commits_then_refreshes_then_returns_fresh_read(mock_get, location):
    db = db_with_first(location)
    
    result = service.update_saved_location("loc-1", USER_ID, update_payload(), db)
    
    order = [c[0] for c in db.method_calls if c[0] in ("commit", "refresh")]
    assert order == ["commit", "refresh"]
    mock_get.assert_called_once_with("loc-1", USER_ID, db)
    assert result is mock_get.return_value

def test_update_missing_location_raises_and_does_not_commit():
    db = db_with_first(None)
    
    with pytest.raises(ValueError, match="does not exist"):
        service.update_saved_location("nope", USER_ID, update_payload(), db)
    
    db.commit.assert_not_called()

# --------------------------- service: delete ----------------------------------------------
def test_delete_removes_and_commits(location):
    db = db_with_first(location)
    
    service.delete_saved_location("loc-1", USER_ID, db)
    
    db.delete.assert_called_once_with(location)
    db.commit.assert_called_once()

def test_delete_missing_location_raises_and_does_not_delete():
    db = db_with_first(None)
    with pytest.raises(ValueError, match= "does not exist"): 
        service. delete_saved_location ("nope", USER_ID, db)
    
    db.delete.assert_not_called()
    db. commit.assert_not_called()

# ---------------------------------- routes ------------------------------------------------
@patch.object(routes, SERVICE_PATCH)
def test_list_route_passes_db_and_user_id(mock_service, user):
    db = MagicMock ()

    result = routes.list_saved_locations(db=db, user=user)
    
    mock_service.get_saved_locations.assert_called_once_with(db, USER_ID)
    assert result is mock_service.get_saved_locations.return_value

@patch.object(routes, SERVICE_PATCH)
def test_get_route_passes_id_user_and_db(mock_service, user):
    db = MagicMock()
    
    result = routes.get_saved_location(location_id="loc-1", db=db, user=user)
    
    mock_service.get_my_saved_locations.assert_called_once_with("loc-1", USER_ID, db)
    assert result is mock_service.get_my_saved_locations.return_value

@patch.object(routes, SERVICE_PATCH)
def test_get_route_missing_returns_404_with_service_message(mock_service, user):
    mock_service.get_my_saved_locations.side_effect = ValueError("gone")

    with pytest.raises(HTTPException) as error:
        routes.get_saved_location(location_id="x", db=MagicMock(), user=user)

    assert (error.value.status_code, error.value.detail) == (404, "gone")

@patch.object(routes, SERVICE_PATCH)
def test_add_route_passes_payload_user_and_db(mock_service, user):
    payload, db = create_payload(), MagicMock()
    
    result = routes.add_saved_location(payload=payload, db=db, user=user)
    
    mock_service. create_saved_location.assert_called_once_with(payload, USER_ID, db)
    assert result is mock_service.create_saved_location.return_value

@patch.object(routes, SERVICE_PATCH)
def test_add_route_limit_reached_returns_409(mock_service, user):
    mock_service.create_saved_location.side_effect = ValueError("at most 6")
    
    with pytest.raises(HTTPException) as error:
        routes.add_saved_location(payload=create_payload(), db=MagicMock(), user=user)
    
    assert (error.value.status_code, error.value.detail) == (409, "at most 6")

@patch.object(routes, SERVICE_PATCH)
def test_edit_route_passes_arguments_in_service_order(mock_service, user):
    payload, db = update_payload(label="Work"), MagicMock()
    
    routes.edit_saved_location(location_id="loc-1", payload=payload, db=db, user=user)
    
    mock_service.update_saved_location.assert_called_once_with("loc-1", USER_ID, payload, db)

@patch.object(routes, SERVICE_PATCH)
def test_edit_route_missing_returns_404(mock_service, user):
    mock_service.update_saved_location.side_effect = ValueError("gone")

    with pytest.raises(HTTPException) as error:
        routes.edit_saved_location(
            location_id="x", payload=update_payload(), db=MagicMock(), user=user
        )
    assert error.value.status_code == 404

@patch.object(routes, SERVICE_PATCH)
def test_delete_route_returns_confirmation(mock_service, user):
    db = MagicMock()
    
    result = routes.remove_saved_location(location_id="loc-1", db=db, user=user)
    
    mock_service.delete_saved_location.assert_called_once_with("loc-1", USER_ID, db)
    assert result == {"detail": "Saved location deleted"}

@patch.object(routes, SERVICE_PATCH)
def test_delete_route_missing_returns_404(mock_service, user):
    mock_service.delete_saved_location.side_effect = ValueError("gone")
    
    with pytest.raises(HTTPException) as error:
        routes.remove_saved_location(location_id="x", db=MagicMock(), user=user)
    
    assert error.value.status_code == 404

@patch.object(routes, SERVICE_PATCH)
def test_unexpected_error_is_not_masked_as_404(mock_service, user):
    mock_service.delete_saved_location.side_effect = RuntimeError("db down")

    with pytest.raises(RuntimeError):
        routes.remove_saved_location(location_id="x", db=MagicMock(), user=user)