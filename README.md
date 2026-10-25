# Home 3D — floor-plan model

Three.js model of the supplied floor plan, built for the HACS card
`giosci1994/floor3d-card` (v2.13.2) and displayed full-screen on the
Home Assistant dashboard **Home 3D** (`home-3d`).

## Current status

- Model regenerated from `floorplan.jpg`: outer footprint, slanted top
  wall, rooms, windows, door openings, straight stair, furniture and five
  lamp objects.
- Dashboard **Home 3D** is live against the temporary CORS preview at
  `http://192.168.1.4:8765/` (served by `serve.py`).
- The model is **not yet copied** to `/config/www/floor3d/`; see
  [Make it permanent](#make-it-permanent).
- Absolute scale is still a placeholder: the plan has no printed
  dimensions, so `SCALE = 70 px/m` is kept. Overall footprint is
  **14.6 × 10.6 m**. The OBJ is exported in **centimetres** because
  floor3d-card's lights, camera and zoom distances use cm.
- Room mapping is now confirmed by the user: **left = Bedroom**,
  **right = Studio**, **WC 1 = Master bathroom**. Only the split of the
  central area into Kitchen (west) and Living room (east) is still an
  assumption, marked **\*** in the legend.

## Files

| File | Purpose |
|---|---|
| `home.obj`, `home.mtl` | Model + materials. Put these in `/config/www/floor3d/`. |
| `home.svg`, `home_preview.png` | Numbered top-view preview and room/light legend. |
| `card.yaml` | Card config for the permanent `/local/floor3d/` location. |
| `manifest.json` | Object IDs, room numbers, areas, HA areas, light mapping. |
| `make_home.py` | **The real generator** — builds the model from `floorplan.jpg`. Edit the tables at the top and re-run. |
| `serve.py` | Temporary CORS static server on port 8765. |
| `floorplan.jpg` / `.png` | Source floor plan. |
| `make_model_starter_OLD.py` | Legacy placeholder starter (5 rooms). **Do not run** — it overwrites `home.obj`/`home.mtl`/`home.svg` with a simplified model and breaks the card. |

## Room mapping

Numbers match `home.svg`.

| # | Object ID | Name | Area | HA area | Confidence |
|---|---|---|---|---|---|
| 1 | `room_left` | Bedroom | 9.4 m² | `bedroom` | confirmed (left) |
| 2 | `room_kitchen` | Kitchen | 14.0 m² | `kitchen` | plan has `K` |
| 3 | `room_living` | Living room \* | 18.4 m² | `living_room` | central-east split assumed |
| 4 | `room_corridor` | Corridor | 10.3 m² | — | plan has `CORRIDOIO` |
| 5 | `room_right` | Studio | 18.1 m² | `studio` | confirmed (right) |
| 6 | `room_ca` | C.A. (wardrobe) | 4.0 m² | — | plan label; walk-in wardrobe, door from the bedroom |
| 7 | `room_wc1` | WC 1 | 6.9 m² | `master_bathroom` | confirmed master bath |
| 8 | `room_wc2` | WC 2 | 4.9 m² | — | plan label |
| 9 | `room_rip` | RIP (storage) | 2.8 m² | — | plan has `RIP` |

HA currently has five areas: `bedroom`, `studio`, `master_bathroom` on
floor **Main** (level 5), plus `kitchen` and `living_room` unassigned;
the **Upstairs** floor (level 6) has no areas. Only areas relevant to
this floor are mapped above; corridors and closets have no HA area.
The common stairwell lies outside the apartment and is not modelled.

## Lights

| # | Entity | Object ID | Placement |
|---|---|---|---|
| L1 | `light.living_room_ball_lamp` | `light_living_room_ball_lamp` | Living room ceiling |
| L2 | `light.bedroom_ceiling_bulbs` | `light_bedroom_ceiling_bulbs` | Left bedroom ceiling |
| L3 | `light.bedside_lamp` | `light_bedside_lamp` | Left bedroom, nightstand, 0.62 m |
| L4 | `light.mood_lights` | `light_mood_lights` | Left bedroom ceiling |
| L5 | `light.pc_keyboard_led_strip` | `light_pc_keyboard_led_strip` | Right studio desk, 0.8 m |

`light.bedroom_ceiling_bulbs` was `unavailable` when last checked; the
card will show the lamp off until the entity is available. Door contacts
were removed from the card because the new plan has no confirmed door
leaf objects. The old bindings were
`binary_sensor.entrance_door_contact` and
`binary_sensor.balcone_lato_cucina_contact`.

## Make it permanent

The dashboard currently points at the temporary preview server. To move
the model onto HA:

1. Open **Studio Code Server** (or Samba / File editor).
2. Create `/config/www/floor3d/`.
3. Upload `home.obj` and `home.mtl` into it.
4. In dashboard `home-3d`, change the card `path` from
   `http://192.168.1.4:8765/` to `/local/floor3d/`.
   `card.yaml` already has the permanent value.
5. Hard-refresh the browser (Ctrl+Shift+R). The card caches OBJ/MTL.
6. The preview server can then be stopped.

Temporary server (keep it running until step 4):

```bash
cd /home/simo/floor3d-starter
python3 serve.py          # 0.0.0.0:8765, CORS enabled
```

## Regenerate

Edit the tables at the top of `make_home.py`:

- `SCALE` — plan pixels per metre (the one value to change when a real
  dimension arrives). If you change it, scale `camera_position`,
  `camera_target` and the `zoom_areas` distances by `new_scale / 70` so
  the initial view stays framed the same way.
- `ROOMS` — plan polygon, name, floor material.
- `WALLS` — endpoints in metres via `P(px, py)`, thickness, openings.
- `LIGHTS` / `LIGHT_ROOMS` — lamp positions and rooms.
- `FURNITURE` — object boxes.

Then:

```bash
cd /home/simo/floor3d-starter
.venv/bin/python make_home.py
.venv/bin/python - <<'PY'
import cairosvg
cairosvg.svg2png(url='home.svg', write_to='home_preview.png', output_width=1600)
PY
```

The generator writes `home.obj`, `home.mtl`, `home.svg`, `card.yaml` and
`manifest.json`. Re-upload the OBJ/MTL after changes.

## Card behaviour

- `walls: fade` with `walls_opacity: 0.18` — near walls fade so the
  rooms stay visible; wall objects are named `wall_*`.
- `camera_position (0, 1500, 850)` and `camera_target (0, 150, 0)` in
  centimetres, relative to the card's centred model.
- `zoom_areas` menu: Whole home, Bedroom, Studio, Kitchen, Living room,
  Master bath.
- No ceilings, so the model reads as a dollhouse from above.
- Wall height 2.9 m; exterior walls 0.28–0.79 m thick (the south spine
  is thick on the plan); interior walls 0.14 m.

## Known limitations

- Scale is assumed, not measured; you chose to keep 70 px/m for now.
  One real dimension (overall width, a room, or a door) is enough to
  rescale every object later.
- The left/right rooms and WC 1 are confirmed; only the central
  Kitchen (west) / Living room (east) split is still assumed.
- Window positions/counts and door openings are approximate traces of
  the photo, not measured joinery.
- The stair is a simplified straight flight; the plan's stair/landing
  geometry is more complex.
- Door leaves are omitted; the openings are empty so rooms remain
  visible. Add static leaves or bind the two contacts once the entrance
  and kitchen-balcony doors are identified.
- The upper floor (HA floor `Upstairs`) is not modelled.

## Next inputs needed

1. Optional: one real dimension, or overall width/depth, if you want to
   replace the 70 px/m placeholder later.
2. Confirmation of the central Kitchen / Living room split (the `K`
   labels support Kitchen in the west half).
3. Whether the kitchen balcony door and entrance door should be modelled
   and bound to `binary_sensor.balcone_lato_cucina_contact` and
   `binary_sensor.entrance_door_contact`.
