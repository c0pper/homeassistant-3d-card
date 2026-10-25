# Serve the model from GitHub raw and cut walls low

> **Partially superseded by ADR 0003.** The remote-hosting decision below
> still stands; the `walls: low` part is replaced by the custom
> `walls: sims` mode. The model commit is `fb54b9a`; the custom card commit is `1860ac9`.

The model used to be loaded from a temporary CORS server on the
development machine (`http://192.168.1.4:8765/`). That only works when
the browser showing the dashboard is on the same LAN. The model is also
committed to the public repo `c0pper/homeassistant-3d-card`, which GitHub
serves with `Access-Control-Allow-Origin: *`.

We therefore load the model from GitHub raw and pin the card `path` to
the **commit that contains the model**:

```yaml
path: https://raw.githubusercontent.com/c0pper/homeassistant-3d-card/15dd34b/
objfile: home.obj
mtlfile: home.mtl
```

Raw GitHub caches a branch for about five minutes and a `?v=` query does
not reliably bypass that cache (tested). A commit-SHA URL is immutable
and available immediately. The trade-off is that every model change
needs the path updated to the new commit.

At the same time the card uses `walls: low` with
`walls_height: 100` (cm): every object matching `wall_*` is clipped at
1 m above the floor. Window and balcony glass objects are named
`wall_glass_*` so that the clipping applies to them too; otherwise they
would float above the cut walls.

**Consequences**

- The dashboard works off-LAN and needs no Home Assistant file copy or
  HA token. The browser must be able to reach GitHub.
- The repo is public, so the model and floor plan are public.
- After a model change: regenerate, commit, push, then update the
  dashboard/`card.yaml` path to the new commit SHA.
- `walls: low` hides wall detail above 1 m and leaves tall non-wall
  objects (wardrobe, lamps) above the cut. That is the intended
  doll's-house look. Use `fade` or `none` if full walls are needed.
- The optional HA-local `/config/www/floor3d/` copy remains available
  but is no longer required.

Related: `AGENTS.md` (workflow), `README.md` (current URLs and
publishing steps), `GLOSSARY.md` (balcony and glass names).
