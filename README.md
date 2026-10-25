# Home 3D — floor-plan model

Three.js model of the supplied floor plan, built for the HACS card
`giosci1994/floor3d-card` (v2.13.2) and displayed full-screen on the
Home Assistant dashboard **Home 3D** (`home-3d`).

## Current status

- Model regenerated from `floorplan.jpg`: outer footprint, slanted top
  wall, rooms, windows, two north balconies with two full-height glass
  doors each, balcony slabs/glass parapets/handrails, furniture and five
  lamp objects. The common stairwell is outside the apartment and is not
  modelled.
- The dashboard loads the model from the **public GitHub repo** via
  `raw.githubusercontent.com`, so it works off-LAN. The local preview
  server is only for development.
- Walls use a custom **`walls: sims`** mode: walls whose outer side faces
  the camera are shown as a closed **20 cm stub**; far walls stay at full
  height. This is the Sims-like cut, not the old uniform `low` cut.
- The mode is provided by a small custom build of floor3d-card v2.13.2,
  loaded as **`custom:floor3d-card-sims`**. The HACS card remains
  installed; the custom resource is separate and shares its editor.
- Absolute scale is still a placeholder: the plan has no printed
  dimensions, so `SCALE = 70 px/m` is kept. Overall footprint is
  **14.6 × 10.6 m**. The OBJ is exported in **centimetres** because
  floor3d-card's lights, camera and zoom distances use cm.
- Room mapping is confirmed: **left = Bedroom**, **right = Studio**,
  **WC 1 = Master bathroom**. Only the split of the central area into
  Kitchen (west) and Living room (east) is still an assumption, marked
  **\*** in the legend.

## Current URLs and commits

| Thing | Value |
|---|---|
| Model commit | `0b3b367` |
| Model base URL | `https://raw.githubusercontent.com/c0pper/homeassistant-3d-card/0b3b367/` |
| Custom card resource | `https://cdn.jsdelivr.net/gh/c0pper/homeassistant-3d-card@0209251/custom-card/floor3d-card.js` |
| Dashboard card type | `custom:floor3d-card-sims` |
| Wall mode | `sims` |

The model base URL is commit-pinned. Raw GitHub caches a branch for
about five minutes and a `?v=` query does **not** reliably bypass that
cache (tested); a commit-SHA URL is immutable and served immediately.
The cost is that each model change needs the path updated to the new
commit.

The custom card is served by **jsDelivr**, not raw GitHub: raw GitHub
serves `.js` as `text/plain`, which browsers reject for module
resources. jsDelivr serves it as `application/javascript` with CORS.
The commit in the jsDelivr URL contains `custom-card/`; the entry imports
its `floor3d-card-core-*.js` and editor chunk from the same folder.

The model is loaded in the **browser**, not by Home Assistant, so the
device showing the dashboard must be able to reach GitHub and jsDelivr.
No HA token is needed. The repo is public, so the model and floor plan
are public too; do not put secrets in the model or repo.

## Files

| File | Purpose |
|---|---|
| `home.obj`, `home.mtl` | Model + materials. These are the files the card fetches. |
| `home.svg`, `home_preview.png` | Numbered top-view preview and room/light legend. |
| `card.yaml` | Current card config: `custom:floor3d-card-sims`, GitHub raw path, `walls: sims`, camera and zoom areas. |
| `manifest.json` | Object IDs, room numbers, areas, HA areas, light mapping, wall split metadata. |
| `make_home.py` | **The real generator** — builds the model from `floorplan.jpg`; splits walls at 20 cm. Edit the tables at the top and re-run. |
| `custom-card/` | Patched floor3d-card v2.13.2 build, the `sims` wall mode, MIT licence, source patch and build notes. |
| `serve.py` | Local CORS server on port 8765, for LAN development only. |
| `floorplan.jpg` / `.png` | Source floor plan. |
| `make_model_starter_OLD.py` | Legacy placeholder starter (5 rooms). **Do not run** — it overwrites the real model with a simplified one. |
| `floor3d-model.zip` | Handy package of the model, preview, card and notes. |

## How `walls: sims` works

Every wall solid is split in the model at **20 cm**:

- `wall_sims_low_*` — a closed 0–20 cm prism, so the stub has a solid top;
- `wall_sims_high_*` — the rest of the wall.

Window and balcony glass is split the same way
(`wall_sims_glass_low_*` / `wall_sims_glass_high_*`).

