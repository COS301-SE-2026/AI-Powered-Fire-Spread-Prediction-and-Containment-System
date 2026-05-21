import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app 

client = TestClient(app)

MOCK_PUBLIC_FIRES = [
    {
        "incident_id": "FIRE-001",
        "latitude": -25.7479,
        "longitude": 28.2293,
        "severity_level": "HIGH",
        "containment_status": "UNCONTAINED"
    }
]

MOCK_ENVIRONMENT_DATA = {
    "temperature_celsius": 32,
    "wind_speed_kmh": 25,
    "wind_direction": "NE",
    "humidity_percentage": 15
}

class TestGuestLiveMapAPI:

    @patch("app.services.incident_service.get_active_public_fires")
    def test_fetch_public_fire_coordinates_unauthenticated(self, mock_get_fires):
        "Guests can see fire locations without logging in"
        mock_get_fires.return_value = MOCK_PUBLIC_FIRES

        response = client.get("/api/v1/incidents/public")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["incident_id"] == "FIRE-001"
        assert "latitude" in data[0]
        assert "longitude" in data[0]

    @patch("app.services.incident_service.get_active_public_fires")
    def test_public_endpoint_strips_tactical_data(self, mock_get_fires):
        "Endpoint should not give access to firefighter locations or simulation data"
        mock_get_fires.return_value = MOCK_PUBLIC_FIRES
        
        response = client.get("/api/v1/incidents/public")
        data = response.json()

        assert "assigned_units" not in data[0]
        assert "prediction_tensor_matrix" not in data[0]

    @patch("app.services.weather_service.get_current_environment_stats")
    def test_fetch_public_environment_widgets(self, mock_get_weather):
        "Widgets does receive environment data"
        mock_get_weather.return_value = MOCK_ENVIRONMENT_DATA
        
        response = client.get("/api/v1/environment/public")
        
        assert response.status_code == 200
        data = response.json()
        assert data["temperature_celsius"] == 32
        assert data["wind_speed_kmh"] == 25