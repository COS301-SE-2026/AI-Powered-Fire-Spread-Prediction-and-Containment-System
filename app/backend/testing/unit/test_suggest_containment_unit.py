import math
from unittest.mock import patch
import numpy as np
import pytest

from ai.schema import UNBURNED
from ai.suggest_containment import (
    ContainmentSuggestion,
    compute_arrival_ticks,
    _standoff_mask,
    _frontier_cells,
    line_length_m,
    _local_gradient_angle,
    _grid_to_lonlat,
    _make_candidate_segment,
    _rasterize_segment,
    _score_candidate,
    suggest_containment_line,
    MIN_LINE_LENGTH_M,
    MAX_LINE_LENGTH_M,
)


class TestSuggestContainmentHelpers:
    def test_containment_suggestion_dataclass(self):
        item = ContainmentSuggestion(
            wkt="LINESTRING(0 0, 1 1)",
            length_m=100.0,
            build_time_min=10.0,
            arrival_at_line_min=25.0,
            margin_min=15.0,
            shielded_cell_score=1.5,
        )
        assert item.length_m == 100.0
        assert item.margin_min == 15.0

    def test_compute_arrival_ticks(self):
        h, w = 3, 3
        step0 = np.full((h, w), UNBURNED, dtype=np.int8)
        step1 = np.full((h, w), UNBURNED, dtype=np.int8)
        step1[1, 1] = 1
        step2 = np.full((h, w), UNBURNED, dtype=np.int8)
        step2[1, 1] = 2
        step2[1, 2] = 1

        history = [step0, step1, step2]
        arrival = compute_arrival_ticks(history)

        assert arrival.shape == (h, w)
        assert arrival[1, 1] == 1
        assert arrival[1, 2] == 2
        assert arrival[0, 0] == -1

    def test_standoff_mask_zero_or_negative(self):
        mask = np.array([[True, False], [False, False]], dtype=bool)
        out_zero = _standoff_mask(mask, standoff_cells=0)
        assert np.array_equal(out_zero, mask)
        assert out_zero is not mask

        out_neg = _standoff_mask(mask, standoff_cells=-1)
        assert np.array_equal(out_neg, mask)

    def test_standoff_mask_positive(self):
        mask = np.zeros((5, 5), dtype=bool)
        mask[2, 2] = True
        dilated = _standoff_mask(mask, standoff_cells=1)
        assert dilated[1:4, 1:4].all()
        assert not dilated[0, 0]

    def test_frontier_cells(self):
        arrival = np.full((5, 5), -1, dtype=np.int32)
        arrival[2, 2] = 1
        cells = _frontier_cells(arrival)
        assert (2, 2) in cells

    def test_line_length_m_clipping(self):
        arr_small = np.full((10, 10), -1, dtype=np.int32)
        arr_small[5, 5] = 0
        len_small = line_length_m(arr_small, cell_size_m=10.0)
        assert len_small == pytest.approx(MIN_LINE_LENGTH_M)

        arr_large = np.zeros((200, 200), dtype=np.int32)
        len_large = line_length_m(arr_large, cell_size_m=100.0)
        assert len_large == pytest.approx(MAX_LINE_LENGTH_M)

    def test_local_gradient_angle_all_nan(self):
        arrival = np.full((10, 10), -1, dtype=np.int32)
        assert _local_gradient_angle(arrival, 5, 5) == 0.0

    def test_local_gradient_angle_zero_gradient(self):
        arrival = np.full((10, 10), 5, dtype=np.int32)
        assert _local_gradient_angle(arrival, 5, 5) == 0.0

    def test_local_gradient_angle_valid_gradient(self):
        arrival = np.full((10, 10), -1, dtype=np.int32)
        for r in range(10):
            for c in range(10):
                arrival[r, c] = r + c
        angle = _local_gradient_angle(arrival, 5, 5)
        assert not math.isnan(angle)
        assert angle != 0.0

    def test_grid_to_lonlat(self):
        bounds = (10.0, -30.0, 20.0, -20.0)
        H, W = 100, 100
        lon, lat = _grid_to_lonlat(0, 0, H, W, bounds)
        assert lon == pytest.approx(10.0)
        assert lat == pytest.approx(-20.0)

        lon_br, lat_br = _grid_to_lonlat(100, 100, H, W, bounds)
        assert lon_br == pytest.approx(20.0)
        assert lat_br == pytest.approx(-30.0)

    def test_make_candidate_segment(self):
        p0, p1 = _make_candidate_segment(row=10, col=10, angle_rad=0.0, half_len_cells=5.0)
        assert p0[0] == pytest.approx(5.0)
        assert p0[1] == pytest.approx(10.0)
        assert p1[0] == pytest.approx(15.0)
        assert p1[1] == pytest.approx(10.0)

    def test_rasterize_segment(self):
        H, W = 10, 10
        cells = _rasterize_segment((1.0, 1.0), (3.0, 3.0), H, W)
        assert (1, 1) in cells
        assert (2, 2) in cells
        assert (3, 3) in cells

        out_cells = _rasterize_segment((-10.0, -10.0), (-5.0, -5.0), H, W)
        assert out_cells == []

    def test_score_candidate(self):
        H, W = 20, 20
        arrival = np.full((H, W), -1, dtype=np.int32)
        arrival[15:, :] = 1
        cells = [(10, 10), (10, 11), (10, 12)]
        angle_rad = math.pi / 2  # points downward in row space

        score = _score_candidate(cells, angle_rad, arrival, lookahead_pad_cells=6)
        assert score > 0


