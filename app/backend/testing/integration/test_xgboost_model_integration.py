import numpy as np
import pytest
from app.backend.ml.training.synthetic_data import (
    SynthConfig,
    generate_synthetic_dataset,
    make_static,
    make_weather,
)
from app.backend.ml.training.train_ignition import group_split, train

from app.backend.src.ai import artifact_store
from app.backend.src.ai.ignition import IgnitionScorer
from app.backend.src.ai.schema import BURNED, BURNING, FEATURES, SCHEMA_VERSION, UNBURNED


# Shared fixture. (scope="module" -> Trains once per pytest run)
@pytest.fixture(scope="module")
def tiny_booster():
    """Train a lightweight XGBoost model reused accross test cases.

    Generate a small synthetic dataset and fits a booster model on CPU/GPU once per module execution session.

    Yields
    ------
        xgb.Booster
            A trained XGBoost booster instance ready for inference testing
    """
    X, y, fire_ids = generate_synthetic_dataset(
        SynthConfig(n_fires=6, n_ticks=10, H=32, W=32, seed=3)
    )
    X_train, y_train, X_va, y_va, _ = group_split(X, y, fire_ids)
    return train(X_train, y_train, X_va, y_va, device="cpu")  # Can change device="gpu"


# Synthetic data generator contract
@pytest.mark.slow
def test_synthetic_dataset_shape():
    """Verify generated synthetic data dimensions adhere to schema expectations.

    Ensures feature matrix X contains column lengths mathing `len(FEATURES)` and that all outputs maintain equal entry lengths.
    """
    X, y, fire_ids = generate_synthetic_dataset(
        SynthConfig(n_fires=3, n_ticks=8, H=32, W=32, seed=1)
    )
    assert X.shape[1] == len(FEATURES)
    assert len(X) == len(y) == len(fire_ids)


@pytest.mark.slow
def test_synthetic_dataset_labels():
    """Verify synthetic label properties for binary classification readiness.

    Ensures target labels strictly binary ({0, 1}) and positive classes exist as a realistic minority subset.
    """
    _, y, _ = generate_synthetic_dataset(
        SynthConfig(n_fires=3, n_ticks=8, H=32, W=32, seed=1)
    )
    assert set(np.unique(y)) <= {0, 1}
    assert 0 < y.mean() < 0.5, "positives should exist but as a minority"


@pytest.mark.slow
def test_synthetic_dataset_fire_ids():
    """fire_ids must contain exactly as many unique values as n_fires"""
    _, _, fire_ids = generate_synthetic_dataset(
        SynthConfig(n_fires=3, n_ticks=8, H=32, W=32, seed=1)
    )
    assert len(np.unique(fire_ids)) == 3


# Group split
@pytest.mark.slow
def test_group_split_sizes():
    """Train + validation rows must equal total rows"""
    X, y, fire_ids = generate_synthetic_dataset(
        SynthConfig(n_fires=5, n_ticks=5, H=24, W=24, seed=2)
    )
    X_train, _, X_va, _, _ = group_split(X, y, fire_ids, val_frac=0.4, seed=0)
    assert len(X_train) + len(X_va) == len(X)


@pytest.mark.slow
def test_group_split_no_leakage():
    """No fire event's rows should appear on both sides of the split"""
    X, y, fire_ids = generate_synthetic_dataset(
        SynthConfig(n_fires=5, n_ticks=5, H=24, W=24, seed=2)
    )
    _, _, _, _, val_fires = group_split(X, y, fire_ids, val_frac=0.4, seed=0)
    train_ids = fire_ids[~np.isin(fire_ids, val_fires)]
    assert not set(np.unique(train_ids)) & set(val_fires)


# Trained model behaviour
@pytest.mark.slow
def test_model_beats_chance(tiny_booster):
    """Validation PR-AUC must comfortably exceed 0.5"""
    assert (
        float(tiny_booster.best_score) > 0.5
    ), "val PR-AUC should beat positive base rate"


