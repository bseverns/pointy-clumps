from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

import requests


OPENWEATHER_URL: Final[str] = "https://api.openweathermap.org/data/2.5/weather"


class WindAPIError(Exception):
    """Raised when anything goes wrong while talking to the weather API."""


@dataclass(frozen=True)
class WindData:
    """Wind speed and direction in a consistent, geometry-friendly form."""

    speed_mps: float
    direction_deg: float | None


def _convert_speed_to_mps(speed: float, units: str) -> float:
    """Convert the API's wind speed into meters per second."""
    if units == "imperial":
        return speed * 0.44704
    return speed


def fetch_wind_for_city(
    location: str,
    api_key: str,
    units: str = "metric",
    timeout: float = 10.0,
) -> WindData:
    """Fetch current wind speed and direction for a city from OpenWeatherMap."""
    if not api_key:
        raise WindAPIError(
            "No OpenWeatherMap API key provided. "
            "Set OPENWEATHER_API_KEY or pass --api-key."
        )

    params = {
        "q": location,
        "appid": api_key,
        "units": units,
    }

    try:
        response = requests.get(OPENWEATHER_URL, params=params, timeout=timeout)
    except requests.RequestException as exc:
        raise WindAPIError(f"Error contacting OpenWeatherMap: {exc}") from exc

    if response.status_code != 200:
        message: str | None = None
        try:
            payload: Any = response.json()
            if isinstance(payload, dict):
                api_message = payload.get("message")
                api_code = payload.get("cod")
                if api_message:
                    message = f"{api_code}: {api_message}" if api_code else str(api_message)
        except ValueError:
            message = None

        if not message:
            snippet = response.text.strip()
            if len(snippet) > 120:
                snippet = snippet[:117] + "..."
            message = f"HTTP {response.status_code}: {snippet or 'unknown error'}"

        raise WindAPIError(f"OpenWeatherMap request failed: {message}")

    try:
        data: Any = response.json()
    except ValueError as exc:
        raise WindAPIError("API returned invalid JSON.") from exc

    if not isinstance(data, dict):
        raise WindAPIError("Unexpected JSON structure from API (expected an object).")

    wind = data.get("wind")
    if not isinstance(wind, dict):
        raise WindAPIError("API response does not contain 'wind' section.")

    speed_raw = wind.get("speed")
    if speed_raw is None:
        raise WindAPIError("API response does not contain 'wind.speed' value.")
    try:
        speed_value = float(speed_raw)
    except (TypeError, ValueError) as exc:
        raise WindAPIError(f"API returned non-numeric wind speed: {speed_raw!r}") from exc

    speed_mps = max(0.0, _convert_speed_to_mps(speed_value, units=units))

    direction_raw = wind.get("deg")
    if direction_raw is None:
        direction_deg: float | None = None
    else:
        try:
            direction_deg = float(direction_raw)
        except (TypeError, ValueError):
            direction_deg = None

    return WindData(speed_mps=speed_mps, direction_deg=direction_deg)
