"""
Wind-driven EisenScript generator: fetch wind data, map to geometry, emit pointy clumps.
"""

from .wind_api import WindData, WindAPIError, fetch_wind_for_city
from .flow_mapping import FlowParams, map_wind_to_flow
from .eisenscript_generator import build_eisenscript


def generate_script_for_location(
    location: str,
    api_key: str,
    units: str = "metric",
    maxdepth: int = 60,
    seed: int | None = None,
    layout: str = "ring",
) -> str:
    """Convenience helper to go from city name to ready-to-save EisenScript text."""
    wind = fetch_wind_for_city(location=location, api_key=api_key, units=units)
    flow = map_wind_to_flow(wind)
    return build_eisenscript(flow_params=flow, maxdepth=maxdepth, seed=seed, layout=layout)


__all__ = [
    "WindData",
    "WindAPIError",
    "FlowParams",
    "fetch_wind_for_city",
    "map_wind_to_flow",
    "build_eisenscript",
    "generate_script_for_location",
]
