from __future__ import annotations

from wind_clump.flow_mapping import FlowParams
from wind_clump.noaa_shape_generators import (
    NOAAAtmosphere,
    apply_moisture_puffiness,
    apply_pressure_clumping,
)


def _base_flow() -> FlowParams:
    return FlowParams(
        wind_speed_mps=5.0,
        wind_direction_deg=180.0,
        clump_count=8,
        spikes_per_clump=60,
        spike_length=1.5,
        spike_radius=0.2,
        clump_radius=2.5,
        clump_height=1.2,
        global_twist=10.0,
    )


def test_moisture_puffiness_swells_radius():
    base = _base_flow()
    soggy = NOAAAtmosphere(precipitation_rate_mm_hr=12.0, humidity_percent=95.0)
    dry = NOAAAtmosphere(precipitation_rate_mm_hr=0.0, humidity_percent=15.0)

    soggy_flow = apply_moisture_puffiness(base, soggy)
    dry_flow = apply_moisture_puffiness(base, dry)

    assert soggy_flow.spike_radius > base.spike_radius
    assert dry_flow.spike_radius < base.spike_radius


def test_pressure_clumping_increases_density_with_gradient():
    base = _base_flow()
    strong_gradient = NOAAAtmosphere(barometric_pressure_hpa=970.0, lightning_strikes_per_hr=8.0)
    flat = NOAAAtmosphere(barometric_pressure_hpa=1013.0, lightning_strikes_per_hr=0.0)

    storm_flow = apply_pressure_clumping(base, strong_gradient)
    flat_flow = apply_pressure_clumping(base, flat)

    assert storm_flow.clump_count > base.clump_count
    assert flat_flow.clump_count <= base.clump_count
    