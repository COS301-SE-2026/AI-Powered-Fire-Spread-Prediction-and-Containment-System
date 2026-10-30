from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException

from app.backend.src.models.workers import WorkerNode
from app.backend.src.schemas.workers import WorkerRegisterRequest
from app.backend.src.services import workers as worker_service


class TestWorkerServiceUnit:
    def test_generate_worker_key_with_parameters(self):
        mock_valkey = MagicMock()
        with patch.object(worker_service, "valkey_client", mock_valkey):
            result = worker_service.generate_worker_key(
                user_id="usr_123",
                label="Office Rig",
                gpu_name="RTX 4090",
                request_host="localhost:8000",
            )

        key = result["registration_key"]
        assert key.startswith("REG-")
        assert result["expires_in_seconds"] == worker_service.REGISTRATION_KEY_TTL
        assert key in result["docker_command"]
        assert "docker run" in result["docker_command"]
        mock_valkey.setex.assert_called_once()

    def test_reset_worker_key_not_found_raises_404(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            worker_service.reset_worker_key(db, "w_unknown", "usr_123", "localhost:8000")
        assert exc.value.status_code == 404

    def test_reset_worker_key_unauthorized_user_raises_403(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner")
        db.query.return_value.filter.return_value.first.return_value = node

        with pytest.raises(HTTPException) as exc:
            worker_service.reset_worker_key(db, "w_1", "usr_stranger", "localhost:8000")
        assert exc.value.status_code == 403

    def test_reset_worker_key_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", label="Node 1", gpu_name="RTX 3080")
        db.query.return_value.filter.return_value.first.return_value = node
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            res = worker_service.reset_worker_key(
                db, "w_1", "usr_owner", "localhost:8000"
            )

        assert res["registration_key"].startswith("REG-")
        assert "docker run" in res["docker_command"]
        mock_valkey.setex.assert_called_once()

    def test_get_worker_command_not_found_raises_404(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            worker_service.get_worker_command(db, "w_unknown", "usr_1", "localhost:8000")
        assert exc.value.status_code == 404

    def test_get_worker_command_unauthorized_raises_403(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner")
        db.query.return_value.filter.return_value.first.return_value = node

        with pytest.raises(HTTPException) as exc:
            worker_service.get_worker_command(db, "w_1", "usr_other", "localhost:8000")
        assert exc.value.status_code == 403

    def test_get_worker_command_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", label="MyNode")
        db.query.return_value.filter.return_value.first.return_value = node

        cmd = worker_service.get_worker_command(db, "w_1", "usr_owner", "localhost:8000")
        assert isinstance(cmd, dict)
        assert "docker_command" in cmd
        assert "docker run" in cmd["docker_command"]

    def test_register_worker_node_low_vram_raises_400(self):
        db = MagicMock()
        req = WorkerRegisterRequest(
            registration_key="REG-1111222233334444",
            label="test-rig",
            gpu_name="Weak GPU",
            vram_mb=2048,
            driver_version="550.54",
            cuda_capable=True,
        )
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            with pytest.raises(HTTPException) as exc:
                worker_service.register_worker_node(db, req)
        assert exc.value.status_code == 400
        mock_valkey.getdel.assert_not_called()

    def test_register_worker_node_unknown_key_raises_401(self):
        db = MagicMock()
        req = WorkerRegisterRequest(
            registration_key="REG-EXPIRED00000000",
            label="test-rig",
            gpu_name="RTX 4090",
            vram_mb=24576,
            driver_version="550.54",
            cuda_capable=True,
        )
        mock_valkey = MagicMock()
        mock_valkey.getdel.return_value = None

        with patch.object(worker_service, "valkey_client", mock_valkey):
            with pytest.raises(HTTPException) as exc:
                worker_service.register_worker_node(db, req)
        assert exc.value.status_code == 401

    def test_register_worker_node_success_new_worker(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        def assign_id_on_add(instance):
            if hasattr(instance, "id") and not instance.id:
                instance.id = "w-new-created-id"

        db.add.side_effect = assign_id_on_add

        mock_valkey = MagicMock()
        mock_valkey.getdel.return_value = "usr_100"

        req = WorkerRegisterRequest(
            registration_key="REG-AAAABBBBCCCCDDDD",
            label="New Rig",
            gpu_name="RTX 4090",
            vram_mb=24576,
            driver_version="550.54",
            cuda_capable=True,
        )

        with patch.object(worker_service, "valkey_client", mock_valkey):
            response = worker_service.register_worker_node(db, req)

        token_type = response.get("token_type") if isinstance(response, dict) else response.token_type
        worker_id = response.get("worker_id") if isinstance(response, dict) else response.worker_id

        assert token_type.lower() == "bearer"
        assert worker_id is not None
        db.add.assert_called_once()
        db.commit.assert_called_once()

    def test_register_worker_node_success_reattaches_existing(self):
        db = MagicMock()
        existing_node = MagicMock(
            id="w_existing",
            user_id="usr_100",
            status="offline",
            label="Old Rig",
            vram_mb=8192,
        )
        db.query.return_value.filter.return_value.first.return_value = existing_node

        mock_valkey = MagicMock()
        mock_valkey.getdel.return_value = "usr_100:w_existing"

        req = WorkerRegisterRequest(
            registration_key="REG-AAAABBBBCCCCDDDD",
            label="Updated Rig",
            gpu_name="RTX 3080",
            vram_mb=10240,
            driver_version="550.54",
            cuda_capable=True,
        )

        with patch.object(worker_service, "valkey_client", mock_valkey):
            response = worker_service.register_worker_node(db, req)

        worker_id = response.get("worker_id") if isinstance(response, dict) else response.worker_id
        assert worker_id == "w_existing"
        assert existing_node.status == "active"
        assert existing_node.vram_mb == 10240
        db.commit.assert_called_once()

    def test_list_workers_admin_returns_all(self):
        db = MagicMock()
        mock_all = [MagicMock(id="w_1"), MagicMock(id="w_2")]
        db.query.return_value.order_by.return_value.all.return_value = mock_all

        result = worker_service.list_workers(db, user_id="admin_1", is_admin=True)
        assert result == mock_all
        db.query.assert_called_once_with(WorkerNode)

    def test_list_workers_volunteer_returns_filtered(self):
        db = MagicMock()
        mock_user_workers = [MagicMock(id="w_vol_1")]
        q = db.query.return_value.filter.return_value.order_by.return_value
        q.all.return_value = mock_user_workers

        result = worker_service.list_workers(db, user_id="vol_1", is_admin=False)
        assert result == mock_user_workers

    def test_activate_worker_node_not_found_raises_404(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            worker_service.activate_worker_node(db, "w_unknown", "usr_1", is_admin=False)
        assert exc.value.status_code == 404

    def test_activate_worker_node_unauthorized_raises_403(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner")
        db.query.return_value.filter.return_value.first.return_value = node

        with pytest.raises(HTTPException) as exc:
            worker_service.activate_worker_node(db, "w_1", "usr_other", is_admin=False)
        assert exc.value.status_code == 403

    def test_activate_worker_node_admin_override_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", status="deactivated")
        db.query.return_value.filter.return_value.first.return_value = node
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            res = worker_service.activate_worker_node(db, "w_1", "usr_admin", is_admin=True)

        assert res.status == "active"
        mock_valkey.sadd.assert_called_with("worker:pool:idle", "w_1")
        db.commit.assert_called_once()

    def test_activate_worker_node_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", status="deactivated")
        db.query.return_value.filter.return_value.first.return_value = node
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            res = worker_service.activate_worker_node(db, "w_1", "usr_owner", is_admin=False)

        assert res.status == "active"
        mock_valkey.sadd.assert_called_with("worker:pool:idle", "w_1")
        db.commit.assert_called_once()

    def test_deactivate_worker_node_not_found_raises_404(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            worker_service.deactivate_worker_node(db, "w_unknown", "usr_1", is_admin=True)
        assert exc.value.status_code == 404

    def test_deactivate_worker_node_unauthorized_raises_403(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner")
        db.query.return_value.filter.return_value.first.return_value = node

        with pytest.raises(HTTPException) as exc:
            worker_service.deactivate_worker_node(db, "w_1", "usr_intruder", is_admin=False)
        assert exc.value.status_code == 403

    def test_deactivate_worker_node_admin_override_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", status="active")
        db.query.return_value.filter.return_value.first.return_value = node
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            res = worker_service.deactivate_worker_node(db, "w_1", "usr_admin", is_admin=True)

        assert res.status == "deactivated"
        mock_valkey.srem.assert_called_with("worker:pool:idle", "w_1")
        db.commit.assert_called_once()

    def test_deactivate_worker_node_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", status="active")
        db.query.return_value.filter.return_value.first.return_value = node
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            res = worker_service.deactivate_worker_node(db, "w_1", "usr_owner", is_admin=False)

        assert res.status == "deactivated"
        mock_valkey.srem.assert_called_with("worker:pool:idle", "w_1")
        db.commit.assert_called_once()

    def test_remove_worker_node_not_found_raises_404(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            worker_service.remove_worker_node(db, "w_unknown", "decommission", "usr_1", is_admin=True)
        assert exc.value.status_code == 404

    def test_remove_worker_node_unauthorized_raises_403(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner")
        db.query.return_value.filter.return_value.first.return_value = node

        with pytest.raises(HTTPException) as exc:
            worker_service.remove_worker_node(db, "w_1", "decommission", "usr_intruder", is_admin=False)
        assert exc.value.status_code == 403

    def test_remove_worker_node_admin_override_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", status="active", removal_reason=None)
        db.query.return_value.filter.return_value.first.return_value = node
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            res = worker_service.remove_worker_node(
                db, "w_1", "Decommissioned by admin", "usr_admin", is_admin=True
            )

        assert res.status == "removed"
        assert res.removal_reason == "Decommissioned by admin"
        mock_valkey.srem.assert_called_with("worker:pool:idle", "w_1")
        db.commit.assert_called_once()

    def test_remove_worker_node_success(self):
        db = MagicMock()
        node = MagicMock(id="w_1", user_id="usr_owner", status="active", removal_reason=None)
        db.query.return_value.filter.return_value.first.return_value = node
        mock_valkey = MagicMock()

        with patch.object(worker_service, "valkey_client", mock_valkey):
            res = worker_service.remove_worker_node(
                db, "w_1", "Hardware failure", "usr_owner", is_admin=False
            )

        assert res.status == "removed"
        assert res.removal_reason == "Hardware failure"
        mock_valkey.srem.assert_called_with("worker:pool:idle", "w_1")
        db.commit.assert_called_once()