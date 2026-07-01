import os

import httpx
from fastapi import APIRouter

router = APIRouter(prefix="/api/weather", tags=["weather"])

DEFAULT_CITY = os.environ.get("DASHBOARD_CITY", "Chennai")

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


async def geocode_city(client: httpx.AsyncClient, city: str) -> dict:
    resp = await client.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
    )
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        raise ValueError(f"No location found for '{city}'")
    return results[0]


@router.get("")
async def get_weather(city: str = DEFAULT_CITY):
    async with httpx.AsyncClient(timeout=10) as client:
        location = await geocode_city(client, city)
        forecast_resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
        )
        forecast_resp.raise_for_status()
        current = forecast_resp.json()["current"]

    return {
        "city": location.get("name", city),
        "region": location.get("admin1"),
        "temperature_c": current["temperature_2m"],
        "wind_speed_kmh": current["wind_speed_10m"],
        "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
    }
