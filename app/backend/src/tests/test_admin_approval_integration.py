"""
tests/test_admin_roles.py

Covers every endpoint in app/routers/admin.py:
  GET  /api/admin/roles/role-requests
  POST /api/admin/roles/role-requests/{id}/approve
  POST /api/admin/roles/role-requests/{id}/reject
  POST /api/admin/roles/role-requests/{id}/revoke
"""
import uuid
from tests.conftest import make_user, make_role_request


# ---------------------------------------------------------------------------
# GET /api/admin/roles/role-requests
# ---------------------------------------------------------------------------
class TestListRoleRequests:
    def test_empty_returns_empty_list(self, client):
        res = client.get("/api/admin/roles/role-requests")
        assert res.status_code == 200
        body = res.json()
        assert body["data"] == []
        assert body["total"] == 0

    def test_returns_all_requests(self, client, db):
        user = make_user(db)
        make_role_request(db, user, status="pending")
        make_role_request(db, user, status="approved")

        res = client.get("/api/admin/roles/role-requests")
        assert res.status_code == 200
        body = res.json()
        assert body["total"] == 2
        assert len(body["data"]) == 2

    def test_response_shape(self, client, db):
        user = make_user(db, full_name="Alice Smith", email="alice@test.com")
        make_role_request(db, user, role="firefighter", license_id="LIC-001")

        res = client.get("/api/admin/roles/role-requests")
        item = res.json()["data"][0]

        assert "request_id" in item
        assert "user_id" in item
        assert item["user_full_name"] == "Alice Smith"
        assert item["email"] == "alice@test.com"
        assert item["role"] == "firefighter"
        assert item["status"] == "pending"
        assert item["firefighter_license_id"] == "LIC-001"


# ---------------------------------------------------------------------------
# POST /api/admin/roles/role-requests/{id}/approve
# ---------------------------------------------------------------------------
class TestApproveRoleRequest:
    def test_approve_pending_request(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="pending")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/approve")
        assert res.status_code == 200
        body = res.json()
        assert body["status"] == "approved"
        assert str(body["request_id"]) == str(req.request_id)

    def test_approve_non_pending_returns_400(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="approved")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/approve")
        assert res.status_code == 400
        assert "approved" in res.json()["detail"]

    def test_approve_nonexistent_returns_404(self, client):
        fake_id = uuid.uuid4()
        res = client.post(f"/api/admin/roles/role-requests/{fake_id}/approve")
        assert res.status_code == 404

    def test_approve_rejected_request_returns_400(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="rejected")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/approve")
        assert res.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/admin/roles/role-requests/{id}/reject
# ---------------------------------------------------------------------------
class TestRejectRoleRequest:
    def test_reject_pending_request(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="pending")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/reject")
        assert res.status_code == 200
        assert res.json()["status"] == "rejected"

    def test_reject_already_rejected_returns_400(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="rejected")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/reject")
        assert res.status_code == 400

    def test_reject_approved_request_returns_400(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="approved")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/reject")
        assert res.status_code == 400

    def test_reject_nonexistent_returns_404(self, client):
        res = client.post(f"/api/admin/roles/role-requests/{uuid.uuid4()}/reject")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# POST /api/admin/roles/role-requests/{id}/revoke
# ---------------------------------------------------------------------------
class TestRevokeRoleRequest:
    def test_revoke_approved_request(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="approved")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/revoke")
        assert res.status_code == 200
        assert res.json()["status"] == "revoked"

    def test_revoke_pending_returns_400(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="pending")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/revoke")
        assert res.status_code == 400

    def test_revoke_already_revoked_returns_400(self, client, db):
        user = make_user(db)
        req = make_role_request(db, user, status="revoked")

        res = client.post(f"/api/admin/roles/role-requests/{req.request_id}/revoke")
        assert res.status_code == 400

    def test_revoke_nonexistent_returns_404(self, client):
        res = client.post(f"/api/admin/roles/role-requests/{uuid.uuid4()}/revoke")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# Health check (sanity)
# ---------------------------------------------------------------------------
def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}