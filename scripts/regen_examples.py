from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable, Tuple

from wind_clump import WindAPIError, generate_script_for_location


ExampleSpec = Tuple[str, str, int]


def _example_specs() -> Iterable[ExampleSpec]:
    """Curated list of windy locations, layouts, and seeds."""
    return [
        ("Chicago,US", "ring", 101),
        ("Chicago,US", "tower", 102),
        ("Reykjavik,IS", "ring", 201),
        ("Wellington,NZ", "ring", 301),
        ("Wellington,NZ", "tower", 302),
    ]


def main() -> int:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        print(
            "Error: OPENWEATHER_API_KEY is not set; cannot regenerate examples.",
            file=sys.stderr,
        )
        return 2

    out_dir = Path("generated/examples")
    out_dir.mkdir(parents=True, exist_ok=True)

    for location, layout, seed in _example_specs():
        slug = (
            location.lower()
            .replace(",", "_")
            .replace(" ", "_")
        )
        filename = f"{slug}_{layout}.es"
        out_path = out_dir / filename

        try:
            script_text = generate_script_for_location(
                location=location,
                api_key=api_key,
                layout=layout,
                maxdepth=60,
                seed=seed,
            )
        except WindAPIError as exc:
            print(
                f"Failed to generate example for {location} [{layout}]: {exc}",
                file=sys.stderr,
            )
            continue

        out_path.write_text(script_text, encoding="utf-8")
        print(f"Wrote {out_path} for {location} [{layout}]")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
