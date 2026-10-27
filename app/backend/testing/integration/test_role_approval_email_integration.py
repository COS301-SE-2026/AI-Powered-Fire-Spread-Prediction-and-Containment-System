from unittest.mock import patch

import pytest

from app.backend.src.dependencies.auth import create_access_token
from app.backend.src.enums.role_request_status import RequestStatus
from app.backend.src.enums.user_role import UserRole

from conftest import make_role_request, make_user

SEND_EMAIL = "app.backend.src.services.auth.email.send_email"

def auth(user):
    """Cookie auth, same pattern as other integration tests"""
    token = create_access_token({"user_id": user.id})
    return {"Cookie": f"access_token={token}"}

@pytest.fixture
def mock_send():
    with patch(SEND_EMAIL) as mocked:
        yield mocked
        
def call(client, action, request_id, acting_user):
    return client.put(f"/api/admin/role-requests/{request_id}/{action}", headers=auth(acting_user))

# Test approve
@pytest.mark.parametrize("role", ["firefighter", "admin"])
def test_approve_sends_email_to_requesting_user(client, db, mock_send, role):
    admin = make_user(db, role="admin")
    user = make_user(db, full_name="Jane Doe", role="user")
    req = make_role_request(db, user, role=role, status="pending")
    
    res = call(client, "approve", req.request_id, admin)
    
    assert res.status_code == 200
    mock_send.assert_called_once()
    to, subect, body = mock_send.call_args.args
    assert to == user.email
    assert "approved" in subect
    assert role.title() in subect
    assert "Jane" in body
    
def test_approve_updates_role_and_sends_email(client, db, mock_send):
    admin = make_user(db, role="admin")
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="firefighter", status="pending")
    
    call(client, "approve", req.request_id, admin)
    
    db.refresh(user)
    assert user.role == UserRole.firefighter
    assert mock_send.call_count == 1
    
def test_approve_email_not_sent_to_admin(client, db, mock_send):
    admin = make_user(db, role="admin")
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="admin", status="pending")
    
    call(client, "approve", req.request_id, admin)
    
    recipients = [c.args[0] for c in mock_send.call_args_list]
    assert admin.email not in recipients
    
def test_approve_still_succeeds_when_email_fails(client, db):
    """SES being down must not undo or fail the approval"""
    admin = make_user(db, role="admin")
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="firefighter", status="pending")
    
    with patch(SEND_EMAIL, side_effect=RuntimeError("ses down")):
        res = call(client, "approve", req.request_id, admin)
        
    assert res.status_code == 200
    db.refresh(user)
    db.refresh(req)
    assert user.role == UserRole.firefighter
    assert req.status == RequestStatus.approved
    
# Test reject
def test_reject_sends_email_and_keeps_role(client, db, mock_send):
    admin = make_user(db, role="admin")
    user = make_user(db, full_name="Jane Doe", role="user")
    req = make_role_request(db, user, role="firefighter", status="pending")
    
    res = call(client, "reject", req.request_id, admin)
    
    assert res.status_code == 200
    db.refresh(user)
    assert user.role == UserRole.user
    mock_send.assert_called_once()
    to, subject, body = mock_send.call_args.args
    assert to == user.email
    assert "Firefighter" in subject
    assert "Jane" in body
    
def test_reject_still_succeeds_when_email_fails(client, db):
    admin = make_user(db, role="admin")
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="firefighter", status="pending")
    
    with patch(SEND_EMAIL, side_effect=RuntimeError("ses down")):
        res = call(client, "reject", req.request_id, admin)
        
    assert res.status_code == 200
    db.refresh
    assert req.status == RequestStatus.rejected
    
# Test revoke
def test_revoke_sends_email_and_restores_previous_role(client, db, mock_send):
    admin = make_user(db, role="admin")
    user = make_user(db, full_name="Jane Doe", role="user")
    req = make_role_request(db, user, role="firefighter", status="approved")
    user.role = UserRole.firefighter
    db.commit()
    
    res = call(client, "revoke", req.request_id, admin)
    
    assert res.status_code == 200
    db.refresh(user)
    assert user.role == UserRole.user
    mock_send.assert_called_once()
    to, subject, body = mock_send.call_args.args
    assert to == user.email
    assert "revoked" in subject
    assert "Jane" in body
    
def test_revoke_still_succeeds_when_email_fails(client, db):
    admin = make_user(db, role="admin")
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="firefighter", status="approved")
    
    with patch(SEND_EMAIL, side_effect=RuntimeError("ses down")):
        res = call(client, "revoke", req.request_id, admin)
        
    assert res.status_code == 200
    db.refresh(req)
    assert req.status == RequestStatus.revoked
    
# Test when no email when nothing happens
@pytest.mark.parametrize(
    "action, bad_status",
    [
        ("approve", "approved"),    # already approved
        ("approve", "rejected"),    # already rejected
        ("reject", "approved"),     # only pending can be rejected
        ("revoke", "pending"),  # only approved can be revoked
    ],
)
def test_invalid_state_returns_400_and_sends_no_email(client, db, mock_send, action, bad_status):
    admin = make_user(db, role="admin")
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="firefighter", status=bad_status)
    
    res = call(client, action, req.request_id, admin)
    
    assert res.status_code == 400
    mock_send.assert_not_called()
    
@pytest.mark.parametrize("action", ["approve", "reject", "revoke"])
def test_unknown_request_returns_404_and_send_no_email(client, db, mock_send, action):
    admin = make_user(db, role="admin")
    
    res = call(client, action, "does-not-exist", admin)
    
    assert res.status_code == 404
    mock_send.assert_not_called()
    
# Test access control
@pytest.mark.parametrize("action", ["approve", "reject", "revoke"])
def test_non_admin_gets_403_and_no_email(client, db, mock_send, action):
    regular = make_user(db, role="user")
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="firefighter", status="pending")
    
    res = call(client, action, req.request_id, regular)
    
    assert res.status_code == 403
    mock_send.assert_not_called()
    db.refresh(req)
    assert req.status == RequestStatus.pending
    
@pytest.mark.parametrize("action", ["approve", "reject", "revoke"])
def test_unauthenticated_gets_401_and_no_email(client, db, mock_send, action):
    user = make_user(db, role="user")
    req = make_role_request(db, user, role="firefighter", status="pending")
    
    res = client.put(f"/api/admin/role-requests/{req.request_id}/{action}")
    
    assert res.status_code == 401
    mock_send.assert_not_called()
