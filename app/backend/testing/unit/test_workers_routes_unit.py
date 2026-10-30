import asyncio
from datetime import datetime, timedelta, timezone
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import HTTPException, WebSocketDisconnect, status
from jose import jwt

from app.backend.src.enums.user_role import UserRole
from app.backend.src.models.workers import WorkerNode
from app.backend.src.routes import workers as workers_route
from app.backend.src.routes.workers import (
    activate_worker,
    clear_sim_progress,
    cloud_fallback,
    deactivate_worker,
    dispatch_simulation_task,
    generate_worker_enrollment_key,
    get_compute_distribution,
    get_simulation_progress,
    get_worker_command,
    get_workers,
    has_active_volunteer_workers,
    register_worker,
    reject_worker_credentials,
    remove_worker,
    reset_worker_key,
    set_sim_progress,
    verify_worker_token,
    websocket_worker_endpoint,
)
from app.backend.src.schemas.workers import (
    ComputeDistrubutionRatio,
    WorkerEnrollmentKeyRequest,
    WorkerRemovalRequest,
    WorkerRegisterRequest,
)


@pytest.fixture(autouse=True)
def clean_globals():
    workers_route.active_worker_connections.clear()
    workers_route.pending_results.clear()
    workers_route.job_progress_keys.clear()
    yield
    workers_route.active_worker_connections.clear()
    workers_route.pending_results.clear()
    workers_route.job_progress_keys.clear()