The custom card computes each wall's outward normal (the same rule the
HACS card uses for `fade`). When the wall's outward side faces the
camera (`normal · camera_side > 0.3`), the high part is hidden; the low
part remains. Far walls keep both parts and look full. The rule handles
corners — both adjacent facades drop — and applies to **exterior and
interior** walls. Near glass drops with its wall.

- **Snap**, not animated: the upper part disappears/reappears as the
  camera crosses the threshold.
- **Straight above**: the horizontal camera-side vector is zero, so no
  wall is near and every wall stays full. This avoids an all-low flash
  when passing overhead.
- The low stub is **20 cm** including a closed top; it is baked into the
  model (`SIMS_H = 0.20` in `make_home.py`), not configured in the card.
- Tall non-wall objects (wardrobe, lamps, balcony rails) stay full.

The custom build registers **`floor3d-card-sims`**, not `floor3d-card`.
The HACS card remains available for `walls: none/fade/low`, and its
`floor3d-card-editor` is reused.

## Publishing a model change

After editing `make_home.py` and regenerating:

```bash
cd /home/simo/floor3d-starter
.venv/bin/python make_home.py
.venv/bin/python - <<'PY'
import cairosvg
cairosvg.svg2png(url='home.svg', write_to='home_preview.png', output_width=1600)
PY
git add home.obj home.mtl home.svg home_preview.png card.yaml manifest.json \
        make_home.py README.md AGENTS.md GLOSSARY.md floor3d-model.zip
git commit -m "Describe the model change"
git push origin master
```

Then read the new commit:

```bash
git rev-parse --short HEAD
```

and set the dashboard card's `path` to
`https://raw.githubusercontent.com/c0pper/homeassistant-3d-card/<sha>/`
(the same value in `card.yaml`). The current model commit is
**`0b3b367`**. `objfile` and `mtlfile` stay plain names.

If the custom card itself changes, rebuild it (see
`custom-card/README.md`), commit the new `custom-card/` files, and update
the dashboard resource URL to the new jsDelivr commit.

## Room mapping

Numbers match `home.svg`.

| # | Object ID | Name | Area | HA area | Confidence |
|---|---|---|---|---|---|
| 1 | `room_left` | Bedroom | 9.4 m² | `bedroom` | confirmed (left) |
| 2 | `room_kitchen` | Kitchen | 14.8 m² | `kitchen` | plan has `K` |
| 3 | `room_living` | Living room \* | 18.4 m² | `living_room` | central-east split assumed |
| 4 | `room_corridor` | Corridor | 8.1 m² | — | plan has `CORRIDOIO` |
| 5 | `room_right` | Studio | 18.1 m² | `studio` | confirmed (right) |
| 6 | `room_ca` | C.A. (wardrobe) | 4.0 m² | — | walk-in wardrobe, door from the bedroom |
| 7 | `room_wc1` | WC 1 | 6.9 m² | `master_bathroom` | confirmed master bath |
| 8 | `room_wc2` | WC 2 | 4.9 m² | — | plan label |
| 9 | `room_rip` | RIP (storage) | 1.4 m² | — | plan has `RIP` |

HA currently has five areas: `bedroom`, `studio`, `master_bathroom` on
floor **Main** (level 5), plus `kitchen` and `living_room` unassigned;
the **Upstairs** floor (level 6) has no areas.

## Balconies and doors

Two balconies are modelled on the north wall:

| Balcony | Plan span | Doors | Objects |
|---|---|---|---|
| Kitchen | x 350–515 px | 2 full-height glass doors | `balcony_kitchen_*`, `wall_sims_glass_*` |
| Living room | x 600–760 px | 2 full-height glass doors | `balcony_living_*`, `wall_sims_glass_*` |

Each balcony is a stone slab with a glass parapet and dark handrail. The
glass door panes run from **5 cm to 285 cm**; in `sims` mode the near
pane shows its 5–20 cm part and the high part hides; far panes stay full.
No door leaves, frames or handles are modelled yet, and the two door
contacts are **not bound**:

- `binary_sensor.entrance_door_contact`
- `binary_sensor.balcone_lato_cucina_contact`

## Lights