class TestSuggestContainmentLineFlow:
    @patch("ai.suggest_containment.bbox_from_fire")
    @patch("ai.suggest_containment.build_boundary_ignition_mask")
    def test_suggest_containment_line_success(
        self, mock_build_mask, mock_bbox
    ):
        mock_bbox.return_value = (18.4, -34.0, 18.5, -33.9)
        H, W = 50, 50
        mock_build_mask.return_value = np.zeros((H, W), dtype=bool)

        history = []
        for t in range(10):
            grid = np.full((H, W), UNBURNED, dtype=np.int8)
            if t > 0:
                grid[15:15 + t * 2, 20:30] = 1
            history.append(grid)

        suggestions = suggest_containment_line(
            history=history,
            fire_lat=-33.95,
            fire_lng=18.45,
            boundary_radius_m=1000.0,
            cell_size_m=30.0,
            n_steps=10,
            top_n=1,
        )

        assert isinstance(suggestions, list)
        if suggestions:
            top = suggestions[0]
            assert top.wkt.startswith("LINESTRING")
            assert top.length_m > 0
            assert top.build_time_min > 0
            assert top.arrival_at_line_min > 0
            assert top.margin_min > 0
            assert top.shielded_cell_score >= 0

    @patch("ai.suggest_containment.bbox_from_fire")
    @patch("ai.suggest_containment.build_boundary_ignition_mask")
    def test_suggest_containment_line_skips_excluded_cells(
        self, mock_build_mask, mock_bbox
    ):
        mock_bbox.return_value = (18.4, -34.0, 18.5, -33.9)
        H, W = 20, 20
        mock_build_mask.return_value = np.ones((H, W), dtype=bool)

        step = np.full((H, W), UNBURNED, dtype=np.int8)
        step[10, 10] = 1
        history = [step, step]

        suggestions = suggest_containment_line(
            history=history,
            fire_lat=-33.95,
            fire_lng=18.45,
            boundary_radius_m=100.0,
            cell_size_m=30.0,
            n_steps=2,
            top_n=2,
        )
        assert suggestions == []

    @patch("ai.suggest_containment.bbox_from_fire")
    @patch("ai.suggest_containment.build_boundary_ignition_mask")
    @patch("ai.suggest_containment._make_candidate_segment")
    def test_suggest_containment_line_zero_length_skip(
        self, mock_make_seg, mock_build_mask, mock_bbox
    ):
        mock_bbox.return_value = (18.4, -34.0, 18.5, -33.9)
        H, W = 30, 30
        mock_build_mask.return_value = np.zeros((H, W), dtype=bool)

        mock_make_seg.return_value = ((5.0, 5.0), (5.0, 5.0))

        step0 = np.full((H, W), UNBURNED, dtype=np.int8)
        step1 = np.full((H, W), UNBURNED, dtype=np.int8)
        step1[10, 10] = 1
        history = [step0, step1]

        suggestions = suggest_containment_line(
            history=history,
            fire_lat=-33.95,
            fire_lng=18.45,
            boundary_radius_m=500.0,
            cell_size_m=30.0,
            n_steps=2,
            top_n=1,
        )
        assert suggestions == []

    @patch("ai.suggest_containment.bbox_from_fire")
    @patch("ai.suggest_containment.build_boundary_ignition_mask")
    @patch("ai.suggest_containment._rasterize_segment")
    def test_suggest_containment_line_no_arrivals_skip(
        self, mock_rasterize, mock_build_mask, mock_bbox
    ):
        mock_bbox.return_value = (18.4, -34.0, 18.5, -33.9)
        H, W = 30, 30
        mock_build_mask.return_value = np.zeros((H, W), dtype=bool)

        step0 = np.full((H, W), UNBURNED, dtype=np.int8)
        step1 = np.full((H, W), UNBURNED, dtype=np.int8)
        step1[10, 10] = 1
        history = [step0, step1]

        mock_rasterize.return_value = [(0, 0), (0, 1)]

        suggestions = suggest_containment_line(
            history=history,
            fire_lat=-33.95,
            fire_lng=18.45,
            boundary_radius_m=500.0,
            cell_size_m=30.0,
            n_steps=2,
            top_n=1,
        )
        assert suggestions == []

    @patch("ai.suggest_containment.bbox_from_fire")
    @patch("ai.suggest_containment.build_boundary_ignition_mask")
    @patch("ai.suggest_containment._rasterize_segment")
    def test_suggest_containment_line_negative_margin_skip(
        self, mock_rasterize, mock_build_mask, mock_bbox
    ):
        mock_bbox.return_value = (18.4, -34.0, 18.5, -33.9)
        H, W = 30, 30
        mock_build_mask.return_value = np.zeros((H, W), dtype=bool)

        step0 = np.full((H, W), UNBURNED, dtype=np.int8)
        step0[10, 10] = 1
        step1 = np.full((H, W), UNBURNED, dtype=np.int8)
        step1[10, 10] = 2
        history = [step0, step1]

        mock_rasterize.return_value = [(10, 10)]

        suggestions = suggest_containment_line(
            history=history,
            fire_lat=-33.95,
            fire_lng=18.45,
            boundary_radius_m=500.0,
            cell_size_m=30.0,
            n_steps=2,
            top_n=1,
        )
        assert suggestions == []

    @patch("ai.suggest_containment.bbox_from_fire")
    @patch("ai.suggest_containment.build_boundary_ignition_mask")
    @patch("ai.suggest_containment._score_candidate", return_value=0.0)
    @patch("ai.suggest_containment._rasterize_segment")
    def test_suggest_containment_line_zero_score_skip(
        self, mock_rasterize, mock_score, mock_build_mask, mock_bbox
    ):
        mock_bbox.return_value = (18.4, -34.0, 18.5, -33.9)
        H, W = 30, 30
        mock_build_mask.return_value = np.zeros((H, W), dtype=bool)

        step0 = np.full((H, W), UNBURNED, dtype=np.int8)
        step1 = np.full((H, W), UNBURNED, dtype=np.int8)
        step1[10, 10] = 1
        history = [step0] + [step1] * 10
        history[-1][10, 11] = 1

        mock_rasterize.return_value = [(10, 11)]

        suggestions = suggest_containment_line(
            history=history,
            fire_lat=-33.95,
            fire_lng=18.45,
            boundary_radius_m=500.0,
            cell_size_m=30.0,
            n_steps=11,
            top_n=1,
        )
        assert suggestions == []