import pytest

from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole
from app.backend.src.services.admin import role_request

from conftest import make_orphaned_role_request, make_role_request, make_user

#----------approve role request----------

def test_approve_sets_status_approved(db):
    """Approve pending request should change status to approved"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="pending")
    admin = make_user(db, role="admin")
    result = role_request.approve_role_request(req.request_id, admin.id, db)
    assert result.status == RequestStatus.approved
    
def test_approve_records_reviewer_and_timestamp(db):
    """Approve should stamp revied_by and reviewed_at on request"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="pending")
    admin = make_user(db, role="admin")
    result = role_request.approve_role_request(req.request_id, admin.id, db)
    assert result.reviewed_by == admin.id
    assert result.reviewed_at is not None
    
def test_approve_grants_requested_role_to_user(db):
    """Approve should promote requesting user to requested role"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="pending")
    admin = make_user(db, role="admin")
    role_request.approve_role_request(req.request_id, admin.id, db)
    db.refresh(user)
    assert user.role == UserRole.admin
    
def test_approve_missing_request_returns_none(db):
    """Approving a request_id that does not exist should return Non, not raise"""
    admin = make_user(db, role="admin")
    result = role_request.approve_role_request("does-not-exist", admin.id, db)
    assert result is None

def test_approve_already_approved_raises(db):
    """A request that's aleady approved cannot be approved again"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="approved")
    admin = make_user(db, role="admin")
    with pytest.raises(ValueError, match="already approved"): role_request.approve_role_request(req.request_id, admin.id, db)
     
def test_approve_already_rejected_raises(db):
    """A rejected request cannot be approved"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="rejected")
    admin = make_user(db, role="admin")
    with pytest.raises(ValueError, match="already rejected"): role_request.approve_role_request(req.request_id, admin.id, db)
        
def test_approve_orphaned_user_raises(db):
    """If request's user_id no longer resolves to a user, approval shaould fail"""
    req = make_orphaned_role_request(db, role="admin", status="pending")
    admin = make_user(db, role="admin") 
    with pytest.raises(ValueError, match="User not found"): role_request.approve_role_request(req.request_id, admin.id, db)
   
def test_approve_failed_lookup_leaves_status_pending(db):
    """A failed approval (missing user) must not leave the request half-updated"""
    req = make_orphaned_role_request(db, role="admin", status="pending")
    admin = make_user(db, role="admin")
    try:
        role_request.approve_role_request(req.request_id, admin.id, db)
    except ValueError:
        pass
    db.refresh(req)
    assert req.status == RequestStatus.pending
    assert req.reviewed_by is None
    
#-------reject role request------------
def test_reject_sets_status_rejected(db):
    """Rejecting a pending request should change status to rejected"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="pending")
    admin = make_user(db, role="admin")
    result = role_request.reject_role_request(req.request_id, admin.id, db)
    assert result.status == RequestStatus.rejected
    
def test_reject_does_not_change_user_role(db):
    """Rejecting must not alter user's existing role"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="pending")
    admin = make_user(db, role="admin")
    role_request.reject_role_request(req.request_id, admin.id, db)
    db.refresh(user)
    assert user.role == UserRole.user
    
def test_reject_missing_request_returns_none(db):
    """Rejecting a request_id that doesn't exist should return None, not raise"""
    admin = make_user(db, role="admin")
    result = role_request.reject_role_request("does-not-exist", admin.id, db)
    assert result is None
    
def test_reject_non_pending_raises(db):
    """Only pending requests can be rejected"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="revoked")
    admin = make_user(db, role="admin")
    with pytest.raises(ValueError, match="already revoked"): role_request.reject_role_request(req.request_id, admin.id, db)
    
def test_reject_orphaned_user_raises(db):
    """If request's user_id no longer resolves to a user, reject should fail"""
    req = make_orphaned_role_request(db, role="admin", status="pending")
    admin = make_user(db, role="admin")
    with pytest.raises(ValueError, match="User not found"): role_request.reject_role_request(req.request_id, admin.id, db)
        
#--------revoke role request----------
def test_revoke_sets_status_revoked(db):
    """Revoking an approved request should change its status to revoked"""
    user = make_user(db, role="admin")
    req = make_role_request(db, user, role="admin", status="approved")
    admin = make_user(db, role="admin")
    result = role_request.revoke_role_request(req.request_id, admin.id, db)
    assert result.status == RequestStatus.revoked
    
def test_revoke_restores_users_previous_role(db):
    """Revoking should roll the user's role back to current_role at request time"""
    user = make_user(db, role="admin")
    req = make_role_request(db, user, role="admin", status="approved")
    req.current_role = UserRole.user
    db.commit()
    admin = make_user(db, role="admin")
    role_request.revoke_role_request(req.request_id, admin.id, db)
    db.refresh(user)
    assert user.role == UserRole.user
    
def test_revoke_missing_request_returns_none(db):
    """Revoking a request_id that doesn't exist should return None, not raise"""
    admin = make_user(db, role="admin")
    result = role_request.revoke_role_request("does-not-exist", admin.id, db)
    assert result is None
    
def test_revoke_non_approved_raises(db):
    """Only approved requests can be revoked"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="pending")
    admin = make_user(db, role="admin")
    with pytest.raises(ValueError, match="Only approved"): role_request.revoke_role_request(req.request_id, admin.id, db)

def test_revoke_already_revoked_raises(db):
    """A request that's already revoked cannot be revoked again"""
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="revoked")
    admin = make_user(db, role="admin")
    with pytest.raises(ValueError, match="Only approved"): role_request.revoke_role_request(req.request_id, admin.id, db)
        
def test_revoke_orphaned_user_raises(db):
    """If the request's user_id no longer resolves to a user, revoke should fail"""
    req = make_orphaned_role_request(db, role="admin", status="approved")
    admin = make_user(db, role="admin")
    with pytest.raises(ValueError, match="User not found"): role_request.revoke_role_request(req.request_id, admin.id, db)
        
#---------get role requests-----------
def test_get_role_requests_empty(db):
    """With no requests in db, listing should be empty with total 0"""
    result = role_request.get_role_requests(db)
    assert result == {"data": [], "total": 0}
    
def test_get_role_requests_returns_created_requests(db):
    """Listing should include requests that were created"""
    user1 = make_user(db, role="user")
    user2 = make_user(db, role="user")
    req1 = make_role_request(db, user1, role="admin", status="pending")
    req2 = make_role_request(db, user2, role="firefighter", status="pending")
    result = role_request.get_role_requests(db)
    ids = {r.request_id for r in result["data"]}
    assert {req1.request_id, req2.request_id} <= ids
    assert result["total"] == len(result["data"])