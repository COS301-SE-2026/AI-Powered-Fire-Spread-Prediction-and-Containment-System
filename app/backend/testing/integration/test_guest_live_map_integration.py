# import pytest
# from geoalchemy2.elements import WKTElement

# from enums.report_status import ReportStatus
# from models.reported_fires import FireReports


# # @pytest.mark.skip(reason="PostGIS not configured for testing yet.")
# def test_guest_fire_map_integration(client, db):
#     """Validate data retrieval for guest live map view"""

#     # mock record into test db
#     mock_fire = FireReports(
#         id="fr_01",
#         reference_number="FR-2026-100",
#         user_id="usr_01",
#         location_text="Place 1",
#         description="Fake fire",
#         image_url="image",
#         location_geom=WKTElement("POINT(28.2293 -25.7479)", srid=4326),
#         boundary_radius=2,
#         status=ReportStatus.verified,
#         status_index=2,
#     )

#     db.add(mock_fire)
#     db.commit()

#     response = client.get("api/guests/reported-fires")

#     assert (
#         response.status_code == 200
#     ), "Since it is public unautherised shouldn't be returned"

#     data = response.json()
#     assert isinstance(data, list), "Expect a list of fire reports"
#     assert len(data) >= 1, "At least one active fire"

#     # fake fire just created
#     guest_fire = next(
#         (item for item in data if item["reference_number"] == "FR-2026-100"), None
#     )
#     assert guest_fire is not None, "Failed to get the mock fire just created"

#     assert "user_id" not in guest_fire, "Sensitive data leaked to public"
