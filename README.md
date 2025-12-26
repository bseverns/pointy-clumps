# Wind-Driven Pointy Clumps (EisenScript)

This project generates **EisenScript** files for [Structure Synth], using **live wind data**
to control the "flow" and density of spiky, pointy clumps. You can then export the result
from Structure Synth as a `.obj` file for use in other 3D tools.

The pipeline looks like this:

1. Python script calls the OpenWeatherMap API for a given city.
2. Wind speed and direction are mapped into geometric parameters:
   - how many clumps
   - how many spikes in each clump
   - spike height vs thickness
   - overall twist and spread
3. An EisenScript `.es` file is written to disk.
4. You open the `.es` in Structure Synth and export as `.obj`.

The mapping leans on Beaufort-style bands:

- **Calm**: compact, chunky clumps with few spikes.
- **Breeze**: more clumps, more spikes, gentle twist.
- **Fresh**: stretched spikes, more density, stronger twist.
- **Gale**: tall, thin, bristling spikes in heavily twisted clumps.

Calm wind yields squat, bushy forms; howling wind stretches everything into long,
sharp, directional spikes.

## Requirements

- Python 3.10+ (earlier 3.x may work, but is not tested).
- A free OpenWeatherMap API key.
- [Structure Synth] installed (desktop app for EisenScript).
- Internet access (to query the weather API).

## Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/your-name/wind-pointy-clumps-es.git
cd wind-pointy-clumps-es

python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

For development and tests:

```bash
pip install -r requirements-dev.txt
```

## Configuration

You’ll need an API key from OpenWeatherMap:

1. Sign up and create an API key.
2. Either:
   - Export it as an environment variable:

     ```bash
     export OPENWEATHER_API_KEY="YOUR_API_KEY_HERE"
     ```

   - Or pass `--api-key` every time you run the script.

## Usage

From the repo root:

```bash
python -m wind_clump.cli "Chicago,US" \
  --output generated/chicago_clump.es \
  --units metric \
  --maxdepth 60 \
  --layout ring \
  --climate-anomaly 0.35 \
  --climate-tag "ESA_SM_1981_2010"
```

Options:

- `location` (positional): City name or `"City,CountryCode"` used as `q` in the API.
- `--api-key`: Explicit API key. If omitted, the script uses `$OPENWEATHER_API_KEY`.
- `--units`: `standard` (Kelvin & m/s), `metric` (°C & m/s), or `imperial` (°F & mph). Default: `metric`.
- `--maxdepth`: Global `set maxdepth` in EisenScript. Higher = more recursion & detail.
- `--seed`: Integer seed for Structure Synth’s RNG. If omitted, a random seed is chosen.
- `--output`: Path to the generated `.es` file (default: `generated/clump.es`).
- `--layout`: Scene layout. One of:
  - `ring` (default): Clumps arranged on a circular ring around the origin.
  - `tower`: Clumps stacked vertically along the Y axis, forming a column.
- `--climate-anomaly`: Normalized anomaly sampled from a climate raster (e.g.,
  NASA/ESA drought or soil-moisture). Values are clamped to `[-1, 1]` and only
  shift hue—geometry stays loyal to the wind field.
- `--climate-anomaly-hue`: Degrees of hue swing when the anomaly hits ±1
  (default: 25°). A smaller number keeps the palette calmer.
- `--climate-tag`: Short label describing which climate layer drove the color.
  It ends up in the EisenScript header so you can trace the provenance later.

### Example: ring layout

```bash
python -m wind_clump.cli "Reykjavik,IS" \
  --output generated/reykjavik_ring.es \
  --layout ring
```

### Example: tower layout

```bash
python -m wind_clump.cli "Reykjavik,IS" \
  --output generated/reykjavik_tower.es \
  --layout tower
```

See also: [example renders for calm → gale](generated/examples/README.md). The
EisenScripts + PNG previews are generated locally (via the regen helper) and
left out of version control to keep the repo nimble—run `make regen` and the
inline image embeds in that README will light up with your own local renders.

### Typical Structure Synth workflow

1. Run the generator to produce an `.es` file.
2. Open the `.es` in Structure Synth.
3. Tweak camera and rendering parameters.
4. Export as `.obj` using Structure Synth’s export menu.
5. Import the `.obj` into your 3D tool (Blender, etc.) and render.

## Layouts

- **Ring**: Clumps orbit the origin in a circular band. Wind direction influences color and twist, so gusty winds create radial hedgehog bursts.
- **Tower**: Clumps are stacked upward; the column leans and twists with the flow, reading like a wind-sculpted growth or plume.

Both layouts share the same Beaufort-inspired mapping from wind to clump density,
spike height, and thickness.

## Climate normals & anomalies (NASA/ESA mash-up)

