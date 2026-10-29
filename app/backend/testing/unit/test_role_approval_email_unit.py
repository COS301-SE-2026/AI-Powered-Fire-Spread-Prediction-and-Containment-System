import asyncio
import logging
from unittest.mock import MagicMock, patch

import pytest 
from fastapi import BackgroundTasks, HTTPException

from app.backend.src.routes.admin import role_requests as routes
from app.backend.src.services.auth import email as email_service

SERVICE_PATCH = "app.backend.src.routes.admin.role_requests.role_request"

# Email builders
BUILDERS = [
    (email_service.send_role_approved_email, "firefighter", "Firefighter", "approved"),
    (email_service.send_role_approved_email, "admin", "Admin", "approved"),
    (email_service.send_role_rejected_email, "firefighter", "Firefighter", "rejected"),
    (email_service.send_role_revoked_email, "admin", "Admin", "revoked"),
]

@pytest.mark.parametrize("builder, role, label, keyword", BUILDERS)
@patch.object(email_service, "send_email")
def test_builders_send_to_user_with_role_in_subject_and_body(
    mock_send, builder, role, label, keyword
):
    builder("jane@example.com", "Jane", role)
    
    mock_send.assert_called_once()
    to, subject, body = mock_send.call_args.args
    assert to == "jane@example.com"
    assert label in subject
    assert keyword in subject
    assert "Jane" in body
    assert label in body
    
@patch.object(email_service, "send_email")
def test_approved_email_links_to_login(mock_send):
    email_service.send_role_approved_email("jane@example.com", "Jane", "admin")
    
    body = mock_send.call_args.args[2]
    assert f"{email_service.FRONTEND_URL}/login" in body
    
@patch.object(email_service, "send_email")
def test_builders_format_underscored_role_as_title(mock_send):
    email_service.send_role_approved_email("jane@example.com", "Jane", "super_admin")
    
    subject = mock_send.call_args.args[1]
    assert "Super Admin" in subject
    
@pytest.mark.parametrize("builder, role, label, keyword", BUILDERS)
@patch.object(email_service, "send_email")
def test_builders_escape_html_in_name(mock_send, builder, role, label, keyword):
    builder("jane@example.com", "<script>alert(1)</script>", role)
    
    body = mock_send.call_args.args[2]
    assert "<script>" not in body
    assert "&lt;script&gt;" in body


@pytest.mark.parametrize("builder, role, label, keyword", BUILDERS)
@patch.object(email_service, "send_email", side_effect=RuntimeError("ses down"))
def test_builders_propagate_send_failure(mock_send, builder, role, label, keyword):
    """The builders don't swallow errors. The route wrapper is what handles them"""
    with pytest.raises(RuntimeError):
        builder("jane@example.com", "Jane", role)
        
# Safe wrapper 
def test_safe_wrapper_calls_send_function_with_arguments():
    send_fn = MagicMock(__name__="send_fn")
    routes.send_email_safe(send_fn, "jane@example.com", "Jane", "admin")
    send_fn.assert_called_once_with("jane@example.com", "Jane", "admin")
    
def test_safe_wrapper_swallows_and_logs_failure(caplog):
    send_fn = MagicMock(side_effect=RuntimeError("ses down"), __name__="send_fn")
    with caplog.at_level(logging.ERROR):
        routes.send_email_safe(send_fn, "jane@example.com", "Jane", "admin")
        
    assert "jane@example.com" in caplog.text
    
# Routes queue the correct email
ROUTE_EMAILS = [
    (routes.approve_role_request, "approve_role_request", routes.send_role_approved_email),
    (routes.reject_role_request, "reject_role_request", routes.send_role_rejected_email),
    (routes.revoke_role_request, "revoke_role_request", routes.send_role_revoked_email),
]

def make_updated_request():
    request = MagicMock()
    request.user.email = "jane@example.com"
    request.user.name = "Jane"
    request.requested_role.value = "firefighter"
    return request

@pytest.mark.parametrize("route, service_fn, email_fn", ROUTE_EMAILS)
@patch(SERVICE_PATCH)
def test_route_queues_email_for_user(mock_service, route, service_fn, email_fn):
    getattr(mock_service, service_fn).return_value = make_updated_request()
    tasks = MagicMock(spec=BackgroundTasks)
    
    route(request_id="req-1", background_tasks=tasks, db=MagicMock(), admin=MagicMock(id="admin-1"))
    
    tasks.add_task.assert_called_once_with(
        routes.send_email_safe, email_fn, "jane@example.com", "Jane", "firefighter"
    )
    
@pytest.mark.parametrize("route, service_fn, email_fn", ROUTE_EMAILS)
@patch(SERVICE_PATCH)
def test_route_does_not_queue_email_when_request_not_found(mock_service, route, service_fn, email_fn):
    getattr(mock_service, service_fn).return_value = None
    tasks = MagicMock(spec=BackgroundTasks)
    
    with pytest.raises(HTTPException) as error:
        route(request_id="req-1", background_tasks=tasks, db=MagicMock(), admin=MagicMock(id="admin-1"))
        
    assert error.value.status_code == 404
    tasks.add_task.assert_not_called()
    
@pytest.mark.parametrize("route, service_fn, email_fn", ROUTE_EMAILS)
@patch(SERVICE_PATCH)
def test_route_does_not_queue_email_when_service_rejects(mock_service, route, service_fn, email_fn):
    getattr(mock_service, service_fn).side_effect = ValueError("aleady approved")
    tasks = MagicMock(spec=BackgroundTasks)
    
    with pytest.raises(HTTPException) as error:
        route(request_id="req-1", background_tasks=tasks, db=MagicMock(), admin=MagicMock(id="admin-1"))
        
    assert error.value.status_code == 400
    tasks.add_task.assert_not_called()
    
@pytest.mark.parametrize("route, service_fn, email_fn", ROUTE_EMAILS)
@patch(SERVICE_PATCH)
def test_route_still_succeeds_when_email_fails(mock_service, route, service_fn, email_fn):
    """"Run real BackgroundTasks with a failing email function: the decision is unaffected"""
    updated = make_updated_request()
    getattr(mock_service, service_fn).return_value = updated
    tasks = BackgroundTasks()
    
    def failing_email(to, name, role):
        raise RuntimeError("ses down")
    
    with patch.object(routes, email_fn.__name__, new=failing_email):
        result = route(request_id="req-1", background_tasks=tasks, db=MagicMock(), admin=MagicMock(id="admin"))
        asyncio.run(tasks())
        
    assert result is updated