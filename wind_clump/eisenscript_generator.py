from __future__ import annotations

import random
from typing import Final

from .flow_mapping import FlowParams


HEADER_COMMENT: Final[str] = """/*
  Wind-Driven Pointy Clumps
  Auto-generated EisenScript.

  This file was produced by wind_clump, using live wind data to steer:
    - clump count
    - spikes per clump
    - spike length / thickness
    - twist and spread

  Open this in Structure Synth and export as OBJ to continue the journey.
*/"""


def build_eisenscript(
    flow_params: FlowParams,
    maxdepth: int = 60,
    seed: int | None = None,
    layout: str = "ring",
) -> str:
    """Turn geometric flow parameters into an EisenScript grammar."""
    direction = (
        flow_params.wind_direction_deg if flow_params.wind_direction_deg is not None else 0.0
    )

    base_hue = direction % 360.0
    hue1 = (base_hue + 15.0) % 360.0
    hue2 = (base_hue - 15.0) % 360.0

    clump_count = max(flow_params.clump_count, 1)
    angle_step = 360.0 / float(clump_count)
    vertical_step = flow_params.clump_height * 1.4

    seed_value = seed if seed is not None else random.randint(0, 2**31 - 1)

    layout_mode = layout.lower()
    if layout_mode not in ("ring", "tower"):
        layout_mode = "ring"

    if layout_mode == "ring":
        scene_rule = """
// Start rule: a ring of clumps, wrapped around the origin.
rule scene {
  CLUMP_COUNT * {
    ry ANGLE_STEP
  } clump
}
"""
    else:
        scene_rule = """
// Start rule: a vertical tower of clumps, rising with the flow.
rule scene {
  CLUMP_COUNT * {
    y VERTICAL_STEP
  } clump
}
"""

    script = f"""{HEADER_COMMENT}

// Layout: {layout_mode}

set maxdepth {maxdepth}
set maxobjects 300000
set seed {seed_value}
set background #000000

// Wind metadata
#define WIND_SPEED_MPS {flow_params.wind_speed_mps:.3f}
#define WIND_DIRECTION_DEG {direction:.3f}

// Derived color anchors
#define BASE_HUE {base_hue:.3f}
#define HUE_VARIANT_1 {hue1:.3f}
#define HUE_VARIANT_2 {hue2:.3f}

// Clump geometry
#define CLUMP_COUNT {clump_count}
#define SPIKES_PER_CLUMP {flow_params.spikes_per_clump}
#define SPIKE_LENGTH {flow_params.spike_length:.3f}
#define SPIKE_RADIUS {flow_params.spike_radius:.3f}
#define CLUMP_RADIUS {flow_params.clump_radius:.3f}
#define CLUMP_HEIGHT {flow_params.clump_height:.3f}
#define GLOBAL_TWIST {flow_params.global_twist:.3f}
#define ANGLE_STEP {angle_step:.3f}
#define VERTICAL_STEP {vertical_step:.3f}
{scene_rule}
// Each clump is pushed outward and twisted with the flow.
rule clump {{
  {{
    ry WIND_DIRECTION_DEG
    rz GLOBAL_TWIST
    x CLUMP_RADIUS
  }} spike_cluster
}}

// A clump is a dense cluster of slender spikes.
rule spike_cluster {{
  SPIKES_PER_CLUMP * {{
    y CLUMP_HEIGHT
    s SPIKE_RADIUS SPIKE_RADIUS SPIKE_LENGTH
  }} spike
}}

// Pointy spikes: three slight variations, randomly chosen.
rule spike {{
  {{ hue BASE_HUE sat 90 b 90 a 90 }} box
}}

rule spike w 2 {{
  {{ ry 10 hue HUE_VARIANT_1 sat 80 b 95 a 85 }} box
}}

rule spike w 2 {{
  {{ ry -10 hue HUE_VARIANT_2 sat 80 b 80 a 80 }} box
}}
"""
    return script
