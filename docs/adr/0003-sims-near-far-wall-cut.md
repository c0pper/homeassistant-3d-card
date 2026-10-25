# Sims-style near/far wall cut

The dashboard needs walls near the camera cut low, with far walls full, so
orbiting the model does not hide the rooms. The stock floor3d-card only
supports:

- `walls: none` — full walls;
- `walls: fade` — near-facing walls become transparent;
- `walls: low` — every wall is clipped at one height.

None of these gives a solid low stub on the near side while keeping the
far side full. The `low` clipping also leaves an open-topped shell, which
looks hollow at 20 cm.

## Decision

- Add a small custom build of floor3d-card **v2.13.2** with a new
  `walls: sims` mode.
- Split every wall solid in the model at **20 cm**:
  `wall_sims_low_*` is a closed 0–20 cm prism (solid top);
  `wall_sims_high_*` is the rest.
- Split window/balcony glass the same way:
  `wall_sims_glass_low_*` / `wall_sims_glass_high_*`.
- The custom card hides the high part when the wall's outward side faces
  the camera, using the same `facing` normal and
  `normal · camera_side > 0.3` rule as `fade`. This applies to exterior
  and interior walls; at a corner both adjacent facades drop.
- Wall pieces are named `wall_sims_high_<wall line>_<piece>` and grouped
  by wall line. The longest piece's normal is used for the whole line,
  so short pieces between windows/balconies and corner pillars drop with
  their wall. A group with no usable normal falls back to the outward
  radial direction.
- A wall also drops when its horizontal distance to the camera is less
  than `walls_near_distance` (1.35) times the horizontal
  camera-to-target distance. This catches edge-on internal and side
  walls in a three-quarter view; it is configurable.
- The change is a **snap** (no animation).
- Straight above there is no horizontal camera side, so all walls stay
  full.
- Near glass hides its high part with the wall; far glass stays full.
- The custom card registers **`floor3d-card-sims`**, loaded as a second
  module resource, so the HACS `floor3d-card` stays installed and shares
  its editor.
- The card JS is served by jsDelivr with a commit-pinned path; raw GitHub
  serves `.js` as `text/plain`, which browsers reject for module
  resources. The model OBJ/MTL remains on raw GitHub.
- The model path is pinned to model commit `5b7ecaa`; the custom card
  resource is pinned to custom-card commit `e822865`.

## Consequences

- The dashboard works off-LAN and needs no HA file copy.
- The wall objects double (low + high), increasing the OBJ size; runtime
  cost is only a visibility toggle.
- The custom card is a fork and must be rebuilt when the base card is
  updated; the source patch and build notes live in `custom-card/`.
- The 20 cm split is baked into the model. Changing it requires editing
  `SIMS_H` in `make_home.py`, regenerating, and updating the model commit.
- Non-wall objects (wardrobe, lamps, balcony rails) stay full above the
  cut.
- The repo is public, so the model and the custom card build are public.

Related: `README.md`, `AGENTS.md`, `GLOSSARY.md`,
`custom-card/README.md`, and ADR 0002 (remote hosting).
