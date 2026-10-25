# floor3d-card development

A Three.js 3D model of the apartment, shown in a Home Assistant dashboard.

## How the model reaches Home Assistant

The dashboard loads the model **from the public GitHub repo** through
`raw.githubusercontent.com`, so it works off the LAN:

- Dashboard: `home-3d` (storage mode), card
  **`custom:floor3d-card-sims`** with
  `path: https://raw.githubusercontent.com/c0pper/homeassistant-3d-card/0b3b367/`.
- Card model files: `objfile: home.obj`, `mtlfile: home.mtl`.
  The path is **pinned to the commit that contains the model**. Raw
  GitHub caches a branch for ~5 minutes and a `?v=` query does not
  reliably bypass it (tested); a commit-SHA URL is immutable and served
  immediately. Update the path to the new SHA after each model push.
- The custom card JS is a second module resource, served by jsDelivr:
  `https://cdn.jsdelivr.net/gh/c0pper/homeassistant-3d-card@0209251/custom-card/floor3d-card.js`.
  It registers `floor3d-card-sims`; the HACS `floor3d-card` resource
  stays installed and shares its editor. Raw GitHub serves `.js` as
  `text/plain`, which browsers reject for modules, hence jsDelivr.
- GitHub raw sends `Access-Control-Allow-Origin: *`; the browser (not
  Home Assistant) fetches the OBJ/MTL, so the device showing the
  dashboard needs internet access. No HA token is involved.
- The repo is public, so the model/layout is public. Do not commit
  secrets or personal data.

After changing `make_home.py` and regenerating, **commit and push**;
otherwise the dashboard keeps the old model:

```sh
.venv/bin/python make_home.py
git add home.obj home.mtl home.svg home_preview.png card.yaml manifest.json make_home.py README.md AGENTS.md floor3d-model.zip
git commit -m "Describe the model change"
git push origin master
```

Then update the card path in `card.yaml` and the dashboard to the new
commit:

```sh
git rev-parse --short HEAD
# path: https://raw.githubusercontent.com/c0pper/homeassistant-3d-card/<sha>/
```

The current model commit is `0b3b367`; the custom card commit is `0209251`. `objfile` and `mtlfile` stay
plain names.

If `custom-card/` changes, rebuild it with the instructions in
`custom-card/README.md`, commit the new `custom-card/` files, and update
the dashboard resource URL to the new jsDelivr commit.

### Local development fallback

When the browser and this machine are on the same LAN, you can switch
the card back to the local server for immediate reloads:

- `path: http://192.168.1.4:8765/`, no `?v=` query.
- `serve.py` serves the folder on port 8765 with
  `Access-Control-Allow-Origin: *` and `Cache-Control: no-store`.

Check the server before debugging:

```sh
ss -ltnp | grep 8765          # is it listening?
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/home.obj
python3 serve.py              # restart it if the port is dead
```

The local server is not reachable from outside the LAN. The optional
permanent setup (`/config/www/floor3d/`, `path: /local/floor3d/`) is an
end-of-project alternative, not the current workflow.

### Walls

The card uses the custom **`walls: sims`** mode: every wall solid is
split in the model at **20 cm** into a closed `wall_sims_low_*` stub and
a `wall_sims_high_*` upper part. The custom card hides the high part of
walls whose outward side faces the camera (the same `normal · camera_side
> 0.3` rule as `fade`); far walls keep both parts. Near glass is split as
`wall_sims_glass_low_*` / `wall_sims_glass_high_*` and hides with its
wall. The change is a snap. Straight above, no wall is near, so all stay
full. Non-wall objects (wardrobe, lamps, balcony rails) stay full.

The HACS card still supports `walls: none/fade/low`; `low` cuts every
object matching `wall_*` at `walls_height`, which is why the split names
still start with `wall_`.

The custom build lives in `custom-card/` (patched v2.13.2, MIT); the
source patch is `custom-card/floor3d-card-sims.patch`. It registers a
separate element, `floor3d-card-sims`, so it can be loaded beside the
HACS card without a duplicate definition.

## Generating the model

`make_home.py` is the generator. It builds `home.obj`, `home.mtl`, `home.svg`, `card.yaml`, and `manifest.json` from `floorplan.jpg`. Edit `ROOMS` / `WALLS`, `BALCONIES` for the two north slabs (`balcony_kitchen` x 350–515, `balcony_living` x 600–760), and `SIMS_H` for the 20 cm wall split, then re-run it.

`make_model_starter_OLD.py` is the legacy 5-room placeholder. Running it overwrites the real model with a simplified one and empties the dashboard card.

The dashboard card binds entities to `object_id` values (`floor_base`, `room_left`, `room_kitchen`, `room_living`, `room_corridor`, `room_right`, `room_ca`, `room_wc1`, `room_wc2`, `room_rip`, plus lights). Renaming an object in `make_home.py` breaks the matching binding and zoom area, so update `card.yaml` and the dashboard in the same change.

## Lighting

The card follows the real sun: `sun: 'yes'` with `sun_power`, a `sky_power` fill, `backgroundColor: sky`, and `shadow: 'yes'`. Daylight, colour and shadows therefore come from `sun.sun` and need no scheduling.

Torch brightness is `globalLightPower: sensor.floor3d_ambient_power`, a Home Assistant template helper that interpolates 0.75 at night to 0.25 by day from the sun's elevation. Rename or delete that helper and the model goes dark. Overall brightness is `exposure`; the GPU limit is 14 shadow-casting lights (5 lamps + the sun here).

## Home Assistant access

Dashboard config is read and written through the `ha-mcp` tools (`ha_config_get_dashboard`, `ha_config_set_dashboard`) with `url_path: home-3d`. Home Assistant itself runs on `192.168.1.144`; its config folder is not mounted on this machine.

## Vocabulary

`GLOSSARY.md` fixes the shared terms for rooms, walls, windows, balconies, doors, furniture placement, and naming. Read it before naming a new room or object. Decisions with lasting consequences live in `docs/adr/`.
