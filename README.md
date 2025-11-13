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
  --layout ring
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

## License

Pick a license you like (MIT is a good default) and add it as `LICENSE`
if you intend to publish this repo.

[Structure Synth]: http://structuresynth.sourceforge.net/
