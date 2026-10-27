import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import pytest

from app.backend.src.ai.inspect_fire import inspect_fire_events, main


def _create_mock_fire_event(fire_id: str, ticks_count: int, min_lon=18.0, min_lat=-34.0, max_lon=19.0, max_lat=-33.0):
    return SimpleNamespace(
        fire_id=fire_id,
        ticks=list(range(ticks_count)),
        min_lon=min_lon,
        min_lat=min_lat,
        max_lon=max_lon,
        max_lat=max_lat,
    )


class TestInspectFireEvents:
    @patch("app.backend.src.ai.inspect_fire.build_fire_events")
    @patch("app.backend.src.ai.inspect_fire.cluster_fire_events")
    @patch("app.backend.src.ai.inspect_fire.load_detections")
    def test_inspect_fire_events_with_limit_and_truncation(
        self, mock_load, mock_cluster, mock_build, capsys
    ):
        mock_load.return_value = ["det1", "det2", "det3", "det4"]
        mock_cluster.return_value = [0, 0, 1, 1]

        # 3 usable fires (ticks >= 2), 1 excluded fire (ticks < 2)
        event_1 = _create_mock_fire_event("fire_1", ticks_count=5)
        event_2 = _create_mock_fire_event("fire_2", ticks_count=10)
        event_3 = _create_mock_fire_event("fire_3", ticks_count=3)
        event_ignored = _create_mock_fire_event("fire_ignored", ticks_count=1)

        mock_build.return_value = [event_1, event_2, event_3, event_ignored]

        # limit=2 ensures truncation branch (len(usable_fires) > limit) executes
        usable = inspect_fire_events("detections.csv", min_ticks=2, limit=2)

        assert len(usable) == 3
        # Should be sorted descending by number of ticks
        assert [e.fire_id for e in usable] == ["fire_2", "fire_1", "fire_3"]

        captured = capsys.readouterr().out
        assert "4 total detections loaded form detections.csv" in captured
        assert "4 distinct fires" in captured
        assert "3 fires that have more than 2 ticks" in captured
        assert "Fire ID = fire_2" in captured
        assert "Fire ID = fire_1" in captured
        assert "Fire ID = fire_3" not in captured
        assert "... (1 more not shown but you can use --limit to see more)" in captured

    @patch("app.backend.src.ai.inspect_fire.build_fire_events")
    @patch("app.backend.src.ai.inspect_fire.cluster_fire_events")
    @patch("app.backend.src.ai.inspect_fire.load_detections")
    def test_inspect_fire_events_limit_none(
        self, mock_load, mock_cluster, mock_build, capsys
    ):
        mock_load.return_value = ["det1", "det2"]
        mock_cluster.return_value = [0, 0]

        event = _create_mock_fire_event("fire_only", ticks_count=4)
        mock_build.return_value = [event]

        usable = inspect_fire_events("detections.csv", limit=None)

        assert len(usable) == 1
        captured = capsys.readouterr().out
        assert "Fire ID = fire_only" in captured
        assert "more not shown" not in captured


class TestInspectFireMain:
    @patch("app.backend.src.ai.inspect_fire.inspect_fire_events")
    def test_main_with_nonzero_limit(self, mock_inspect, monkeypatch):
        test_args = [
            "inspect_fire.py",
            "--csv", "test.csv",
            "--lat-col", "custom_lat",
            "--lon-col", "custom_lon",
            "--date-col", "custom_date",
            "--time-col", "custom_time",
            "--max-gap-km", "10.0",
            "--max-gap-days", "2.0",
            "--min-ticks", "4",
            "--limit", "15",
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        main()

        mock_inspect.assert_called_once_with(
            "test.csv",
            "custom_lat",
            "custom_lon",
            "custom_date",
            "custom_time",
            10.0,
            2.0,
            4,
            15,
        )

    @patch("app.backend.src.ai.inspect_fire.inspect_fire_events")
    def test_main_with_zero_limit_converts_to_none(self, mock_inspect, monkeypatch):
        test_args = [
            "inspect_fire.py",
            "--csv", "records.csv",
            "--limit", "0",
        ]
        monkeypatch.setattr(sys, "argv", test_args)

        main()

        mock_inspect.assert_called_once_with(
            "records.csv",
            "latitude",
            "longitude",
            "acq_date",
            "acq_time",
            5.0,
            4.0,
            2,
            None,
        )

    def test_main_module_execution_entrypoint(self, monkeypatch):
        test_args = ["inspect_fire.py", "--csv", "entry.csv"]
        monkeypatch.setattr(sys, "argv", test_args)

        for mod in ("ai.inspect_fire", "app.backend.src.ai.inspect_fire"):
            monkeypatch.delitem(sys.modules, mod, raising=False)

        mock_event = _create_mock_fire_event("fire_main", ticks_count=3)
        with patch("ai.build_ignition_dataset.load_detections", return_value=["det1", "det2"]), \
            patch("ai.build_ignition_dataset.cluster_fire_events", return_value=[0, 0]), \
            patch("ai.build_ignition_dataset.build_fire_events", return_value=[mock_event]):
            import runpy
            runpy.run_module("ai.inspect_fire", run_name="__main__")