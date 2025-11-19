#!/usr/bin/env python3
"""Sample a climate normal + anomaly raster to steer hue swings.

NASA/ESA publish tons of GeoTIFFs (precipitation, drought, snow, etc.). This
script samples a lat/long pixel so you can treat multi-year averages as the
"base layout" and daily anomalies as a color-only twist.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import rasterio
except ImportError as exc:  # pragma: no cover - optional helper
    raise SystemExit(
        "rasterio is required for sampling rasters. Install it via `pip install rasterio`."
    ) from exc


def _sample_raster(path: Path, lat: float, lon: float) -> float:
    """Return the value at lat/lon from a GeoTIFF."""
    with rasterio.open(path) as dataset:
        row, col = dataset.index(lon, lat)
        band = dataset.read(1, masked=True)
        value = band[row, col]
        if hasattr(value, "mask") and getattr(value, "mask"):
            raise RuntimeError("The requested coordinate is masked/no-data in this raster.")
        return float(value)


def _normalize_anomaly(value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 0.0
    t = (value - min_value) / (max_value - min_value)
    normalized = (t * 2.0) - 1.0
    return max(-1.0, min(1.0, normalized))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sample a climate normal + anomaly raster and emit CLI hints.",
    )
    parser.add_argument("--normal", required=True, help="Path to the normal/mean GeoTIFF.")
    parser.add_argument(
        "--anomaly",
        help="Path to the anomaly GeoTIFF for the same field (optional).",
    )
    parser.add_argument("--lat", type=float, required=True, help="Latitude in decimal degrees.")
    parser.add_argument("--lon", type=float, required=True, help="Longitude in decimal degrees.")
    parser.add_argument(
        "--anomaly-min",
        type=float,
        help="Minimum anomaly value to map to -1 (required when --anomaly is set).",
    )
    parser.add_argument(
        "--anomaly-max",
        type=float,
        help="Maximum anomaly value to map to +1 (required when --anomaly is set).",
    )
    parser.add_argument(
        "--tag",
        default=None,
        help="Short label describing the dataset (e.g., 'ESA_CCI_SM_v07').",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Optional path to write a JSON blob with the sampled values.",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    normal_value = _sample_raster(Path(args.normal), lat=args.lat, lon=args.lon)

    anomaly_value: float | None = None
    normalized_anomaly = 0.0
    if args.anomaly:
        if args.anomaly_min is None or args.anomaly_max is None:
            parser.error("--anomaly-min and --anomaly-max are required when --anomaly is used.")
        anomaly_value = _sample_raster(Path(args.anomaly), lat=args.lat, lon=args.lon)
        normalized_anomaly = _normalize_anomaly(anomaly_value, args.anomaly_min, args.anomaly_max)

    tag = args.tag or "CLIMATE_NORMAL"
    cli_snippet = f"--climate-anomaly {normalized_anomaly:.3f} --climate-tag \"{tag}\""

    payload: dict[str, Any] = {
        "lat": args.lat,
        "lon": args.lon,
        "normal_value": normal_value,
        "anomaly_value": anomaly_value,
        "normalized_anomaly": normalized_anomaly,
        "suggested_cli_flags": cli_snippet,
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print()
    print("Use these flags when calling wind_clump:")
    print(cli_snippet)
    return 0


if __name__ == "__main__":  # pragma: no cover - helper script
    raise SystemExit(main())