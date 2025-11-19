from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from .eisenscript_generator import build_eisenscript
from .flow_mapping import map_wind_to_flow
from .wind_api import WindAPIError, fetch_wind_for_city


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wind_clump",
        description="Generate wind-driven EisenScript pointy clumps.",
    )
    parser.add_argument(
        "location",
        help=(
            "Location string for OpenWeatherMap 'q' parameter, "
            "e.g. 'London,UK' or 'Chicago,US'."
        ),
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        help=(
            "OpenWeatherMap API key. If omitted, the OPENWEATHER_API_KEY "
            "environment variable will be used."
        ),
    )
    parser.add_argument(
        "--units",
        choices=("standard", "metric", "imperial"),
        default="metric",
        help="Units for the OpenWeatherAPI (default: metric).",
    )
    parser.add_argument(
        "--maxdepth",
        type=int,
        default=60,
        help="Global max recursion depth for the EisenScript (default: 60).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for Structure Synth. If omitted, a random seed is chosen.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="generated/clump.es",
        help="Path to output EisenScript file (default: generated/clump.es).",
    )
    parser.add_argument(
        "--layout",
        choices=("ring", "tower"),
        default="ring",
        help="Scene layout: 'ring' of clumps or vertical 'tower' (default: ring).",
    )
    parser.add_argument(
        "--climate-anomaly",
        type=float,
        default=0.0,
        help=(
            "Normalized anomaly (-1..1) sampled from a climate raster. "
            "Positive values swing hues warm, negatives swing cool."
        ),
    )
    parser.add_argument(
        "--climate-anomaly-hue",
        type=float,
        default=25.0,
        help=(
            "Maximum hue swing (in degrees) to apply when the anomaly hits ±1. "
            "Default: 25 degrees."
        ),
    )
    parser.add_argument(
        "--climate-tag",
        default=None,
        help=(
            "Optional label describing the climate layer (e.g., 'CHIRPS_1981-2020'). "
            "We embed it as metadata so you remember which raster drove the colors."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    api_key = args.api_key or os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        print(
            "Error: No API key supplied. Use --api-key or set OPENWEATHER_API_KEY.",
            file=sys.stderr,
        )
        return 2

    try:
        wind = fetch_wind_for_city(
            location=args.location,
            api_key=api_key,
            units=args.units,
        )
    except WindAPIError as exc:
        print(f"Error fetching wind data: {exc}", file=sys.stderr)
        return 1

    flow = map_wind_to_flow(wind)
    anomaly_value = max(-1.0, min(1.0, float(args.climate_anomaly)))
    hue_shift = anomaly_value * float(args.climate_anomaly_hue)

    script_text = build_eisenscript(
        flow_params=flow,
        maxdepth=args.maxdepth,
        seed=args.seed,
        layout=args.layout,
        hue_shift_deg=hue_shift,
        climate_tag=args.climate_tag,
        climate_anomaly=anomaly_value,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(script_text, encoding="utf-8")

    print(
        f"Wrote EisenScript to {output_path} "
        f"(location={args.location!r}, wind={flow.wind_speed_mps:.2f} m/s, layout={args.layout})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
