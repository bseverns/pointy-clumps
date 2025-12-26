from __future__ import annotations

import math
import os
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import matplotlib.pyplot as plt

from wind_clump import (
    FlowParams,
    WindAPIError,
    WindData,
    build_eisenscript,
    fetch_wind_for_city,
    map_wind_to_flow,
)


@dataclass(frozen=True)
class ExampleSpec:
    location: str
    layout: str
    seed: int
    label: str
    fallback_wind: Optional[WindData] = None


def _example_specs() -> Iterable[ExampleSpec]:
    """Curated list of windy scenarios across Beaufort-like bands.

    Each spec includes a fallback `WindData` so we can regenerate documentation
    assets in a headless CI box without hitting the OpenWeatherMap API. If an
    API key is present and reachable, we still prefer live data; the fallback
    keeps the pipeline humming when proxies or missing credentials would
    otherwise block the docs.
    """

    return (
        ExampleSpec(
            location="Calm Demo,XX",
            layout="ring",
            seed=11,
            label="calm",
            fallback_wind=WindData(speed_mps=0.8, direction_deg=35.0),
        ),
        ExampleSpec(
            location="Breeze Demo,XX",
            layout="tower",
            seed=12,
            label="breeze",
            fallback_wind=WindData(speed_mps=4.2, direction_deg=120.0),
        ),
        ExampleSpec(
            location="Fresh Demo,XX",
            layout="ring",
            seed=13,
            label="fresh",
            fallback_wind=WindData(speed_mps=8.7, direction_deg=205.0),
        ),
        ExampleSpec(
            location="Gale Demo,XX",
            layout="tower",
            seed=14,
            label="gale",
            fallback_wind=WindData(speed_mps=18.0, direction_deg=315.0),
        ),
    )


def _scene_slug(spec: ExampleSpec) -> str:
    return (
        spec.location.lower()
        .replace(",", "_")
        .replace(" ", "_")
    )


def _render_preview(flow: FlowParams, layout: str, seed: int, output_path: Path) -> None:
    random.seed(seed)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")

    clump_count = max(flow.clump_count, 1)
    angle_step = 2 * math.pi / float(clump_count)
    vertical_step = flow.clump_height * 1.4

    for clump_idx in range(clump_count):
        angle = angle_step * clump_idx
        base_x, base_y, base_z = 0.0, 0.0, 0.0

        if layout == "ring":
            base_x = math.cos(angle) * flow.clump_radius
            base_z = math.sin(angle) * flow.clump_radius
        else:
            base_y = vertical_step * clump_idx

        for _ in range(flow.spikes_per_clump):
            jitter = 0.45 * flow.spike_radius
            jx = (random.random() - 0.5) * jitter
            jy = (random.random() - 0.5) * jitter
            jz = (random.random() - 0.5) * jitter

            length = flow.spike_length * (0.75 + random.random() * 0.35)
            radius = flow.spike_radius * (0.6 + random.random() * 0.6)

            color_shift = 0.25 + 0.5 * random.random()
            color = (1.0 - color_shift, 0.4 + 0.4 * color_shift, 0.2 + 0.6 * color_shift)

            ax.bar3d(
                base_x + jx,
                base_y + jy,
                base_z + jz,
                radius,
                radius,
                length,
                color=color,
                shade=True,
                alpha=0.9,
            )

    spread = max(flow.clump_radius * 1.6, flow.spike_length * 2.0)
    ax.set_xlim(-spread, spread)
    ax.set_ylim(-spread if layout == "ring" else -0.5, spread if layout == "ring" else vertical_step * (clump_count + 0.5))
    ax.set_zlim(0, spread * 1.2)
    ax.view_init(elev=28, azim=40 if layout == "ring" else -35)
    ax.set_axis_off()
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200, transparent=True)
    plt.close(fig)


def main() -> int:
    api_key = os.environ.get("OPENWEATHER_API_KEY")

    out_dir = Path("generated/examples")
    out_dir.mkdir(parents=True, exist_ok=True)

    for spec in _example_specs():
        slug = _scene_slug(spec)
        filename = f"{slug}_{spec.layout}.es"
        out_path = out_dir / filename

        script_text: str | None = None
        flow_for_preview: FlowParams | None = None

        if api_key:
            try:
                live_wind = fetch_wind_for_city(
                    location=spec.location,
                    api_key=api_key,
                    units="metric",
                )
                flow_for_preview = map_wind_to_flow(live_wind)
                script_text = build_eisenscript(
                    flow_params=flow_for_preview,
                    maxdepth=60,
                    seed=spec.seed,
                    layout=spec.layout,
                )
            except WindAPIError as exc:
                print(
                    f"Failed to generate example for {spec.location} [{spec.layout}] via API: {exc}",
                    file=sys.stderr,
                )
                script_text = None

        if script_text is None:
            if not spec.fallback_wind:
                print(
                    f"Skipping {spec.location} [{spec.layout}]: no API key and no fallback wind.",
                    file=sys.stderr,
                )
                continue

            flow_for_preview = map_wind_to_flow(spec.fallback_wind)
            script_text = build_eisenscript(
                flow_params=flow_for_preview,
                maxdepth=60,
                seed=spec.seed,
                layout=spec.layout,
            )
            print(
                f"Used fallback wind for {spec.location} [{spec.layout}] "
                f"(speed={spec.fallback_wind.speed_mps} m/s).",
                file=sys.stderr,
            )

        out_path.write_text(script_text, encoding="utf-8")
        print(f"Wrote {out_path} for {spec.location} [{spec.layout}]")

        if flow_for_preview is None:
            flow_for_preview = map_wind_to_flow(spec.fallback_wind) if spec.fallback_wind else None

        if flow_for_preview:
            preview_path = out_dir / "previews" / f"{slug}_{spec.layout}.png"
            _render_preview(flow_for_preview, layout=spec.layout, seed=spec.seed, output_path=preview_path)
            print(f"Wrote preview {preview_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
