from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from app.backend.src.ai.simulation_api import simulate_fire_cluster, ClusterPrediction
import asyncio

def make_fire(ref, lat, lng, boundary_radius=0.2):
    return SimpleNamespace(
        id=ref,
        reference_number=ref,
        lat=lat,
        lng=lng,
        boundary_radius=boundary_radius,
    )

def make_worker_history(H=20, W=20, n_ticks=3):
    history =[]

    for t in range (n_ticks):
        grid = np.zeros((H, W), dtype= int)
        grid[H // 2, W // 2] = 1
        if t > 0:
            grid[H // 2, W // 2 + t] = 2
        history.append(grid.tolist())
    return history

@pytest.mark.anyio
async def test_simulate_fire_cluster_dispatches_and_parses_result():
    fire_a = make_fire("F1", -25.7479, 28.2293)
    fire_b = make_fire("F2", -25.7485, 28.2299)

    fake_history = make_worker_history()

    with patch(
        "app.backend.src.ai.simulation_api.get_cached_cluster_prediction",
        return_value=None,
    ), patch(
        "app.backend.src.ai.simulation_api.cache_cluster_prediction",
    ) as mock_cache_write, patch(
        "app.backend.src.ai.simulation_api.sqs"
    ) as mock_sqs, patch(
        "app.backend.src.ai.simulation_api.wait_for_result",
        new=AsyncMock(return_value={"history": fake_history}),
    ) as mock_wait:

        semaphore = asyncio.Semaphore(1)
        result = await simulate_fire_cluster(
            fires=[fire_a, fire_b],
            n_steps=4,
            semaphore=semaphore,
            containment_lines_by_fire={"F1": ["LINESTRING(28.22 -25.74, 28.23 -25.75)"]},
        )

    assert isinstance(result, ClusterPrediction)
    assert set(result.fire_refs) == {"F1", "F2"}
    assert result.grid_h > 0 and result.grid_w > 0
    assert len(result.history) == len(fake_history)

    # dispatched exactly one job to SQS, for the merged cluster
    mock_sqs.send_message.assert_called_once()
    sent_body = mock_sqs.send_message.call_args.kwargs["MessageBody"]
    assert '"fires"' in sent_body  # job used the plural, multi-fire field
    assert '"F1"' in sent_body and '"F2"' in sent_body

    # waited on the same job_id it dispatched
    dispatched_job_id = mock_wait.call_args.args[0]
    assert dispatched_job_id.startswith("cluster-")

    # result got cached after a successful run
    mock_cache_write.assert_called_once()


@pytest.mark.anyio
async def test_simulate_fire_cluster_returns_cached_result_without_dispatching():
    fire_a = make_fire("F1", -25.7479, 28.2293)
    fire_b = make_fire("F2", -25.7485, 28.2299)

    cached_payload = {
        "fire_refs": ["F1", "F2"],
        "lat": -25.748,
        "lng": 28.229,
        "history": [[0, 0, 0, 1]],
        "burned_cells": 1,
        "radius_m": 10.0,
        "truncated": False,
        "lat_extent_deg": 0.01,
        "lon_extent_deg": 0.01,
        "grid_h": 2,
        "grid_w": 2,
        "cell_size_m": 15.0,
    }

    with patch(
        "app.backend.src.ai.simulation_api.get_cached_cluster_prediction",
        return_value=cached_payload,
    ), patch("app.backend.src.ai.simulation_api.sqs") as mock_sqs, patch(
        "app.backend.src.ai.simulation_api.wait_for_result", new=AsyncMock()
    ) as mock_wait:

        semaphore = asyncio.Semaphore(1)
        result = await simulate_fire_cluster([fire_a, fire_b], 4, semaphore)

    assert isinstance(result, ClusterPrediction)
    assert result.fire_refs == ["F1", "F2"]
    mock_sqs.send_message.assert_not_called()
    mock_wait.assert_not_called()


@pytest.mark.anyio
async def test_simulate_fire_cluster_raises_504_on_timeout():
    from fastapi import HTTPException

    fire_a = make_fire("F1", -25.7479, 28.2293)
    fire_b = make_fire("F2", -25.7485, 28.2299)

    with patch(
        "app.backend.src.ai.simulation_api.get_cached_cluster_prediction",
        return_value=None,
    ), patch("app.backend.src.ai.simulation_api.sqs"), patch(
        "app.backend.src.ai.simulation_api.wait_for_result",
        new=AsyncMock(return_value=None),
    ):
        semaphore = asyncio.Semaphore(1)
        with pytest.raises(HTTPException) as exc_info:
            await simulate_fire_cluster([fire_a, fire_b], 4, semaphore)

    assert exc_info.value.status_code == 504