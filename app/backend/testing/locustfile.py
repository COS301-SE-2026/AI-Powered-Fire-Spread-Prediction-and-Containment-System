import os
import random
from locust import HttpUser, task, between, events
from sqlalchemy import create_engine, text

class FireAwayUser(HttpUser):
    # wait time in seconds, btw users
    wait_time = between(0.5, 1.5)

    @task(3)
    def view_public_map_feed(self):
        """Simulates users fetching active public fire reports."""
        with self.client.get(
            "/api/guests/reported-fires?limit=50",
            name="GET /api/guests/reported-fires",
            timeout=5.0,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed with status: {response.status_code}")

    @task(1)
    def submit_fire_report(self):
        """Simulate users submitting concurrent fire reports."""
        payload = {
            "lat": round(random.uniform(-34.5, -33.5), 6),
            "lng": round(random.uniform(18.0, 19.5), 6),
            "location_text": "Sector Test Area",
            "description": "Simulated wildfire report under load test",
            "image_url": None,
            "boundary_radius": round(random.uniform(0.5, 5.0), 2),
            "photo_hash": None
        }
        with self.client.post(
            "/api/guests/reported-fires",
            json=payload,
            name="POST /api/guests/reported-fires",
            timeout=5.0,
            catch_response=True
        ) as response:
            if response.status_code not in (200, 201):
                response.failure(f"Failed with status: {response.status_code}")