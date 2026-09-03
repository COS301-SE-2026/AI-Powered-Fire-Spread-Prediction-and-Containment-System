from datetime import datetime, timezone

import pytest
from geoalchemy2.elements import WKTElement

from conftest import make_report, make_user
from app.backend.src.enums.report_status import ReportStatus
from app.backend.src.models.reported_fires import FireReports

### GET /api/users/reported-fires ###


# test if nothing in db then endpoint returns HTTP 200 OK
# smoke test and empty-case test
def test_get_report_empty(client):
    response = client.get("/api/users/reported-fires")

    assert (
        response.status_code == 200
    ), "Expect 200 OK when DB is empty, returned {response.status_code}"

    assert (
        response.json() == []
    ), "Expect empty list when DB is empty, returned something in the list"


# endpoint exsistance test
# test if the report is in db then must appear in GET response
def test_get_reports(client, db):
    report = make_report(db)
    response = client.get("/api/users/reported-fires")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list), "must return list"
    assert len(data) >= 1, "must return atleast 1 report"

    refnums = []
    for r in response.json():
        refnums.append(r["reference_number"])
    assert report.reference_number in refnums, " report not found in get response"


# test if the shape of the get is correct
def test_get_report_shape(client, db):
    make_report(db)
    response = client.get("/api/users/reported-fires")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    item = data[0]
    expected_keys = {
        "id",
        "reference_number",
        "lat",
        "lng",
        "location_text",
        "status",
        "boundary_radius",
        "size",
        "submitted_at",
        "reporter_name",
        "verification_notes",
    }
    assert (
        set(item.keys()) == expected_keys
    ), "wrong shape: {set(item.keys())} should be: {expected_keys}"


# happy path tests
# test if one anonymous report exsists and if all the values is correct
def test_get_anonymous(client, db):
    report = make_report(
        db,
        lat=-25.7479,
        lng=28.2293,
        status=ReportStatus.pending,
        status_index=1,
    )
    response = client.get("/api/users/reported-fires")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

    item = None
    for r in data:
        if r["reference_number"] == report.reference_number:
            item = r
            break
    assert item is not None, "report not found in respons"

    assert item["id"] == report.id, "Expected {report.id}, got {item['id']}"
    assert (
        item["location_text"] == report.location_text
    ), "Expected {report.location_text}, got {item['location_text']}"
    assert (
        item["status"] == ReportStatus.pending.value
    ), "Expected {report.status}, got {item['status']}"
    assert item["boundary_radius"] == pytest.approx(
        float(report.boundary_radius)
    ), "Expected {report.boundary_radius}, got {item['boundary_radius']}"
    assert item["lat"] == pytest.approx(
        -25.7479, abs=1e-4
    ), "Expected lat possible swapped with lng"
    assert item["lng"] == pytest.approx(
        28.2293, abs=1e-4
    ), "Expected lng possible swapped with lat"
    assert (
        item["reporter_name"] == "Anonymous"
    ), "Expected {report.reporter_name}, got {item['reporter_name']}"


# test if the reporter name comes back as the actual full name
def test_get_reporter(client, db):
    user = make_user(db, full_name="Piet Pompies", role="user")
    report = make_report(db, user=user)
    response = client.get("/api/users/reported-fires")

    assert response.status_code == 200
    data = response.json()

    item = None
    for r in data:
        if r["reference_number"] == report.reference_number:
            item = r
            break
    assert item is not None, "report not found in respons"

    assert (
        item["reporter_name"] == "Piet Pompies"
    ), "Expected Piet Pompies, got {item['reporter_name']}"


# test if 3 reports exist then 3 needs to come back exactly as they are
def test_get_multiple_reports(client, db):
    reports = []
    for _ in range(3):
        reports.append(make_report(db))

    response = client.get("/api/users/reported-fires")

    assert response.status_code == 200

    refnums = []
    for r in response.json():
        refnums.append(r["reference_number"])

    for report in reports:
        count = refnums.count(report.reference_number)
        assert count == 1, "Expected {report.reference_number} to appear 1, got {count}"


