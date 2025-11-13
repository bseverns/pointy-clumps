from __future__ import annotations

from dataclasses import dataclass

from .wind_api import WindData


@dataclass(frozen=True)
class FlowParams:
    """Geometry parameters derived from the wind.

    The bands roughly echo Beaufort:
      - Calm   → few, chunky clumps.
      - Breeze → more clumps, gentle twist.
      - Fresh  → taller, sharper spikes.
      - Gale   → dense, thin spikes with strong twist.
    """

    wind_speed_mps: float
    wind_direction_deg: float | None

    clump_count: int
    spikes_per_clump: int

    spike_length: float
    spike_radius: float

    clump_radius: float
    clump_height: float

    global_twist: float


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def map_wind_to_flow(wind: WindData) -> FlowParams:
    """Map a physical wind measurement onto a family of clumpy, pointy shapes.

    Uses Beaufort-like bands so qualitative shifts happen at key thresholds.
    """
    speed = max(0.0, float(wind.speed_mps))

    # Band edges in m/s, loosely inspired by Beaufort.
    if speed < 1.5:
        band_name = "calm"
        band_min, band_max = 0.0, 1.5
    elif speed < 7.5:
        band_name = "breeze"
        band_min, band_max = 1.5, 7.5
    elif speed < 13.5:
        band_name = "fresh"
        band_min, band_max = 7.5, 13.5
    else:
        band_name = "gale"
        band_min, band_max = 13.5, 20.0

    # For shaping we clamp speeds to the band; extreme gales still max-out the "gale" family.
    shape_speed = _clamp(speed, band_min, band_max)
    if band_max > band_min:
        local_norm = (shape_speed - band_min) / (band_max - band_min)
    else:
        local_norm = 0.0

    if band_name == "calm":
        clump_min, clump_max = 3, 5
        spikes_min, spikes_max = 12, 40
        length_min, length_max = 0.6, 1.2
        radius_min, radius_max = 0.32, 0.24
        radius_min, radius_max = max(radius_min, radius_max), min(radius_min, radius_max)
        cr_min, cr_max = 1.0, 2.0
        ch_min, ch_max = 0.4, 0.8
        twist_min, twist_max = -5.0, 5.0
    elif band_name == "breeze":
        clump_min, clump_max = 5, 9
        spikes_min, spikes_max = 40, 80
        length_min, length_max = 1.2, 2.0
        radius_min, radius_max = 0.24, 0.18
        radius_min, radius_max = max(radius_min, radius_max), min(radius_min, radius_max)
        cr_min, cr_max = 2.0, 3.5
        ch_min, ch_max = 0.8, 1.5
        twist_min, twist_max = 5.0, 15.0
    elif band_name == "fresh":
        clump_min, clump_max = 9, 13
        spikes_min, spikes_max = 80, 130
        length_min, length_max = 2.0, 3.0
        radius_min, radius_max = 0.18, 0.11
        radius_min, radius_max = max(radius_min, radius_max), min(radius_min, radius_max)
        cr_min, cr_max = 3.5, 5.0
        ch_min, ch_max = 1.5, 2.3
        twist_min, twist_max = 15.0, 30.0
    else:  # gale
        clump_min, clump_max = 13, 18
        spikes_min, spikes_max = 130, 190
        length_min, length_max = 3.0, 4.2
        radius_min, radius_max = 0.11, 0.06
        radius_min, radius_max = max(radius_min, radius_max), min(radius_min, radius_max)
        cr_min, cr_max = 5.0, 7.0
        ch_min, ch_max = 2.3, 3.2
        twist_min, twist_max = 30.0, 50.0

    clump_count = int(round(_lerp(clump_min, clump_max, local_norm)))
    spikes_per_clump = int(round(_lerp(spikes_min, spikes_max, local_norm)))

    spike_length = _lerp(length_min, length_max, local_norm)
    spike_radius = _lerp(radius_min, radius_max, local_norm)

    clump_radius = _lerp(cr_min, cr_max, local_norm)
    clump_height = _lerp(ch_min, ch_max, local_norm)

    global_twist = _lerp(twist_min, twist_max, local_norm)

    return FlowParams(
        wind_speed_mps=speed,
        wind_direction_deg=wind.direction_deg,
        clump_count=clump_count,
        spikes_per_clump=spikes_per_clump,
        spike_length=spike_length,
        spike_radius=spike_radius,
        clump_radius=clump_radius,
        clump_height=clump_height,
        global_twist=global_twist,
    )
