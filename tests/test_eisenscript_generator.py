from __future__ import annotations

from wind_clump.eisenscript_generator import build_eisenscript
from wind_clump.flow_mapping import FlowParams


def _sample_flow_params() -> FlowParams:
    return FlowParams(
        wind_speed_mps=5.0,
        wind_direction_deg=90.0,
        clump_count=8,
        spikes_per_clump=40,
        spike_length=1.5,
        spike_radius=0.2,
        clump_radius=2.0,
        clump_height=1.0,
        global_twist=5.0,
    )


def test_build_eisenscript_ring_layout() -> None:
    params = _sample_flow_params()
    script = build_eisenscript(flow_params=params, maxdepth=42, seed=123, layout="ring")

    assert "set maxdepth 42" in script
    assert "set seed 123" in script
    assert "// Layout: ring" in script
    assert "ry ANGLE_STEP" in script
    assert "#define VERTICAL_STEP" in script  # constant defined even when unused


def test_build_eisenscript_tower_layout() -> None:
    params = _sample_flow_params()
    script = build_eisenscript(flow_params=params, maxdepth=30, seed=999, layout="tower")

    assert "set maxdepth 30" in script
    assert "set seed 999" in script
    assert "// Layout: tower" in script
    assert "y VERTICAL_STEP" in script
    assert "#define ANGLE_STEP" in script  # constant defined even when unused

def test_climate_metadata_and_hue_shift_show_up() -> None:
    params = _sample_flow_params()
    script = build_eisenscript(
        flow_params=params,
        hue_shift_deg=30.0,
        climate_tag="ESA_SM",
        climate_anomaly=0.5,
    )

    assert '#define CLIMATE_TAG "ESA_SM"' in script
    assert "#define CLIMATE_ANOMALY 0.500" in script
    assert "#define HUE_SHIFT_DEG 30.000" in script
    assert "#define BASE_HUE 120.000" in script  # 90° + 30° hue shift

def test_direction_and_speed_are_reflected_in_script() -> None:
    params = _sample_flow_params()
    script = build_eisenscript(flow_params=params, maxdepth=10, seed=1, layout="ring")

    assert "WIND_SPEED_MPS 5.000" in script
    assert "WIND_DIRECTION_DEG 90.000" in script
