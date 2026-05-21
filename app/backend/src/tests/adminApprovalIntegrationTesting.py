import copy
from admin import adminRoleApproval

ORIGINAL_ROLE_REQUESTS = copy.deepcopy(adminRoleApproval.ROLE_REQUESTS)

def reset_requests():
    adminRoleApproval.ROLE_REQUESTS = copy.deepcopy(ORIGINAL_ROLE_REQUESTS)

def test_get_role_requests(client):
    reset_requests()

    response = client.get("/api/admin/roles/role-requests")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(req["request_id"] == "req_1" for req in data)
    assert any(req["request_id"] == "req_2" for req in data)

def test_approve_admin_request(client):
    reset_requests()

    response = client.post("/api/admin/roles/role-requests/req_2/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"

def test_approve_firefighter_with_valid_license(client):
    reset_requests()

    response = client.post("/api/admin/roles/role-requests/req_1/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "approved"

def test_reject_firefighter_with_invalid_license(client):
    reset_requests()

    adminRoleApproval.ROLE_REQUESTS.append({
        "request_id": "req_13",
        "user_id": "user_13",
        "role": "firefighter",
        "status": "pending",
        "firefighter_license_id": "INVALID"
    })

    response = client.post("/api/admin/roles/role-requests/req_13/approve")
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

def test_reject_pending_request(client):
    reset_requests()

    response = client.post("/api/admin/roles/role-requests/req_2/reject")
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"

def test_approve_already_processed_request_returns_400(client):
    reset_requests()

    client.post("/api/admin/roles/role-requests/req_2/reject")
    response = client.post("/api/admin/roles/role-requests/req_2/approve")
    assert response.status_code == 400
    assert response.json()["detail"] == "Request already processed"

def test_request_not_found_returns_404(client):
    reset_requests()

    response = client.post("/api/admin/roles/role-requests/nonexistent/approve")
    assert response.status_code == 404