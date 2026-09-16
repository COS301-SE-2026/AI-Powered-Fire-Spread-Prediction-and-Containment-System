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
    result = role_request.approve_role_request(req.request_id, admin_id, db_session)
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

def test_approve_already_rejected_raises(db_session, scenario):
    """A rejected request cannot be approved"""
    admin_id, user, req = scenario(status=RequestStatus.rejected)
    try:
        role_request.approve_role_request(req.request_id, admin_id, db_session)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "already rejected" in str(e)
        
def test_approve_orphaned_user_raises(db_session, scenario):
    """If request's user_id no longer resolves to a user, approval shaould fail"""
    admin_id, _, req = scenario(status=RequestStatus.pending, orphan=True)
    try:
        role_request.approve_role_request(req.request_id, admin_id, db_session)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "User not found" in str(e)
        
def test_approve_failed_lookup_leaves_status_pending(db_session, scenario):
    """A failed approval (missing user) must not leave the request half-updated"""
    admin_id, _, req = scenario(status=RequestStatus.pending, orphan=True)
    try:
        role_request.approve_role_request(req.request_id, admin_id, db_session)
    except ValueError:
        pass
    db_session.refresh(req)
    assert req.status == RequestStatus.pending
    assert req.reviewed_by is None
    
#-------reject role request------------
def test_reject_sets_status_rejected(db_session, scenario):
    """Rejecting a pending request should change status to rejected"""
    admin_id, user, req = scenario(status=RequestStatus.pending)
    result = role_request.reject_role_request(req.request_id, admin_id, db_session)
    assert result.status == RequestStatus.rejected
    
def test_reject_does_not_change_user_role(db_session, scenario):
    """Rejecting must not alter user's existing role"""
    admin_id, user, req = scenario(status=RequestStatus.pending, current_role=UserRole.user)
    role_request.reject_role_request(req.request_id, admin_id, db_session)
    db_session.refresh(user)
    assert user.role == UserRole.user
    
def test_reject_missing_request_returns_none(db_session, scenario):
    """Rejecting a request_id that doesn't exist should return None, not raise"""
    admin_id, _, _ = scenario()
    result = role_request.reject_role_request("does-not-exist", admin_id, db_session)
    assert result is None
    
def test_reject_non_pending_raises(db_session, scenario):
    """Only pending requests can be rejected"""
    admin_id, user, req = scenario(status=RequestStatus.revoked)
    try:
        role_request.reject_role_request(req.request_id, admin_id, db_session)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "already revoked" in str(e)
    
def test_reject_orphaned_user_raises(db_session, scenario):
    """If request's user_id no longer resolves to a user, reject should fail"""
    admin_id , _, req = scenario(status=RequestStatus.pending, orphan=True)
    try:
        role_request.reject_role_request(req.request_id, admin_id, db_session)
        assert False, "expected ValueError"
    except ValueError as e:
        assert "User not found" in str(e)
        
#--------revoke role request----------
def test_revoke_sets_status_revoked(db_session, scenario):
    """Revoking an approved request should change its status to revoked"""
    admin_id, user, req = scenario(status=RequestStatus.approved)
    result = role_request.revoke_role_request(req.request_id, admin_id, db_session)
    assert result.status == RequestStatus.revoked
    
def test_revoke_restores_users_previous_role(db_session, scenario):
    """Revoking should roll the user's role back to current_role at request time"""
    admin_id, user, req = scenario(status=RequestStatus.approved, requested_role=UserRole.admin, current_role=UserRole.user)
    role_request.revoke_role_request(req.request_id, admin_id, db_session)
    db_session.refresh(user)
    assert user.role == UserRole.user
    
def test_revoke_missing_request_returns_none(db_session, scenario):
    """Revoking a request_id that doesn't exist should return None, not raise"""
    admin_id, _, _ = scenario()
    result = role_request.revoke_role_request("does-not-exist", admin_id, db_session)
    assert result is None