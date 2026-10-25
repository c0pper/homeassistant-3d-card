# floor3d-card sims build

A small build of [`giosci1994/floor3d-card`](https://github.com/giosci1994/floor3d-card)
v2.13.2 (tag commit `41e1272`, MIT) with one added wall mode:

```yaml
walls: sims
```

The normal card only has `none`, `fade` and `low`. `sims` shows **near
walls as a closed 20 cm stub and far walls at full height**, based on the
same facing rule as `fade`:

- Each wall in the model is split at 20 cm into `wall_sims_low_*` (the
  closed stub) and `wall_sims_high_*` (the rest).
- A wall is near when its outward side faces the camera
  (`normal · camera_side > 0.3`); its high part is hidden. Far walls show
  both parts. Straight above, no wall is near, so all walls stay full.
- Near window/balcony glass is split too (`wall_sims_glass_low_*` /
  `wall_sims_glass_high_*`); its high part is hidden with the wall.
- The low part is a closed prism, so the stub has a solid top, not a
  hollow clipping edge.
- The change is a snap, not an animation.

This build registers **`floor3d-card-sims`**, not `floor3d-card`, so it can
be loaded beside the HACS card. Use it as:

```yaml
type: custom:floor3d-card-sims
walls: sims
```

The HACS `floor3d-card` resource stays installed; the card editor is
shared (`floor3d-card-editor`).

## Hosting

The built files in this folder are loaded as a module resource. Raw
GitHub serves `.js` as `text/plain`, which browsers reject for modules;
use jsDelivr with the commit that contains this folder:

```yaml
# dashboard resource, type module
https://cdn.jsdelivr.net/gh/c0pper/homeassistant-3d-card@0209251/custom-card/floor3d-card.js
```

The entry imports `./floor3d-card-core-<hash>.js` and the editor chunk
from the same folder; keep all files in `custom-card/` together.

## Rebuild

The patch `floor3d-card-sims.patch` is relative to v2.13.2:

```sh
git clone --depth 1 --branch v2.13.2 https://github.com/giosci1994/floor3d-card.git
cd floor3d-card
git apply /path/to/custom-card/floor3d-card-sims.patch
npm install
npm run build
```

Then copy `dist/*` here. The card version string is
`v2.13.2-sims.1`.

## Upstream

The change is small and could be proposed upstream as a `walls: sims`
mode. Until then this build is independent of HACS updates.
