from __future__ import annotations

from wind_clump.flow_mapping import FlowParams, map_wind_to_flow
from wind_clump.wind_api import WindData


def test_zero_wind_produces_calm_family() -> None:
    wind = WindData(speed_mps=0.0, direction_deg=None)
    params = map_wind_to_flow(wind)

    assert isinstance(params, FlowParams)
    assert params.wind_speed_mps == 0.0
    assert params.wind_direction_deg is None

    # Calm family should be compact and chunky.
    assert 3 <= params.clump_count <= 6
    assert 10 <= params.spikes_per_clump <= 60
    assert 0.5 <= params.spike_length <= 1.5
    assert 0.2 <= params.spike_radius <= 0.4
    assert 0.8 <= params.clump_radius <= 2.5
    assert 0.3 <= params.clump_height <= 1.0
    assert -20.0 <= params.global_twist <= 20.0


def test_extreme_wind_yields_more_intense_geometry() -> None:
    calm_wind = WindData(speed_mps=0.0, direction_deg=None)
    gale_wind = WindData(speed_mps=100.0, direction_deg=270.0)

    calm_params = map_wind_to_flow(calm_wind)
    gale_params = map_wind_to_flow(gale_wind)

    # Raw speed is preserved, but geometry is shaped via band clamping.
    assert gale_params.wind_speed_mps == 100.0

    assert gale_params.clump_count > calm_params.clump_count
    assert gale_params.spikes_per_clump > calm_params.spikes_per_clump
    assert gale_params.spike_length > calm_params.spike_length
    assert gale_params.spike_radius < calm_params.spike_radius
    assert gale_params.clump_radius > calm_params.clump_radius
    assert gale_params.clump_height > calm_params.clump_height
    assert gale_params.global_twist > calm_params.global_twist


def test_direction_is_carried_through() -> None:
    wind = WindData(speed_mps=3.5, direction_deg=123.0)
    params = map_wind_to_flow(wind)

    assert params.wind_direction_deg == 123.0
