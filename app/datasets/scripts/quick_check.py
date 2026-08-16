import httpx

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# two clearly distinct, known points
coords = [(-25.7479, 28.2293), (-33.9249, 18.4241)]  # Pretoria, Cape Town
latitudes, longitudes = zip(*coords)

params = {
    "latitude": latitudes,
    "longitude": longitudes,
    "start_date": "2024-01-01",
    "end_date": "2024-01-02",
    "hourly": ["temperature_2m"],
}

req = httpx.Request("GET", ARCHIVE_URL, params=params)
print("URL actually sent:")
print(req.url)

response = httpx.get(ARCHIVE_URL, params=params, timeout=30.0)
data = response.json()
print()
print("Response type:", type(data))
print("Number of points returned:", len(data) if isinstance(data, list) else 1)
if isinstance(data, list):
    for i, point in enumerate(data):
        print(f"  point {i}: lat={point.get('latitude')}, lon={point.get('longitude')}")