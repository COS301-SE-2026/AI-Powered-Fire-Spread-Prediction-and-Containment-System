from types import SimpleNamespace

from app.backend.src.ai.simulation_api import cluster_fires_by_bbox_overlap


def make_fire(ref, lat, lng, boundary_radius=0.2):
    return SimpleNamespace(
        id=ref,
        reference_number=ref,
        lat=lat,
        lng=lng,
        boundary_radius=boundary_radius,
    )


def test_no_fires_returns_no_groups():
    assert cluster_fires_by_bbox_overlap([], n_steps=4) == []


def test_single_fire_is_its_own_group():
    fire = make_fire("F1", -25.7479, 28.2293)
    groups = cluster_fires_by_bbox_overlap([fire], n_steps=4)
    assert len(groups) == 1
    assert groups[0] == [fire]


def test_far_apart_fires_stay_separate():
    fire_a = make_fire("F1", -25.75, 28.20)
    fire_b = make_fire("F2", -25.75, 28.70)

    groups = cluster_fires_by_bbox_overlap([fire_a, fire_b], n_steps=4)

    assert len(groups) == 2
    assert {g[0].reference_number for g in groups} == {"F1", "F2"}


def test_nearby_fires_merge_into_one_group():
    fire_a = make_fire("F1", -25.7479, 28.2293)
    fire_b = make_fire("F2", -25.7485, 28.2299)

    groups = cluster_fires_by_bbox_overlap([fire_a, fire_b], n_steps=4)

    assert len(groups) == 1
    refs = {f.reference_number for f in groups[0]}
    assert refs == {"F1", "F2"}


def test_transitive_merging_across_a_chain():
    fire_a = make_fire("A", -25.7479, 28.2000)
    fire_b = make_fire("B", -25.7479, 28.2050)
    fire_c = make_fire("C", -25.7479, 28.2100)

    groups = cluster_fires_by_bbox_overlap([fire_a, fire_b, fire_c], n_steps=4)

    assert len(groups) == 1
    refs = {f.reference_number for f in groups[0]}
    assert refs == {"A", "B", "C"}


def test_mixed_clustered_and_isolated_fires():
    fire_a = make_fire("A", -25.7479, 28.2293)
    fire_b = make_fire("B", -25.7485, 28.2299)
    fire_c = make_fire("C", -26.5000, 29.5000)

    groups = cluster_fires_by_bbox_overlap([fire_a, fire_b, fire_c], n_steps=4)

    assert len(groups) == 2
    sizes = sorted(len(g) for g in groups)
    assert sizes == [1, 2]
