from __future__ import annotations

from dataclasses import dataclass, replace

from .flow_mapping import FlowParams


@dataclass(frozen=True)
class NOAAAtmosphere:
    """Subset of NOAA-style fields we use to warp the geometry."""

    precipitation_rate_mm_hr: float | None = None
    humidity_percent: float | None = None
    barometric_pressure_hpa: float | None = None
    lightning_strikes_per_hr: float | None = None


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _norm(value: float | None, min_value: float, max_value: float) -> float | None:
    if value is None:
        return None
    if max_value <= min_value:
        return None
    return _clamp01((float(value) - min_value) / (max_value - min_value))


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def apply_moisture_puffiness(flow: FlowParams, atmosphere: NOAAAtmosphere) -> FlowParams:
    """Blend precipitation + humidity into the spike radius."""

    humidity_norm = _norm(atmosphere.humidity_percent, 0.0, 100.0)
    precip_norm = _norm(atmosphere.precipitation_rate_mm_hr, 0.0, 20.0)

    contributions: list[tuple[float, float]] = []
    if humidity_norm is not None:
        contributions.append((humidity_norm, 0.6))
    if precip_norm is not None:
        contributions.append((precip_norm, 0.4))

    if not contributions:
        return flow

    weighted = sum(val * weight for val, weight in contributions) / sum(weight for _, weight in contributions)
    radius_factor = _lerp(0.75, 1.45, weighted)
    new_radius = flow.spike_radius * radius_factor
    return replace(flow, spike_radius=new_radius)


def apply_pressure_clumping(flow: FlowParams, atmosphere: NOAAAtmosphere) -> FlowParams:
    """Use barometric gradients + lightning to remap clump density."""

    pressure_norm: float | None = None
    if atmosphere.barometric_pressure_hpa is not None:
        delta = abs(float(atmosphere.barometric_pressure_hpa) - 1013.25)
        pressure_norm = _clamp01(delta / 35.0)

    lightning_norm = _norm(atmosphere.lightning_strikes_per_hr, 0.0, 12.0)

    contributions: list[tuple[float, float]] = []
    if pressure_norm is not None:
        contributions.append((pressure_norm, 0.7))
    if lightning_norm is not None:
        contributions.append((lightning_norm, 0.3))

    if not contributions:
        return flow

    gradient = sum(val * weight for val, weight in contributions) / sum(weight for _, weight in contributions)

    min_clumps = max(1, int(round(flow.clump_count * 0.6)))
    max_clumps = max(1, int(round(flow.clump_count * 1.6)))
    new_clump_count = int(round(_lerp(min_clumps, max_clumps, gradient)))
    return replace(flow, clump_count=new_clump_count)


__all__ = [
    "NOAAAtmosphere",
    "apply_moisture_puffiness",
    "apply_pressure_clumping",
]