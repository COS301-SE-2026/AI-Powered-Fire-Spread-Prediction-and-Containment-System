from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.services.admin import role_request

#----------approve role request----------

def test_approve_sets_status_approved(db_session, scenario):
    """Approve pending request should change status to approved"""
    admin_id, user, req = scenario(status=RequestStatus.pending)
    result = role_request.approve_role_request(req.request_id, admin_id, db_session)
    assert result.status == RequestStatus.approved
    
def test_approve_records_reviewer_and_timestamp(db_session, scenario):
    """Approve should stamp revied_by and reviewed_at on request"""
    admin_id, user, req = scenario(status=RequestStatus.pending)
    result = role_request.approve_role_request(req.request_is, admin_id, db_session)
    assert result.reviewed_by == admin_id
    assert result.reviewed_at is not None
    
def test_approve_grants_requested_role_to_user(db_session, scenario):
    """Approve should promote requesting user to requested role"""
    admin_id, user, req = scenario(status=RequestStatus.pending, requested_role=UserRole.admin, current_role=UserRole.user)
    role_request.approve_role_request(req.request_id, admin_id, db_session)
    db_session.refresh(user)
    assert user.role == UserRole.admin
    
def test_approve_missing_request_returns_none(db_session, scenario):
    """Approving a request_id that does not exist should return Non, not raise"""
    admin_id, _, _ = scenario()
    result = role_request.approve_role_request("does-not-exist", admin_id, db_session)
    assert result is None

def test_approve_already_approved_raises(db_session, scenario):
    """A request that's aleady approved cannot be approved again"""
    admin_id, user, req = scenario(status=RequestStatus.approved)
    try:
        role_request.approve_role_request(req.request_id, admin_id, db_session)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "already approved" in str(e)