Use long-term climatology rasters (NASA POWER, ESA CCI, Copernicus, etc.) as the
slow-moving scaffold, then let daily anomalies only touch the palette. Because
the generator cleanly separates layout (ring vs tower, twists, spike counts)
from color, you can inject a climate signal as a hue swing without distorting
geometry.

Workflow:

1. Grab a GeoTIFF normal + anomaly pair (soil moisture, drought, NDVI,…).
2. Sample your lat/long using the helper:

   ```bash
   pip install rasterio  # once
   python scripts/sample_climate_normal.py \
     --normal data/esa_sm_longterm_mean.tif \
     --anomaly data/esa_sm_daily_anom.tif \
     --lat 64.13 --lon -21.94 \
     --anomaly-min -0.1 --anomaly-max 0.1 \
     --tag "ESA_SM_1981_2010"
   ```

   The script prints JSON plus a ready-to-paste CLI snippet like
   `--climate-anomaly 0.420 --climate-tag "ESA_SM_1981_2010"`.
3. Feed that snippet into `wind_clump.cli` alongside your city name. The layout
   (ring vs tower) and geometry still come from the live wind; only the hues
   swing according to the anomaly.

Practical tips:

- The anomaly gets clamped to ±1 internally. If your raster’s units are big,
  rescale them with `--anomaly-min/--anomaly-max` so ±1 lands where “wild”
  anomalies live.
- If you only have a normal (no anomaly), still run the script without
  `--anomaly`; the hue shift stays neutral but the JSON gives you metadata to
  log alongside each render.
- Embed the `CLIMATE_TAG` macro (automatically written into the `.es`) in your
  render filenames so you always know which raster drove the color story.

## Regenerating example scenes

There is a small helper script plus a Makefile target to regenerate a handful
of example scenes for several famously windy locations.

To regenerate them:

```bash
export OPENWEATHER_API_KEY="YOUR_API_KEY_HERE"
make regen
```

This writes multiple `.es` files into `generated/examples/`, e.g.:

- `chicago_us_ring.es`
- `chicago_us_tower.es`
- `reykjavik_is_ring.es`
- `wellington_nz_ring.es`
- `wellington_nz_tower.es`

You can open any of them directly in Structure Synth.

## Pull-request sanity check (so "Failed to create PR" stops popping up)

This repo ships without a git remote on purpose. If your tool complains that it
"Failed to create PR," it’s because there’s nowhere to push. Two fixes:

1. Wire up your remote and push the branch:

   ```bash
   git remote add origin git@github.com:your-name/wind-pointy-clumps-es.git
   git push -u origin work
   ```

2. Or, stick to the local flow: commit your changes, then run the PR helper
   your platform provides (it’ll package the branch without needing a networked
   remote). It’s the punk-rock, air-gapped way to ship.

Either way, make sure `git status` is clean and you’ve actually committed before
asking the bot to open a PR. Zero commits = zero PR.

## Tests

To run the test suite:

```bash
make test
# or
pytest
```

Tests cover:

- Mapping from `WindData` to `FlowParams` for calm vs extreme wind,
  including monotonic behavior across Beaufort-like bands.
- EisenScript generation for both `ring` and `tower` layouts.
- NOAA-driven shape generators that puff up spikes with moisture and densify
  clumps when pressure gradients and lightning say the air is unstable.

## NOAA moisture + pressure shape generators

OpenWeatherMap gives us gorgeous wind, but NOAA's feeds hand over extra
atmospheric toys: precipitation rate, humidity, barometric pressure, and even
lightning strike estimates. Drop those into `wind_clump.noaa_shape_generators`
to nudge the existing `FlowParams` without rewriting the wind pipeline.

```python
from wind_clump import (
    NOAAAtmosphere,
    apply_moisture_puffiness,
    apply_pressure_clumping,
    map_wind_to_flow,
)

wind_flow = map_wind_to_flow(wind_data)
noaa = NOAAAtmosphere(
    precipitation_rate_mm_hr=6.2,
    humidity_percent=88,
    barometric_pressure_hpa=987,
    lightning_strikes_per_hr=4,
)

flow_with_moisture = apply_moisture_puffiness(wind_flow, noaa)
storm_ready_flow = apply_pressure_clumping(flow_with_moisture, noaa)
```

- **Moisture → `spike_radius`**: humidity + precip swell spikes from chunky 0.75×
  (desert-dry) to a soaked 1.45× multiplier.
- **Pressure gradients → `clump_count`**: deviations from ~1013 hPa plus
  lightning activity lean into density shifts, spanning roughly 60–160% of the
  wind-derived clump count.

These helpers are composable: call whichever ones match the sensor payload you
have, and feed the returned `FlowParams` directly into `build_eisenscript`.

## License

Pick a license you like (MIT is a good default) and add it as `LICENSE`
if you intend to publish this repo.

[Structure Synth]: http://structuresynth.sourceforge.net/
