# floor3d-card development

A Three.js 3D model of the apartment, shown in a Home Assistant dashboard.

## How the model reaches Home Assistant

During development the card loads the model **over HTTP from this machine** — nothing is copied into Home Assistant.

- Dashboard: `home-3d` (storage mode), card `custom:floor3d-card` with `path: http://192.168.1.4:8765/`.
- Server: `serve.py` in this repo serves the folder on port 8765 with `Access-Control-Allow-Origin: *` and `Cache-Control: no-store`.
- Regenerate a model file, reload the dashboard, and the new geometry appears. No upload, no cache busting.

Check the server before debugging the card:

```sh
ss -ltnp | grep 8765          # is it listening?
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8765/home.obj
python3 serve.py              # restart it if the port is dead
```

If this machine is off or `serve.py` has died, the dashboard shows an empty scene. That is the usual cause of "the model disappeared".

The permanent setup (`/config/www/floor3d/`, `path: /local/floor3d/`) is a deliberate end-of-project step, not the current workflow.

## Generating the model

`make_home.py` is the generator. It builds `home.obj`, `home.mtl`, `home.svg`, `card.yaml`, and `manifest.json` from `floorplan.jpg`. Edit the `ROOMS` / `WALLS` tables at the top, then re-run it.

`make_model_starter_OLD.py` is the legacy 5-room placeholder. Running it overwrites the real model with a simplified one and empties the dashboard card.

The dashboard card binds entities to `object_id` values (`floor_base`, `room_left`, `room_kitchen`, `room_living`, `room_corridor`, `room_right`, `room_ca`, `room_wc1`, `room_wc2`, `room_stairs`, `room_rip`, plus lights). Renaming an object in `make_home.py` breaks the matching binding and zoom area, so update `card.yaml` and the dashboard in the same change.

## Home Assistant access

Dashboard config is read and written through the `ha-mcp` tools (`ha_config_get_dashboard`, `ha_config_set_dashboard`) with `url_path: home-3d`. Home Assistant itself runs on `192.168.1.144`; its config folder is not mounted on this machine.

## Vocabulary

`GLOSSARY.md` fixes the shared terms for rooms, walls, windows, balconies, doors, furniture placement, and naming. Read it before naming a new room or object. Decisions with lasting consequences live in `docs/adr/`.