| # | Entity | Object ID | Placement |
|---|---|---|---|
| L1 | `light.living_room_ball_lamp` | `light_living_room_ball_lamp` | Living room ceiling |
| L2 | `light.bedroom_ceiling_bulbs` | `light_bedroom_ceiling_bulbs` | Left bedroom ceiling |
| L3 | `light.bedside_lamp` | `light_bedside_lamp` | Left bedroom, nightstand, 0.62 m |
| L4 | `light.mood_lights` | `light_mood_lights` | Left bedroom ceiling |
| L5 | `light.pc_keyboard_led_strip` | `light_pc_keyboard_led_strip` | Right studio desk, 0.8 m |

`light.bedroom_ceiling_bulbs` was `unavailable` when last checked; the
card will show the lamp off until the entity is available.

## Card behaviour

- `walls: sims` — see [How `walls: sims` works](#how-walls-sims-works).
- `camera_position (0, 1500, 850)` and `camera_target (0, 150, 0)` in
  centimetres, relative to the card's centred model.
- `zoom_areas` menu: Whole home, Bedroom, Studio, Kitchen, Living room,
  Master bath.
- No ceilings, so the model reads as a dollhouse from above.

## Local development (LAN only)

For faster iteration when the browser and this machine are on the same
LAN, switch the card `path` back to `http://192.168.1.4:8765/`; keep
`objfile` and `mtlfile` as plain names:

```bash
cd /home/simo/floor3d-starter
python3 serve.py          # 0.0.0.0:8765, CORS enabled
```

Check it before debugging:

```sh
ss -ltnp | grep 8765
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/home.obj
```

The custom card JS still comes from jsDelivr; only the model path changes
for local iteration. This server is not reachable from outside the LAN.

## Optional permanent HA-local copy

If you later want the model served by Home Assistant itself:

1. Create `/config/www/floor3d/`.
2. Upload `home.obj` and `home.mtl` into it.
3. Set `path: /local/floor3d/`.
4. Hard-refresh (Ctrl+Shift+R). The card caches OBJ/MTL.

You can also copy `custom-card/` to `/config/www/floor3d-card-sims/` and
register `/local/floor3d-card-sims/floor3d-card.js` as the module
resource instead of jsDelivr. Neither is required for remote use.

## Regenerate

Edit the tables at the top of `make_home.py`:

- `SCALE` — plan pixels per metre. If you change it, scale
  `camera_position`, `camera_target` and the `zoom_areas` distances by
  `new_scale / 70`.
- `ROOMS` — plan polygon, name, floor material.
- `WALLS` — endpoints in metres via `P(px, py)`, thickness, openings
  (`window`, `door`, `balcony`).
- `LIGHTS` / `LIGHT_ROOMS` — lamp positions and rooms.
- `FURNITURE` — object boxes.
- `BALCONIES` — slab span and depth; the two names are
  `balcony_kitchen` (x 350–515) and `balcony_living` (x 600–760).
- `SIMS_H` — the low-stub height (0.20 m). The wall split is baked into
  the OBJ, so changing it needs a regeneration and a new model commit.

Then regenerate and publish (see above). The generator writes
`home.obj`, `home.mtl`, `home.svg`, `card.yaml` and `manifest.json`.

## Known limitations

- Scale is assumed, not measured; 70 px/m is kept for now. One real
  dimension is enough to rescale every object later.
- The central Kitchen (west) / Living room (east) split is still
  assumed; the left/right rooms and WC 1 are confirmed.
- Window positions/counts and door openings are approximate traces of
  the photo, not measured joinery.
- Balcony doors are glass panes, not hinged leaves; no frames or
  handles. Near glass is cut at 20 cm with its wall.
- The main stairwell is outside the apartment and not modelled.
- The custom `sims` card is a fork of floor3d-card v2.13.2; HACS updates
  to the base card do not automatically update it. The source patch is in
  `custom-card/`.
- The wall split doubles the wall objects (low + high) and therefore the
  OBJ size; the effect is still cheap at runtime because it only toggles
  `visible`.

## Next inputs needed

1. Optional: one real dimension, or overall width/depth, if you want to
   replace the 70 px/m placeholder later.
2. Confirmation of the central Kitchen / Living room split.
3. Whether to model hinged balcony/entrance door leaves and bind
   `binary_sensor.balcone_lato_cucina_contact` and
   `binary_sensor.entrance_door_contact`.

## Security note

The GitHub repo is public, so the model is readable by anyone. The git
remote on this machine embeds a token in its URL; since the repo is
public, consider switching to a tokenless remote with a credential
helper and rotating that token.
