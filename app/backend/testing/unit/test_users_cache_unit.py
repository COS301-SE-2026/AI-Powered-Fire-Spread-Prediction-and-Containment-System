import importlib
from unittest.mock import MagicMock
import pytest
import redis

from app.backend.src.services.users import cache


class TestUsersCache:
    def test_cache_init_success_default_env(self, monkeypatch):
        monkeypatch.delenv("VALKEY_HOST", raising=False)
        monkeypatch.delenv("VALKEY_PORT", raising=False)

        mock_redis_client = MagicMock()
        mock_redis_constructor = MagicMock(return_value=mock_redis_client)
        monkeypatch.setattr(redis, "Redis", mock_redis_constructor)

        reloaded = importlib.reload(cache)

        assert reloaded.VALKEY_HOST == "valkey"
        assert reloaded.VALKEY_PORT == 6379
        mock_redis_constructor.assert_called_once_with(
            host="valkey",
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
        mock_redis_client.ping.assert_called_once()
        assert reloaded.cache_client is mock_redis_client

    def test_cache_init_success_custom_env(self, monkeypatch):
        monkeypatch.setenv("VALKEY_HOST", "custom-valkey-host")
        monkeypatch.setenv("VALKEY_PORT", "6380")

        mock_redis_client = MagicMock()
        mock_redis_constructor = MagicMock(return_value=mock_redis_client)
        monkeypatch.setattr(redis, "Redis", mock_redis_constructor)

        reloaded = importlib.reload(cache)

        assert reloaded.VALKEY_HOST == "custom-valkey-host"
        assert reloaded.VALKEY_PORT == 6380
        mock_redis_constructor.assert_called_once_with(
            host="custom-valkey-host",
            port=6380,
            db=0,
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
        assert reloaded.cache_client is mock_redis_client

    def test_cache_init_connection_failure_sets_client_none(self, monkeypatch):
        mock_redis_client = MagicMock()
        mock_redis_client.ping.side_effect = redis.ConnectionError("Connection refused")
        monkeypatch.setattr(redis, "Redis", MagicMock(return_value=mock_redis_client))

        reloaded = importlib.reload(cache)

        assert reloaded.cache_client is None

    def test_cache_init_redis_constructor_exception_sets_client_none(self, monkeypatch):
        monkeypatch.setattr(
            redis,
            "Redis",
            MagicMock(side_effect=Exception("Failed to construct Redis client")),
        )

        reloaded = importlib.reload(cache)

        assert reloaded.cache_client is None