def test_model_physics_direction(tiny_booster, small_grids):
    """A cell adjacent to fire must score higher than the same cell with no fire"""
    scorer = IgnitionScorer(tiny_booster)
    weather, static, burn = small_grids(9, 9)

    no_fire = scorer.score_grid(weather, static, burn.copy())
    burn[4, 4] = BURNING
    with_fire = scorer.score_grid(weather, static, burn)

    assert (
        with_fire[4, 5] > no_fire[4, 5]
    ), "adjacent cell should score higher when fire present"
    assert (
        with_fire[4, 5] > with_fire[0, 0]
    ), "adjacent cell should score higher than a distant cell"


@pytest.mark.slow
def test_scorer_zeros_burning_cells(tiny_booster, small_grids):
    """Cells already BURNING must get p=0 (DCA owns their state)"""
    scorer = IgnitionScorer(tiny_booster)
    weather, static, burn = small_grids()
    burn[1, 1] = BURNING
    heat = scorer.score_grid(weather, static, burn)
    assert heat[1, 1] == pytest.approx(0.0)


@pytest.mark.slow
def test_scorer_output_shape_and_dtype(tiny_booster, small_grids):
    """score_grid must return float32 array matching burn_state shape"""
    scorer = IgnitionScorer(tiny_booster)
    weather, static, burn = small_grids()
    heat = scorer.score_grid(weather, static, burn)
    assert heat.shape == burn.shape
    assert heat.dtype == np.float32


# Artifact store
@pytest.mark.slow
def test_artifact_publish_and_list(tiny_booster, tmp_path, monkeypatch):
    """Two publishes should produce two distinct listed versions"""
    monkeypatch.setenv("FIRE_ARTIFACT_STORE", str(tmp_path))
    model_path = tmp_path / "m.json"
    tiny_booster.save_model(str(model_path))
    meta = {
        "schema_version": SCHEMA_VERSION,
        "features": FEATURES,
        "val_aucpr": float(tiny_booster.best_score),
    }
    v1 = artifact_store.publish("ignition", model_path, meta, promote=True)
    v2 = artifact_store.publish("ignition", model_path, meta, promote=False)
    assert artifact_store.list_versions("ignition") == sorted([v1, v2])


@pytest.mark.slow
def test_artifact_promote_updates_latest(tiny_booster, tmp_path, monkeypatch):
    """Promoting v2 should move LATEST from v1 tp v2"""
    monkeypatch.setenv("FIRE_ARTIFACT_STORE", str(tmp_path))
    model_path = tmp_path / "m.json"
    tiny_booster.save_model(str(model_path))
    meta = {
        "schema_version": SCHEMA_VERSION,
        "features": FEATURES,
        "val_aucpr": float(tiny_booster.best_score),
    }

    v1 = artifact_store.publish("ignition", model_path, meta, promote=True)
    v2 = artifact_store.publish("ignition", model_path, meta, promote=False)

    assert artifact_store.resolve("ignition", "LATEST").name == v1
    artifact_store.promote_version("ignition", v2)
    assert artifact_store.resolve("ignition", "LATEST").name == v2


@pytest.mark.slow
def test_artifact_load_roundtrip(tiny_booster, tmp_path, monkeypatch, small_grids):
    """A published model must load correctly and score a grid"""
    monkeypatch.setenv("FIRE_ARTIFACT_STORE", str(tmp_path))
    model_path = tmp_path / "m.json"
    tiny_booster.save_model(str(model_path))
    artifact_store.publish(
        "ignition",
        model_path,
        {
            "schema_version": SCHEMA_VERSION,
            "features": FEATURES,
            "val_aucpr": float(tiny_booster.best_score),
        },
        promote=True,
    )
    scorer = IgnitionScorer.load("LATEST")
    weather, static, burn = small_grids()
    assert scorer.score_grid(weather, static, burn).shape == (5, 5)


@pytest.mark.slow
def test_schema_guard_rejects_mismatch(tiny_booster, tmp_path, monkeypatch):
    """Loading a model whose schema does not match the code must raise RuntimeError"""
    monkeypatch.setenv("FIRE_ARTIFACT_STORE", str(tmp_path))
    model_path = tmp_path / "m.json"
    tiny_booster.save_model(str(model_path))
    artifact_store.publish(
        "ignition",
        model_path,
        {"schema_version": 999, "features": ["bogus"]},
        promote=True,
    )
    with pytest.raises(RuntimeError, match="Schema mismatch"):
        IgnitionScorer.load("LATEST")
