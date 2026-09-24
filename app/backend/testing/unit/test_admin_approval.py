
import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch

from app.backend.main import app
from app.backend.db import get_db

from app.backend.src.dependencies.auth import get_current_admin_user
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.routes.admin import role_requests as routes
from app.backend.src.services.admin import role_request as service

# action, status fail, status suceed
SERVICE_ACTIONS = [
    (service.approve_role_request, RequestStatus.approved, RequestStatus.pending),
    (service.reject_role_request, RequestStatus.rejected,RequestStatus.pending),
    (service.revoke_role_request, RequestStatus.pending, RequestStatus.approved),
]


# role request row
def make_request(status):
    return MagicMock(
        status=status,
        user_id="user-1",
        requested_role="firefighter",
        current_role="registered_user",
        reviewed_by=None,
        reviewed_at=None,
    )

def make_user(role="registered_user"):
    return MagicMock(id="user-1", role=role)

def make_db(*first_results):
    db = MagicMock()
    db.query.return_value.filter.return_value.first.side_effect = list(first_results)
    return db

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def admin():
    return MagicMock(id="admin-1")

# -------------------Services-------------------------------------------------

# get_role_requests
def test_get_role_requests_returns_data_and_total():
    rows = [object(), object()]
    db = MagicMock()
    db.query.return_value.all.return_value = rows

    assert service.get_role_requests(db) == {"data": rows, "total": 2}


# unknown request id return none
@pytest.mark.parametrize("action, bad, good", SERVICE_ACTIONS)
def test_aservice_request_missing_returns_none(action, bad, good):
    assert action("missing", "admin-1", make_db(None)) is None


@pytest.mark.parametrize("action, bad, good_status", SERVICE_ACTIONS)
def test_service_user_missing_returns_error(action, bad, good_status):
    db = make_db(make_request(good_status), None)

    with pytest.raises(ValueError, match="User not found"):
        action("req-1", "admin-1", db)

@pytest.mark.parametrize("action, bad_status, good", SERVICE_ACTIONS)
def test_service_wrong_status_returns_error(action, bad_status, good):

    with pytest.raises(ValueError):
        action("req-1", "admin-1", make_db(make_request(bad_status)))


@pytest.mark.parametrize (
    "action, start_status, start_role, end_status, end_role",
    [
        (
            service.approve_role_request,
            RequestStatus.pending,
            "registered_user",
            RequestStatus.approved,
            "firefighter",
        ),
        (
            service.reject_role_request,
            RequestStatus.pending,
            "registered_user",
            RequestStatus. rejected,
            "registered_user",
        ),
        (
            service.revoke_role_request,
            RequestStatus.approved,
            "firefighter",
            RequestStatus. revoked,
            "registered_user",
        ),
    ],
)

def test_service_actions_valid_request_updates_and_commits( action, start_status, start_role, end_status, end_role ):
    request = make_request(start_status)
    user = MagicMock(id="user-1", role=start_role)
    db = make_db(request, user)

    result = action("req-1", "admin-1", db)

    assert result is request
    assert request. status == end_status
    assert user. role == end_role
    assert request.reviewed_by == "admin-1"
    assert request. reviewed_at is not None
    db.commit.assert_called_once()

# search_report_table
def test_search_report_table_returns_data_and_total():
    rows = [object(), object()]
    db = MagicMock()
    db.query.return_value.outerjoin.return_value.filter.return_value.all.return_value = rows

    assert service.search_report_table(db, "smith") == {"data": rows, "total": 2}

# ------------------------------------routes-------------------------------------------------------------------------
PATCH = "app.backend.src.routes.admin.role_requests.role_request"
ROUTES = [
    (routes.approve_role_request, "approve_role_request"),
    (routes.reject_role_request, "reject_role_request"),
    (routes.revoke_role_request, "revoke_role_request"),
]

@patch(PATCH)
def test_get_role_requests_route_returns_service_result(mock_service):
    mock_service.get_role_requests.return_value = {"data": [], "total": 0}

    assert routes.get_role_requests(db=MagicMock()) == {"data": [], "total": 0}

@pytest.mark.parametrize("route, service_fn", ROUTES)
@patch(PATCH)
def test_review_routes_request_not_found_raises_404(mock_service, route, service_fn):
    getattr(mock_service, service_fn).return_value = None

    with pytest.raises(HTTPException) as error:
        route(request_id="req-1", db=MagicMock(), admin=MagicMock(id="admin-1"))

    assert error.value.status_code == 404

@pytest.mark.parametrize("route, service_fn", ROUTES)
@patch (PATCH)
def test_review_routes_value_error_raises_400(mock_service, route, service_fn):
    getattr(mock_service, service_fn).side_effect = ValueError("bad state")

    with pytest.raises(HTTPException) as error:
        route(request_id="req-1", db=MagicMock(), admin=MagicMock(id="admin-1"))

    assert error.value.status_code == 400
    assert error.value.detail == "bad state"


@pytest.mark.parametrize("route, service_fn", ROUTES)
@patch(PATCH)
def test_review_routes_success_returns_request_and_passes_ids( mock_service, route, service_fn ):
    db = MagicMock()
    updated_request = object()
    getattr(mock_service, service_fn).return_value = updated_request

    result = route(request_id="req-1", db=db, admin=MagicMock(id="admin-1"))

    assert result is updated_request
    getattr(mock_service, service_fn).assert_called_once_with("req-1", "admin-1", db)

@patch(PATCH)
def test_search_location_table_returns_service_result(mock_service):
    mock_service.search_report_table.return_value = {"data": [], "total": 0}

    result = routes.search_location_table(key="smith", db=MagicMock())

    assert result == {"data": [], "total": 0}

def test_router_requires_admin_user():
    protected_by = [dep.dependency for dep in routes.router.dependencies]

    assert get_current_admin_user in protected_by