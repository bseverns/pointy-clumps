# Example renders: calm → gale (ring + tower)

These are teaching-friendly snapshots that show how the Beaufort-ish bands map
onto the **ring** and **tower** layouts. Each render comes from an EisenScript
in `generated/examples/`. Previews live in `generated/examples/previews/`
**but are intentionally not tracked in git**—generate them locally to keep the
repo light and binary-free. Once you regen the assets, the Markdown image tags
below will light up with your local renders.

## The four moods

| Mood | Layout | Expected preview (after you run regen) |
| --- | --- | --- |
| Calm (0.8 m/s, soft twist) | Ring | `previews/calm_demo_xx_ring.png` |
| Breeze (4.2 m/s, leaning column) | Tower | `previews/breeze_demo_xx_tower.png` |
| Fresh (8.7 m/s, stretched spikes) | Ring | `previews/fresh_demo_xx_ring.png` |
| Gale (18 m/s, bristling plume) | Tower | `previews/gale_demo_xx_tower.png` |

If you prefer pictures over filenames, drop the generated previews into place
and they’ll embed right here:

- Calm, ring:

  ![Calm ring preview](previews/calm_demo_xx_ring.png)

- Breeze, tower:

  ![Breeze tower preview](previews/breeze_demo_xx_tower.png)

- Fresh, ring:

  ![Fresh ring preview](previews/fresh_demo_xx_ring.png)

- Gale, tower:

  ![Gale tower preview](previews/gale_demo_xx_tower.png)

The previews use the same flow parameters that the EisenScript generator spits
out. They’re intentionally minimal—half sketchbook, half street flyer—so you can
focus on how wind speed and layout change the composition.

## Files to open in Structure Synth

- `calm_demo_xx_ring.es`
- `breeze_demo_xx_tower.es`
- `fresh_demo_xx_ring.es`
- `gale_demo_xx_tower.es`

Those `.es` files are also generated on demand and ignored by git. Keep them
local, remix them, and blow them away when you’re done.

## Regenerating (with or without the API)

```bash
# Preferred: live data (will hit OpenWeatherMap)
export OPENWEATHER_API_KEY="YOUR_KEY"
PYTHONPATH=. python scripts/regen_examples.py

# Air-gapped / proxy jail: rely on the baked-in fallback winds above
PYTHONPATH=. python scripts/regen_examples.py
```

The generator still honors `--layout` and wind-driven geometry; the only switch
is whether the wind comes from the API or the deterministic fallback values you
see in the table. Once you’ve opened the `.es` in Structure Synth, tweak the
camera and export a fresh screenshot if you want a higher-fidelity render for
your own notebook.
