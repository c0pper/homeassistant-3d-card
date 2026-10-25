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
- The dashboard now loads the model from the **public GitHub repo** via
  `raw.githubusercontent.com`, so it works when Home Assistant or the
  browser is **off the LAN**. The local preview server is only for
  development.
- Walls use **`walls: low`**, cut at **100 cm** above the floor, as a
  doll's house. This replaced the orientation-based `fade` mode.
- Absolute scale is still a placeholder: the plan has no printed
  dimensions, so `SCALE = 70 px/m` is kept. Overall footprint is
  **14.6 × 10.6 m**. The OBJ is exported in **centimetres** because
  floor3d-card's lights, camera and zoom distances use cm.
- Room mapping is confirmed: **left = Bedroom**, **right = Studio**,
  **WC 1 = Master bathroom**. Only the split of the central area into
  Kitchen (west) and Living room (east) is still an assumption, marked
  **\*** in the legend.

## Files

| File | Purpose |
|---|---|
| `home.obj`, `home.mtl` | Model + materials. These are the files the card fetches. |
| `home.svg`, `home_preview.png` | Numbered top-view preview and room/light legend. |
| `card.yaml` | Current card config: GitHub raw path, `walls: low`, camera and zoom areas. |
| `manifest.json` | Object IDs, room numbers, areas, HA areas, light mapping. |
| `make_home.py` | **The real generator** — builds the model from `floorplan.jpg`. Edit the tables at the top and re-run. |
| `serve.py` | Local CORS server on port 8765, for LAN development only. |
| `floorplan.jpg` / `.png` | Source floor plan. |
| `make_model_starter_OLD.py` | Legacy placeholder starter (5 rooms). **Do not run** — it overwrites the real model with a simplified one. |
| `floor3d-model.zip` | Handy package of the model, preview, card and notes. |

## How the card fetches the model now

The repo is public: `c0pper/homeassistant-3d-card`. GitHub raw serves
the files with `Access-Control-Allow-Origin: *`, which the card needs.

```yaml
path: https://raw.githubusercontent.com/c0pper/homeassistant-3d-card/master/
objfile: home.obj?v=2026-10-25-low
mtlfile: home.mtl?v=2026-10-25-low
```

- The card appends `objfile` / `mtlfile` to `path`, so the actual URLs are
  `.../master/home.obj?v=...` and `.../master/home.mtl?v=...`.
- The `?v=` query is a cache-buster. Raw GitHub caches for about five
  minutes; changing the version makes the browser and CDN fetch the new
  file. The card explicitly handles a `?` in `objfile`
  (`fileExt = objfile.split('?')[0]...`).
- The model is loaded in the **browser**, not by Home Assistant, so the
  device showing the dashboard must be able to reach GitHub. Public
  GitHub is normally reachable; no token is needed.
- Because the repo is public, the floor-plan model is public too. Do not
  put secrets or personal data in the model or repo.

### Publishing a model change

After editing `make_home.py` and regenerating:

```bash
cd /home/simo/floor3d-starter
.venv/bin/python make_home.py
.venv/bin/python - <<'PY'
import cairosvg
cairosvg.svg2png(url='home.svg', write_to='home_preview.png', output_width=1600)
PY
git add home.obj home.mtl home.svg card.yaml manifest.json \
        make_home.py README.md AGENTS.md floor3d-model.zip
git commit -m "Describe the model change"
git push origin master
```

Then bump the `?v=` value in `card.yaml` and in the dashboard card
(`objfile` and `mtlfile`) so the browser does not keep the old OBJ/MTL.
The current value is **`2026-10-25-low`**.

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
| Kitchen | x 350–515 px | 2 full-height glass doors | `balcony_kitchen_*`, `wall_glass_balcony_*` |
| Living room | x 600–760 px | 2 full-height glass doors | `balcony_living_*`, `wall_glass_balcony_*` |

Each balcony is a stone slab with a glass parapet and dark handrail. The
glass door panes run from **5 cm to 285 cm**; with `walls: low` the card
clips them together with the walls at 100 cm. No door leaves, frames or
handles are modelled yet, and the two door contacts are **not bound**:

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

- `walls: low` with `walls_height: 100` (cm). All objects matching
  `wall_*` are clipped at 1 m above the floor; windows and balcony glass
  are named `wall_glass_*` so they are clipped too. Objects that are not
  walls (stairs, wardrobe, lamps) stay at full height.
- `camera_position (0, 1500, 850)` and `camera_target (0, 150, 0)` in
  centimetres, relative to the card's centred model.
- `zoom_areas` menu: Whole home, Bedroom, Studio, Kitchen, Living room,
  Master bath.
- No ceilings, so the model reads as a dollhouse from above.

## Local development (LAN only)

For faster iteration when the browser and this machine are on the same
LAN, switch the card `path` back to `http://192.168.1.4:8765/` and drop
the `?v=` query from `objfile`/`mtlfile`:

```bash
cd /home/simo/floor3d-starter
python3 serve.py          # 0.0.0.0:8765, CORS enabled
```

Check it before debugging:

```sh
ss -ltnp | grep 8765
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/home.obj
```

This server is not reachable from outside the LAN. If the model
disappears while you are remote, check the GitHub raw URL instead.

## Optional permanent HA-local copy

If you later want the model served by Home Assistant itself:

1. Create `/config/www/floor3d/`.
2. Upload `home.obj` and `home.mtl` into it.
3. Set `path: /local/floor3d/` and remove the `?v=` queries.
4. Hard-refresh (Ctrl+Shift+R). The card caches OBJ/MTL.

This is no longer required for remote use; the GitHub raw path works
off-LAN.

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

Then regenerate and publish (see above). The generator writes
`home.obj`, `home.mtl`, `home.svg`, `card.yaml` and `manifest.json`.

## Known limitations

- Scale is assumed, not measured; you chose to keep 70 px/m for now.
  One real dimension is enough to rescale every object later.
- The central Kitchen (west) / Living room (east) split is still
  assumed; the left/right rooms and WC 1 are confirmed.
- Window positions/counts and door openings are approximate traces of
  the photo, not measured joinery.
- Balcony doors are glass panes, not hinged leaves; no frames or
  handles. With `low` walls they are clipped at 1 m.
- The main stairwell is outside the apartment and not modelled.
- With `low`, tall non-wall objects (wardrobe 2.1 m, lamps at 2.55 m)
  remain above the cut. That is expected; the card only clips walls.

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