class TestHelperFunctions:
    def test_set_sim_progress_none_key_early_return(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            set_sim_progress(None, "stage1", "message1")
            mock_valkey.setex.assert_not_called()

    def test_set_sim_progress_success(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            set_sim_progress("prog123", "running", "step 1")
            mock_valkey.setex.assert_called_once()
            args, _ = mock_valkey.setex.call_args
            assert args[0] == "sim:progress:prog123"
            assert args[1] == workers_route.PROGRESS_TTL_SECONDS
            payload = json.loads(args[2])
            assert payload["stage"] == "running"
            assert payload["message"] == "step 1"

    def test_set_sim_progress_handles_exception(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            mock_valkey.setex.side_effect = RuntimeError("Valkey offline")
            set_sim_progress("prog123", "running", "step 1")

    def test_clear_sim_progress_none_key_early_return(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            clear_sim_progress(None)
            mock_valkey.delete.assert_not_called()

    def test_clear_sim_progress_success(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            clear_sim_progress("prog123")
            mock_valkey.delete.assert_called_once_with("sim:progress:prog123")

    def test_clear_sim_progress_handles_exception(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            mock_valkey.delete.side_effect = RuntimeError("Valkey error")
            clear_sim_progress("prog123")

    def test_cloud_fallback(self):
        with patch("app.backend.src.routes.workers.set_sim_progress") as mock_set:
            res = cloud_fallback("key123")
            mock_set.assert_called_once_with("key123", "cloud", "Running on cloud worker")
            assert res == {"dispatched_to": "cloud_fallback", "status": "queued"}

    @pytest.mark.asyncio
    async def test_reject_worker_credentials(self):
        ws = AsyncMock()
        await reject_worker_credentials(ws)
        ws.accept.assert_awaited_once()
        ws.close.assert_awaited_once_with(
            code=workers_route.WORKER_CREDENTIAL_INVALID,
            reason="Invalid worker credentials",
        )

    @pytest.mark.asyncio
    async def test_verify_worker_token_success(self, monkeypatch):
        monkeypatch.setattr(workers_route, "JWT_SECRET_KEY", "test-secret")
        token = jwt.encode(
            {"sub": "worker-1", "role": "worker_node", "type": "worker_device"},
            "test-secret",
            algorithm="HS256",
        )
        worker_id = await verify_worker_token(token)
        assert worker_id == "worker-1"

    @pytest.mark.asyncio
    async def test_verify_worker_token_invalid_scope_raises(self, monkeypatch):
        monkeypatch.setattr(workers_route, "JWT_SECRET_KEY", "test-secret")
        token = jwt.encode(
            {"sub": "worker-1", "role": "user", "type": "worker_device"},
            "test-secret",
            algorithm="HS256",
        )
        with pytest.raises(HTTPException) as exc:
            await verify_worker_token(token)
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid worker credentials or scope" in exc.value.detail

    @pytest.mark.asyncio
    async def test_verify_worker_token_jwt_error_raises(self, monkeypatch):
        monkeypatch.setattr(workers_route, "JWT_SECRET_KEY", "test-secret")
        with pytest.raises(HTTPException) as exc:
            await verify_worker_token("invalid.jwt.token")
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Could not validate worker credentails" in exc.value.detail


class TestRestEndpoints:
    def test_get_workers_admin_and_volunteer(self):
        db = MagicMock()
        admin_user = MagicMock(id="adm-1", role=UserRole.admin)
        volunteer_user = MagicMock(id="vol-1", role=UserRole.user)

        with patch.object(workers_route.worker_service, "list_workers") as mock_list:
            mock_list.return_value = ["node1"]
            res_admin = get_workers(db=db, current_user=admin_user)
            mock_list.assert_called_with(db=db, user_id="adm-1", is_admin=True)
            assert res_admin == ["node1"]

            res_vol = get_workers(db=db, current_user=volunteer_user)
            mock_list.assert_called_with(db=db, user_id="vol-1", is_admin=False)
            assert res_vol == ["node1"]

    def test_get_simulation_progress(self):
        user = MagicMock()
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            mock_valkey.get.return_value = json.dumps({"stage": "sim", "message": "50%"})
            res = get_simulation_progress("prog-1", user)
            assert res == {"stage": "sim", "message": "50%"}

            mock_valkey.get.return_value = None
            res_none = get_simulation_progress("prog-2", user)
            assert res_none == {"stage": None, "message": None}

    def test_activate_worker(self):
        db = MagicMock()
        user = MagicMock(id="u1", role=UserRole.admin)
        with patch.object(workers_route.worker_service, "activate_worker_node") as mock_act:
            mock_act.return_value = {"id": "w1", "status": "active"}
            res = activate_worker("w1", db, user)
            mock_act.assert_called_once_with(db=db, worker_id="w1", user_id="u1", is_admin=True)
            assert res["status"] == "active"

    def test_deactivate_worker(self):
        db = MagicMock()
        user = MagicMock(id="u1", role=UserRole.user)
        with patch.object(workers_route.worker_service, "deactivate_worker_node") as mock_deact:
            mock_deact.return_value = {"id": "w1", "status": "deactivated"}
            res = deactivate_worker("w1", db, user)
            mock_deact.assert_called_once_with(db=db, worker_id="w1", user_id="u1", is_admin=False)
            assert res["status"] == "deactivated"

    def test_remove_worker(self):
        db = MagicMock()
        user = MagicMock(id="u1", role=UserRole.admin)
        payload = WorkerRemovalRequest(reason="Maintenance decommissioning")
        with patch.object(workers_route.worker_service, "remove_worker_node") as mock_rem:
            mock_rem.return_value = {"id": "w1", "status": "removed"}
            res = remove_worker("w1", payload, db, user)
            mock_rem.assert_called_once_with(
                db=db,
                worker_id="w1",
                reason="Maintenance decommissioning",
                user_id="u1",
                is_admin=True,
            )
            assert res["status"] == "removed"

    def test_get_worker_command(self):
        db = MagicMock()
        user = MagicMock(id="u1")
        req = MagicMock()
        req.headers.get.return_value = "api.fireaway.test"

        with patch.object(workers_route.worker_service, "get_worker_command") as mock_cmd:
            mock_cmd.return_value = {"docker_command": "docker run ..."}
            res = get_worker_command("w1", db, user, req)
            mock_cmd.assert_called_once_with(db, "w1", "u1", "api.fireaway.test")
            assert res == {"docker_command": "docker run ..."}

    def test_reset_worker_key(self):
        db = MagicMock()
        user = MagicMock(id="u1")
        req = MagicMock()
        req.headers.get.return_value = "api.fireaway.test"

        with patch.object(workers_route.worker_service, "reset_worker_key") as mock_reset:
            mock_reset.return_value = {"registration_key": "REG-NEW"}
            res = reset_worker_key("w1", db, user, req)
            mock_reset.assert_called_once_with(db, "w1", "u1", "api.fireaway.test")
            assert res == {"registration_key": "REG-NEW"}

    def test_get_compute_distribution(self):
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.group_by.return_value.all.return_value = [
            ("active", 3),
            ("busy", 2),
            ("quarantined", 1),
            ("offline", 4),
        ]
        db.query.return_value = q

        res = get_compute_distribution(db)
        assert isinstance(res, ComputeDistrubutionRatio)
        assert res.active == 3
        assert res.busy == 2
        assert res.quarantined == 1
        assert res.offline == 4
        assert res.total == 10

    def test_generate_worker_enrollment_key(self):
        user = MagicMock(id="usr-77")
        req = MagicMock()
        req.headers.get.return_value = "localhost:8000"
        body = WorkerEnrollmentKeyRequest(label="Lab Node", gpu_name="RTX 4090")

        with patch.object(workers_route.worker_service, "generate_worker_key") as mock_gen:
            mock_gen.return_value = {
                "registration_key": "REG-ABC",
                "expires_in_seconds": 86400,
                "docker_command": "docker run ...",
            }
            res = generate_worker_enrollment_key(body, user, req)
            mock_gen.assert_called_once_with(
                "usr-77",
                label="Lab Node",
                gpu_name="RTX 4090",
                request_host="localhost:8000",
            )
            assert res["registration_key"] == "REG-ABC"

    def test_register_worker(self):
        db = MagicMock()
        body = WorkerRegisterRequest(
            registration_key="REG-12345678",
            label="Home Rig",
            gpu_name="RTX 3080",
            vram_mb=10240,
            driver_version="550.54",
            cuda_capable=True,
        )

        with patch.object(workers_route.worker_service, "register_worker_node") as mock_reg:
            mock_reg.return_value = {
                "access_token": "mock.jwt.token",
                "token_type": "bearer",
                "worker_id": "w-1",
            }
            res = register_worker(body, db)
            mock_reg.assert_called_once_with(db, body)
            assert res["worker_id"] == "w-1"


class TestWebSocketWorkerEndpoint:
    @pytest.mark.asyncio
    async def test_websocket_missing_token_closes(self):
        ws = AsyncMock()
        ws.headers = {}
        db = MagicMock()
        await websocket_worker_endpoint(ws, token=None, db=db)
        ws.close.assert_awaited_once_with(code=status.WS_1008_POLICY_VIOLATION)

    @pytest.mark.asyncio
    async def test_websocket_bearer_header_and_token_validation_failure(self):
        ws = AsyncMock()
        ws.headers = {"Authorization": "Bearer bad-token"}
        db = MagicMock()

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            side_effect=HTTPException(status_code=401),
        ), patch(
            "app.backend.src.routes.workers.reject_worker_credentials"
        ) as mock_reject:
            await websocket_worker_endpoint(ws, token=None, db=db)
            mock_reject.assert_awaited_once_with(ws)

    @pytest.mark.asyncio
    async def test_websocket_worker_not_found_or_rejected_status(self):
        ws = AsyncMock()
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch(
            "app.backend.src.routes.workers.reject_worker_credentials"
        ) as mock_reject:
            await websocket_worker_endpoint(ws, token="valid", db=db)
            mock_reject.assert_awaited_once_with(ws)

        ws.reset_mock()
        mock_node = MagicMock(status="rejected")
        db.query.return_value.filter.return_value.first.return_value = mock_node

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch(
            "app.backend.src.routes.workers.reject_worker_credentials"
        ) as mock_reject:
            await websocket_worker_endpoint(ws, token="valid", db=db)
            mock_reject.assert_awaited_once_with(ws)

    @pytest.mark.asyncio
    async def test_websocket_deactivated_node_closes(self):
        ws = AsyncMock()
        db = MagicMock()
        node = MagicMock(status="deactivated")
        db.query.return_value.filter.return_value.first.return_value = node

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ):
            await websocket_worker_endpoint(ws, token="valid", db=db)
            ws.close.assert_awaited_once_with(code=status.WS_1008_POLICY_VIOLATION)

    @pytest.mark.asyncio
    async def test_websocket_quarantined_still_active_and_expired(self):
        ws = AsyncMock()
        db = MagicMock()
        future_time = datetime.now(timezone.utc) + timedelta(minutes=10)
        node = MagicMock(status="quarantined", quarantine_until=future_time.replace(tzinfo=None))
        db.query.return_value.filter.return_value.first.return_value = node

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ):
            await websocket_worker_endpoint(ws, token="valid", db=db)
            ws.close.assert_awaited_once_with(code=status.WS_1008_POLICY_VIOLATION)

        ws.reset_mock()
        past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        node = MagicMock(status="quarantined", quarantine_until=past_time)
        db.query.return_value.filter.return_value.first.return_value = node
        ws.receive_text.side_effect = WebSocketDisconnect()

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            await websocket_worker_endpoint(ws, token="valid", db=db)
            assert node.status == "offline"
            assert node.quarantine_until is None

    @pytest.mark.asyncio
    async def test_websocket_message_loop_ping_pong_progress_result_errors(self):
        ws = AsyncMock()
        db = MagicMock()
        node = MagicMock(status="active", consecutive_failures=0)
        db.query.return_value.filter.return_value.first.return_value = node

        loop = asyncio.get_running_loop()
        sim_future = loop.create_future()
        err_future = loop.create_future()
        workers_route.pending_results["job-sim"] = sim_future
        workers_route.pending_results["job-err"] = err_future
        workers_route.job_progress_keys["job-p"] = "prog-key"

        messages = [
            json.dumps({"type": "ping"}),
            json.dumps({"type": "pong"}),
            json.dumps({"type": "progress", "job_id": "job-p", "stage": "render", "message": "done 30%"}),
            json.dumps({"type": "simulation_result", "job_id": "job-sim", "payload": {"result": 42}}),
            json.dumps({"type": "simulation_error", "job_id": "job-other", "error_kind": "data_source"}),
            json.dumps({"type": "simulation_error", "job_id": "job-err", "error": "CUDA out of memory"}),
            WebSocketDisconnect(),
        ]

        async def mock_receive():
            if not messages:
                raise WebSocketDisconnect()
            item = messages.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

        ws.receive_text = mock_receive

        def mock_refresh(target):
            target.status = "busy"

        db.refresh.side_effect = mock_refresh

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch(
            "app.backend.src.routes.workers.set_sim_progress"
        ) as mock_set_prog, patch.object(
            workers_route.worker_service, "valkey_client"
        ) as mock_valkey:
            await websocket_worker_endpoint(ws, token="valid", db=db)

            ws.send_text.assert_any_await(json.dumps({"type": "pong"}))
            mock_set_prog.assert_called_with("prog-key", "render", "done 30%")
            assert sim_future.done()
            assert sim_future.result() == {"result": 42}
            assert err_future.done()
            assert err_future.result() is None
            assert node.consecutive_failures == 1
            assert node.status == "quarantined"

    @pytest.mark.asyncio
    async def test_websocket_simulation_result_already_active_and_no_future(self):
        ws = AsyncMock()
        db = MagicMock()
        node = MagicMock(status="active")
        db.query.return_value.filter.return_value.first.return_value = node

        messages = [
            json.dumps({"type": "simulation_result", "job_id": "job-no-fut", "payload": {}}),
            WebSocketDisconnect(),
        ]

        async def mock_receive():
            if not messages:
                raise WebSocketDisconnect()
            item = messages.pop(0)
            if isinstance(item, Exception):
                raise item
            return item

        ws.receive_text = mock_receive

        def mock_refresh(target):
            target.status = "active"

        db.refresh.side_effect = mock_refresh

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch.object(workers_route.worker_service, "valkey_client"):
            await websocket_worker_endpoint(ws, token="valid", db=db)
            assert node.status == "offline"

    @pytest.mark.asyncio
    async def test_websocket_timeout_sends_ping_and_disconnects_on_ping_failure(self):
        ws = AsyncMock()
        db = MagicMock()
        node = MagicMock(status="active")
        db.query.return_value.filter.return_value.first.return_value = node

        call_count = 0

        async def mock_receive():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise asyncio.TimeoutError()
            raise WebSocketDisconnect()

        ws.receive_text = mock_receive
        ws.send_text.return_value = None

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch.object(workers_route.worker_service, "valkey_client"):
            await websocket_worker_endpoint(ws, token="valid", db=db)
            ws.send_text.assert_any_await(json.dumps({"type": "ping"}))

        ws.reset_mock()
        call_count = 0

        async def mock_receive_timeout_break():
            raise asyncio.TimeoutError()

        ws.receive_text = mock_receive_timeout_break
        ws.send_text.side_effect = RuntimeError("Broken pipe")

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch.object(workers_route.worker_service, "valkey_client"):
            await websocket_worker_endpoint(ws, token="valid", db=db)
            ws.send_text.assert_any_await(json.dumps({"type": "ping"}))

    @pytest.mark.asyncio
    async def test_websocket_cleanup_db_failure_branch(self):
        ws = AsyncMock()
        ws.receive_text.side_effect = WebSocketDisconnect()
        db = MagicMock()
        node = MagicMock(status="active")

        # First query call succeeds on connect; second query call raises on disconnect cleanup
        q_init = MagicMock()
        q_init.filter.return_value.first.return_value = node

        def query_side_effect(model):
            if query_side_effect.calls == 0:
                query_side_effect.calls += 1
                return q_init
            raise RuntimeError("Database offline during cleanup")

        query_side_effect.calls = 0
        db.query.side_effect = query_side_effect

        with patch(
            "app.backend.src.routes.workers.verify_worker_token",
            new_callable=AsyncMock,
            return_value="w1",
        ), patch.object(workers_route.worker_service, "valkey_client"):
            await websocket_worker_endpoint(ws, token="valid", db=db)


class TestHasActiveVolunteerWorkers:
    def test_has_active_workers_scard_logic(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            mock_valkey.scard.return_value = 1
            workers_route.active_worker_connections["w1"] = MagicMock()
            assert has_active_volunteer_workers() is True

            mock_valkey.scard.return_value = 0
            assert has_active_volunteer_workers() is False

    def test_has_active_workers_exception_fallback(self):
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            mock_valkey.scard.side_effect = RuntimeError("Redis down")
            workers_route.active_worker_connections["w1"] = MagicMock()
            assert has_active_volunteer_workers() is True

            workers_route.active_worker_connections.clear()
            assert has_active_volunteer_workers() is False


class TestDispatchSimulationTask:
    @pytest.mark.asyncio
    async def test_dispatch_simulation_task_session_local_branch(self):
        mock_session_inst = MagicMock()
        mock_ctx = MagicMock()
        mock_ctx.__enter__.return_value = mock_session_inst
        mock_ctx.__exit__.return_value = None

        with patch("app.backend.db.SessionLocal", return_value=mock_ctx), patch(
            "app.backend.src.routes.workers.dispatch_simulation_task",
            new_callable=AsyncMock,
        ) as mock_dispatch:
            mock_dispatch.return_value = {"dispatched_to": "cloud_fallback"}
            res = await dispatch_simulation_task({"job_id": "j1"}, db=None, progress_key="pk")
            mock_dispatch.assert_awaited_once_with({"job_id": "j1"}, db=mock_session_inst, progress_key="pk")
            assert res == {"dispatched_to": "cloud_fallback"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_no_idle_worker(self):
        db = MagicMock()
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = None
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "j1"}, db=db, progress_key="pk")
            assert res == {"status": "cloud"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_worker_not_in_active_connections(self):
        db = MagicMock()
        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = b"worker-bytes-id"
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "j1"}, db=db, progress_key="pk")
            mock_valkey.srem.assert_called_with("worker:pool:idle", "worker-bytes-id")
            assert res == {"status": "cloud"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_node_not_active_in_db(self):
        db = MagicMock()
        ws = AsyncMock()
        workers_route.active_worker_connections["w1"] = ws
        node = MagicMock(status="offline")
        db.query.return_value.filter.return_value.first.return_value = node

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = "w1"
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "j1"}, db=db, progress_key="pk")
            mock_valkey.srem.assert_called_with("worker:pool:busy", "w1")
            assert res == {"status": "cloud"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_task_success_result(self):
        db = MagicMock()
        ws = AsyncMock()
        workers_route.active_worker_connections["w1"] = ws
        node = MagicMock(status="active", gpu_name="RTX 4090")
        db.query.return_value.filter.return_value.first.return_value = node

        async def send_and_resolve(msg):
            parsed = json.loads(msg)
            job_id = parsed["payload"]["job_id"]
            await asyncio.sleep(0.01)
            workers_route.pending_results[job_id].set_result({"burned_cells": 100})

        ws.send_text = send_and_resolve

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            mock_valkey.spop.return_value = "w1"
            res = await dispatch_simulation_task({"job_id": "job-ok"}, db=db, progress_key="pk")
            assert res == {"burned_cells": 100}
            assert node.status == "busy"
            mock_valkey.delete.assert_called_with("sim:progress:pk")

    @pytest.mark.asyncio
    async def test_dispatch_simulation_task_success_without_progress_key(self):
        db = MagicMock()
        ws = AsyncMock()
        workers_route.active_worker_connections["w1"] = ws
        node = MagicMock(status="active", gpu_name="RTX 4090")
        db.query.return_value.filter.return_value.first.return_value = node

        async def send_and_resolve(msg):
            parsed = json.loads(msg)
            job_id = parsed.get("payload", {}).get("job_id", "sim_job")
            await asyncio.sleep(0.01)
            workers_route.pending_results[job_id].set_result({"burned_cells": 50})

        ws.send_text = send_and_resolve

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey:
            mock_valkey.spop.return_value = "w1"
            res = await dispatch_simulation_task({"job_id": "sim_job"}, db=db, progress_key=None)
            assert res == {"burned_cells": 50}
            mock_valkey.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_simulation_task_worker_reports_none_error(self):
        db = MagicMock()
        ws = AsyncMock()
        workers_route.active_worker_connections["w1"] = ws
        node = MagicMock(status="active", gpu_name="RTX 4090")
        db.query.return_value.filter.return_value.first.return_value = node

        async def send_and_fail(msg):
            parsed = json.loads(msg)
            job_id = parsed["payload"]["job_id"]
            await asyncio.sleep(0.01)
            workers_route.pending_results[job_id].set_result(None)

        ws.send_text = send_and_fail

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = "w1"
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "job-none"}, db=db, progress_key="pk")
            assert res == {"status": "cloud"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_task_worker_disconnects_mid_simulation(self):
        db = MagicMock()
        ws = AsyncMock()
        workers_route.active_worker_connections["w1"] = ws
        node = MagicMock(status="active", gpu_name="RTX 4090")
        db.query.return_value.filter.return_value.first.return_value = node

        async def send_and_drop(msg):
            workers_route.active_worker_connections.pop("w1", None)

        ws.send_text = send_and_drop

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = "w1"
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "job-drop"}, db=db, progress_key="pk")
            assert res == {"status": "cloud"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_task_timeout_and_quarantine(self, monkeypatch):
        monkeypatch.setattr(workers_route, "JOB_TIMEOUT_SECONDS", 0.05)
        db = MagicMock()
        ws = AsyncMock()
        workers_route.active_worker_connections["w1"] = ws
        node = MagicMock(status="active", consecutive_failures=0, gpu_name="RTX 4090")
        db.query.return_value.filter.return_value.first.return_value = node

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = "w1"
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "job-timeout"}, db=db, progress_key="pk")
            assert node.status == "quarantined"
            assert node.consecutive_failures == 1
            assert res == {"status": "cloud"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_send_exception_recovery(self):
        db = MagicMock()
        ws = AsyncMock()
        ws.send_text.side_effect = RuntimeError("Network socket down")
        workers_route.active_worker_connections["w1"] = ws
        node = MagicMock(status="active", gpu_name="RTX 4090")

        def mock_refresh(target):
            target.status = "busy"

        db.refresh.side_effect = mock_refresh
        db.query.return_value.filter.return_value.first.return_value = node

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = "w1"
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "job-err"}, db=db, progress_key="pk")
            assert node.status == "active"
            mock_valkey.sadd.assert_called_with("worker:pool:idle", "w1")
            assert res == {"status": "cloud"}

    @pytest.mark.asyncio
    async def test_dispatch_simulation_send_exception_when_refresh_fails(self):
        db = MagicMock()
        ws = AsyncMock()
        ws.send_text.side_effect = RuntimeError("Socket failed")
        workers_route.active_worker_connections["w1"] = ws
        db.refresh.side_effect = RuntimeError("DB refresh broken")

        with patch.object(workers_route.worker_service, "valkey_client") as mock_valkey, patch(
            "app.backend.src.routes.workers.cloud_fallback"
        ) as mock_cloud:
            mock_valkey.spop.return_value = "w1"
            mock_cloud.return_value = {"status": "cloud"}
            res = await dispatch_simulation_task({"job_id": "job-db-broken"}, db=db, progress_key=None)
            assert res == {"status": "cloud"}