### POST /api/users/reported-fires ###

PAYLOAD = {
    "lat": -25.7479,
    "lng": 28.2293,
    "location_text": "Hatfield, Pretoria",
    "image_url": "https://example.com/fire.jpg",
    "boundary_radius": 0.2,
}


# test if post endpoint exist and returns a valid response
def test_post_exist(client):
    response = client.post("/api/users/reported-fires", json=PAYLOAD)

    assert (
        response.status_code == 200
    ), "Expect success status, returned {response.status_code}: {response.text}"
    body = response.json()
    assert "id" in body, "shoulf contain id in body"
    assert "reference_number" in body, "should contain reference number in body"


# test if shape of post is correct
def test_post_shape(client):
    response = client.post("/api/users/reported-fires", json=PAYLOAD)

    assert response.status_code == 200
    item = response.json()

    expected_keys = {
        "id",
        "reference_number",
        "lat",
        "lng",
        "location_text",
        "description",
        "image_url",
        "status",
        "boundary_radius",
        "size",
        "submitted_at",
        "reporter_name",
        "priority",
        "verification_notes",
        "system_verified",
    }

    assert (
        set(item.keys()) == expected_keys
    ), "wrong shape: {set(item.keys())} should be: {expected_keys}"


# test that payload is valid and response values are correct
def test_post_happy_path(client, db):
    response = client.post("/api/users/reported-fires", json=PAYLOAD)

    assert response.status_code == 200
    body = response.json()

    assert (
        body["location_text"] == PAYLOAD["location_text"]
    ), "Expected {PAYLOAD['location_text']}, got {body['location_text']}"
    assert (
        body["status"] == ReportStatus.pending.value
    ), "Expected pending, got {body['status']}"
    assert body["lat"] == pytest.approx(
        PAYLOAD["lat"], abs=1e-4
    ), "lat possibly swapped with lng, got {body['lat']}"
    assert body["lng"] == pytest.approx(
        PAYLOAD["lng"], abs=1e-4
    ), "lat possibly swapped with lat, got {body['lng']}"
    assert (
        body["reporter_name"] == "Anonymous"
    ), "Expected Anonymous, got {body['reporter_name']}"

    row = db.query(FireReports).filter(FireReports.id == body["id"]).first()
    assert row is not None, "Report not found in db after POST"
    assert row.status == ReportStatus.pending


# #test if specific user exists and responds correctly
# def test_post_user(client, db):
#     user = make_user(db, full_name="Piet Pompies")

#     response = client.post(f"/api/users/reported-fires?user_id={user.id}",json=PAYLOAD)

#     assert response.status_code == 200
#     body = response.json()

#     assert body["reporter_name"] == "Piet Pompies", "Expected Piet Pompies, got {body['reporter_name']}"


# test if post has missing field it has to send 422 back
def test_post_missing_lat(client):
    newpayload = {**PAYLOAD}
    del newpayload["lat"]

    response = client.post("/api/users/reported-fires", json=newpayload)
    assert response.status_code == 422, "Expected 422, got {response.status_code}"


# test if payload type is valid
def test_post_invalid_type(client):
    newpayload = {**PAYLOAD, "lat": "string"}

    response = client.post("/api/users/reported-fires", json=newpayload)
    assert response.status_code == 422, "Expected 422, got {response.status_code}"


def test_not_allowed(client):
    response = client.delete("/api/users/reported-fires")
    assert (
        response.status_code == 405
    ), "Expected 405 method NOt ALlowed, got {response.status_code}"


def test_post_boundary_radius_zero(client):
    newpayload = {**PAYLOAD, "boundary_radius": 0}
    response = client.post("/api/users/reported-fires", json=newpayload)
    assert (
        response.status_code == 422
    ), "Expected 422 for boundary_radius of 0, got {response.status_code}"
