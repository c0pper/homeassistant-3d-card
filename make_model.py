#!/usr/bin/env python3
"""
Generate a starter 3D floor plan for the Home Assistant floor3d-card.

Outputs (next to this script):
  home.obj   - Wavefront OBJ, one named object per room floor / wall / lamp / door
  home.mtl   - materials
  home.svg   - top-view preview with room names and sizes
  card.yaml  - ready-to-paste Lovelace card config

All dimensions are metres. Edit ROOMS / WALLS / LIGHTS and re-run.
"""

import json
import math
import os
from pathlib import Path

OUT = Path(__file__).resolve().parent
WALL_H = 2.70
EXT_T = 0.20
INT_T = 0.12

# ---------------------------------------------------------------- rooms
ROOMS = [
    # id, label, x0, z0, x1, z1, floor material
    ("living_room",      "Living Room",      0.0, 0.0,  6.0, 4.6, "wood"),
    ("kitchen",          "Kitchen",          6.0, 0.0,  9.4, 3.2, "tile"),
    ("bedroom",          "Bedroom",          6.0, 3.2, 10.2, 7.0, "wood"),
    ("studio",           "Studio",           0.0, 4.6,  4.0, 7.6, "wood"),
    ("master_bathroom",  "Master bathroom",  4.0, 4.6,  6.0, 7.0, "tile"),
]

# ---------------------------------------------------------------- walls
# ("x", x, z0, z1, thickness, gaps) - wall runs along z at fixed x
# ("z", z, x0, x1, thickness, gaps) - wall runs along x at fixed z
# gaps = [(a, b), ...] door openings along the run
WALLS = [
    ("z", 0.0,  0.0,  9.4, EXT_T, [(1.20, 2.10)]),          # north, entrance
    ("x", 9.4,  0.0,  3.2, EXT_T, [(0.80, 2.00)]),          # kitchen east, balcony door
    ("z", 3.2,  9.4, 10.2, EXT_T, []),
    ("x", 10.2, 3.2,  7.0, EXT_T, []),                      # bedroom east
    ("z", 7.0,  4.0, 10.2, EXT_T, []),                      # south
    ("x", 4.0,  7.0,  7.6, EXT_T, []),
    ("z", 7.6,  0.0,  4.0, EXT_T, []),                      # studio south
    ("x", 0.0,  0.0,  7.6, EXT_T, []),                      # west
    ("x", 6.0,  0.0,  7.0, INT_T, [(1.00, 1.90), (5.20, 6.10)]),
    ("z", 4.6,  0.0,  6.0, INT_T, [(1.10, 2.00)]),
    ("z", 3.2,  6.0, 10.2, INT_T, [(6.90, 7.80)]),
    ("x", 4.0,  4.6,  7.0, INT_T, []),
]

# ---------------------------------------------------------------- objects
# name, x, y, z
LIGHTS = [
    ("light_living_room_ball_lamp",    3.00, 2.30, 2.30),
    ("light_mood_lights",              7.00, 2.40, 4.10),
    ("light_bedroom_ceiling_bulbs",    8.60, 2.50, 4.80),
    ("light_bedside_lamp",             8.90, 0.62, 6.40),
    ("light_pc_keyboard_led_strip",    2.00, 0.78, 6.75),
]

# name, x0, y0, z0, x1, y1, z1, material
FURNITURE = [
    ("furniture_sofa",        0.60, 0.00, 0.60, 2.90, 0.45, 1.45, "fabric"),
    ("furniture_sofa_back",   0.60, 0.45, 0.55, 2.90, 0.95, 0.82, "fabric"),
    ("furniture_dining_table", 3.20, 0.72, 2.60, 4.80, 0.78, 3.60, "wood"),
    ("furniture_dining_leg1", 3.28, 0.00, 2.68, 3.38, 0.72, 2.78, "dark"),
    ("furniture_dining_leg2", 4.62, 0.00, 2.68, 4.72, 0.72, 2.78, "dark"),
    ("furniture_dining_leg3", 3.28, 0.00, 3.42, 3.38, 0.72, 3.52, "dark"),
    ("furniture_dining_leg4", 4.62, 0.00, 3.42, 4.72, 0.72, 3.52, "dark"),
    ("furniture_bed",         7.40, 0.00, 4.80, 9.40, 0.55, 6.80, "fabric"),
    ("furniture_bed_head",    7.40, 0.00, 4.80, 9.40, 1.05, 5.02, "wood"),
    ("furniture_desk",        1.40, 0.72, 6.40, 2.90, 0.78, 7.05, "wood"),
    ("furniture_desk_leg1",   1.44, 0.00, 6.44, 1.54, 0.72, 6.54, "dark"),
    ("furniture_desk_leg2",   2.76, 0.00, 6.44, 2.86, 0.72, 6.54, "dark"),
    ("furniture_desk_leg3",   1.44, 0.00, 6.91, 1.54, 0.72, 7.01, "dark"),
    ("furniture_desk_leg4",   2.76, 0.00, 6.91, 2.86, 0.72, 7.01, "dark"),
    ("furniture_kitchen_counter", 6.30, 0.00, 0.20, 9.20, 0.90, 0.85, "counter"),
    ("furniture_kitchen_island",  6.60, 0.00, 1.60, 8.20, 0.92, 2.40, "counter"),
    ("furniture_bath_sink",   4.25, 0.00, 6.45, 5.15, 0.85, 6.90, "white"),
    ("furniture_bath_toilet", 5.35, 0.00, 6.40, 5.85, 0.75, 6.90, "white"),
]

# ---------------------------------------------------------------- materials
MATERIALS = {
    "wood":    (0.62, 0.45, 0.30),
    "tile":    (0.80, 0.82, 0.84),
    "wall":    (0.93, 0.93, 0.90),
    "fabric":  (0.35, 0.42, 0.55),
    "counter": (0.72, 0.73, 0.70),
    "white":   (0.90, 0.90, 0.88),
    "dark":    (0.22, 0.22, 0.24),
    "glass":   (0.55, 0.75, 0.85),
    "light":   (1.00, 0.93, 0.70),
}


class Obj:
    def __init__(self):
        self.lines = []
        self.verts = []
        self.norms = []
        self.vcount = 0
        self.ncount = 0

    def _v(self, x, y, z):
        self.verts.append((x, y, z))
        self.vcount += 1
        return self.vcount

    def _n(self, x, y, z):
        ln = math.sqrt(x * x + y * y + z * z) or 1.0
        self.norms.append((x / ln, y / ln, z / ln))
        self.ncount += 1
        return self.ncount

    def box(self, name, mat, x0, y0, z0, x1, y1, z1):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        z0, z1 = sorted((z0, z1))
        v = [
            self._v(x0, y0, z0), self._v(x1, y0, z0),
            self._v(x1, y0, z1), self._v(x0, y0, z1),
            self._v(x0, y1, z0), self._v(x1, y1, z0),
            self._v(x1, y1, z1), self._v(x0, y1, z1),
        ]
        self.lines.append(f"o {name}")
        self.lines.append(f"usemtl {mat}")
        # faces: (quad, outward normal)
        faces = [
            ((v[0], v[3], v[2], v[1]), (0, -1, 0)),
            ((v[4], v[7], v[6], v[5]), (0, 1, 0)),
            ((v[0], v[1], v[5], v[4]), (0, 0, -1)),
            ((v[3], v[2], v[6], v[7]), (0, 0, 1)),
            ((v[0], v[4], v[7], v[3]), (-1, 0, 0)),
            ((v[1], v[2], v[6], v[5]), (1, 0, 0)),
        ]
        for quad, nrm in faces:
            n = self._n(*nrm)
            idx = " ".join(f"{i}//{n}" for i in quad)
            self.lines.append(f"f {idx}")

    def sphere(self, name, mat, cx, cy, cz, r, slices=12, stacks=8):
        self.lines.append(f"o {name}")
        self.lines.append(f"usemtl {mat}")
        ring = []
        for i in range(stacks + 1):
            theta = math.pi * i / stacks
            row = []
            for j in range(slices):
                phi = 2 * math.pi * j / slices
                x = cx + r * math.sin(theta) * math.cos(phi)
                y = cy + r * math.cos(theta)
                z = cz + r * math.sin(theta) * math.sin(phi)
                row.append(self._v(x, y, z))
            ring.append(row)
        for i in range(stacks):
            for j in range(slices):
                j2 = (j + 1) % slices
                a, b = ring[i][j], ring[i][j2]
                c, d = ring[i + 1][j2], ring[i + 1][j]
                nx = (self.verts[a - 1][0] + self.verts[b - 1][0] + self.verts[c - 1][0]) / 3 - cx
                ny = (self.verts[a - 1][1] + self.verts[b - 1][1] + self.verts[c - 1][1]) / 3 - cy
                nz = (self.verts[a - 1][2] + self.verts[b - 1][2] + self.verts[c - 1][2]) / 3 - cz
                n = self._n(nx, ny, nz)
                self.lines.append(f"f {a}//{n} {b}//{n} {c}//{n} {d}//{n}")

    def write(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("# starter home model for floor3d-card\n")
            fh.write("mtllib home.mtl\n")
            for v in self.verts:
                fh.write("v %.4f %.4f %.4f\n" % v)
            for n in self.norms:
                fh.write("vn %.4f %.4f %.4f\n" % n)
            fh.write("\n".join(self.lines))
            fh.write("\n")


def segments(start, end, gaps):
    """Split [start, end] around gaps, return list of (a, b)."""
    out = []
    cur = start
    for a, b in sorted(gaps):
        a, b = max(a, start), min(b, end)
        if a > cur:
            out.append((cur, a))
        cur = max(cur, b)
    if cur < end:
        out.append((cur, end))
    return out


def build():
    obj = Obj()

    for rid, label, x0, z0, x1, z1, mat in ROOMS:
        obj.box(f"room_{rid}", "wood" if mat == "wood" else "tile",
                x0, -0.06, z0, x1, 0.0, z1)

    for axis, coord, a, b, t, gaps in WALLS:
        for s, e in segments(a, b, gaps):
            if e - s < 0.01:
                continue
            if axis == "x":
                name = f"wall_x{coord:.1f}_z{s:.2f}_{e:.2f}".replace(".", "_")
                obj.box(name, "wall", coord - t / 2, 0.0, s,
                        coord + t / 2, WALL_H, e)
            else:
                name = f"wall_z{coord:.1f}_x{s:.2f}_{e:.2f}".replace(".", "_")
                obj.box(name, "wall", s, 0.0, coord - t / 2,
                        e, WALL_H, coord + t / 2)

    # door leaf in the entrance opening (hinged at x=1.20)
    obj.box("door_entrance", "dark", 1.20, 0.02, -0.02, 2.10, 2.05, 0.02)
    # balcony door leaf in the kitchen east opening
    obj.box("door_balcony", "glass", 9.36, 0.02, 0.80, 9.40, 2.20, 2.00)

    for name, x, y, z in LIGHTS:
        obj.sphere(name, "light", x, y, z, 0.10)

    for rec in FURNITURE:
        name, x0, y0, z0, x1, y1, z1, mat = rec
        obj.box(name, mat, x0, y0, z0, x1, y1, z1)

    obj.write(OUT / "home.obj")

    with open(OUT / "home.mtl", "w", encoding="utf-8") as fh:
        fh.write("# starter home model materials\n")
        for name, (r, g, b) in MATERIALS.items():
            fh.write(f"newmtl {name}\n")
            fh.write(f"Kd {r:.3f} {g:.3f} {b:.3f}\n")
            fh.write("Ka 0.05 0.05 0.05\nKs 0.10 0.10 0.10\nNs 20\n")
            if name == "light":
                fh.write("Ke 0.90 0.80 0.50\n")
            if name == "glass":
                fh.write("d 0.35\n")
            fh.write("\n")

    return obj


def preview():
    """Top-view SVG preview."""
    s = 64.0
    pad = 34
    minx = min(r[2] for r in ROOMS)
    maxx = max(r[4] for r in ROOMS)
    minz = min(r[3] for r in ROOMS)
    maxz = max(r[5] for r in ROOMS)
    w = int((maxx - minx) * s + pad * 2)
    h = int((maxz - minz) * s + pad * 2 + 18)

    def X(x):
        return pad + (x - minx) * s

    def Z(z):
        return pad + (z - minz) * s

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="system-ui, sans-serif">',
        f'<rect width="100%" height="100%" fill="#0f172a"/>',
    ]
    colors = {"wood": "#5b4430", "tile": "#3b4a55"}
    for rid, label, x0, z0, x1, z1, mat in ROOMS:
        parts.append(
            f'<rect x="{X(x0)}" y="{Z(z0)}" width="{(x1-x0)*s}" height="{(z1-z0)*s}" '
            f'fill="{colors[mat]}" stroke="#8ea0b5" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{X((x0+x1)/2)}" y="{Z((z0+z1)/2)-4}" fill="#f1f5f9" '
            f'font-size="13" font-weight="600" text-anchor="middle">{label}</text>'
        )
        parts.append(
            f'<text x="{X((x0+x1)/2)}" y="{Z((z0+z1)/2)+13}" fill="#94a3b8" '
            f'font-size="10" text-anchor="middle">{x1-x0:.1f} x {z1-z0:.1f} m</text>'
        )
    for axis, coord, a, b, t, gaps in WALLS:
        for seg_a, seg_b in segments(a, b, gaps):
            if axis == "x":
                parts.append(
                    f'<line x1="{X(coord)}" y1="{Z(seg_a)}" x2="{X(coord)}" y2="{Z(seg_b)}" '
                    f'stroke="#e2e8f0" stroke-width="{max(3, t*s)}" stroke-linecap="butt"/>'
                )
            else:
                parts.append(
                    f'<line x1="{X(seg_a)}" y1="{Z(coord)}" x2="{X(seg_b)}" y2="{Z(coord)}" '
                    f'stroke="#e2e8f0" stroke-width="{max(3, t*s)}" stroke-linecap="butt"/>'
                )
    for name, x, y, z in LIGHTS:
        parts.append(f'<circle cx="{X(x)}" cy="{Z(z)}" r="4.5" fill="#fbbf24"/>')
        parts.append(
            f'<text x="{X(x)}" y="{Z(z)-9}" fill="#fbbf24" font-size="8" '
            f'text-anchor="middle">{name.replace("light_", "")}</text>'
        )
    parts.append(
        f'<text x="{pad}" y="{h-12}" fill="#64748b" font-size="10">'
        f'bounding box {maxx-minx:.1f} x {maxz-minz:.1f} m - wall height {WALL_H:.1f} m'
        f'</text>'
    )
    parts.append("</svg>")
    (OUT / "home.svg").write_text("\n".join(parts), encoding="utf-8")


def card_yaml():
    return """# Add this as a card (panel view recommended) after the model files are in
# /config/www/floor3d/ and floor3d-card is installed.
type: custom:floor3d-card
name: Home 3D
path: /local/floor3d/
objfile: home.obj
mtlfile: home.mtl
backgroundColor: '#0b1220'
globalLightPower: 0.55
shadow: 'no'
click: 'yes'
entities:
  - entity: light.living_room_ball_lamp
    type3d: light
    object_id: light_living_room_ball_lamp
    action: more-info
    light:
      lumens: 700
  - entity: light.bedside_lamp
    type3d: light
    object_id: light_bedside_lamp
    action: more-info
    light:
      lumens: 400
  - entity: light.mood_lights
    type3d: light
    object_id: light_mood_lights
    action: more-info
    light:
      lumens: 500
  - entity: light.bedroom_ceiling_bulbs
    type3d: light
    object_id: light_bedroom_ceiling_bulbs
    action: more-info
    light:
      lumens: 800
  - entity: light.pc_keyboard_led_strip
    type3d: light
    object_id: light_pc_keyboard_led_strip
    action: more-info
    light:
      lumens: 300
  - entity: binary_sensor.entrance_door_contact
    type3d: door
    object_id: door_entrance
    action: more-info
    door:
      doortype: swing
      side: left
      direction: inner
      degrees: 85
  - entity: binary_sensor.balcone_lato_cucina_contact
    type3d: door
    object_id: door_balcony
    action: more-info
    door:
      doortype: swing
      side: right
      direction: inner
      degrees: 70
"""


def main():
    build()
    preview()
    (OUT / "card.yaml").write_text(card_yaml(), encoding="utf-8")
    manifest = {
        "rooms": [
            {"area_id": r[0], "label": r[1], "object_id": f"room_{r[0]}",
             "width_m": round(r[4] - r[2], 2), "depth_m": round(r[5] - r[3], 2)}
            for r in ROOMS
        ],
        "lights": [{"entity": f"light.{name[6:]}", "object_id": name} for name, *_ in LIGHTS],
        "doors": [
            {"entity": "binary_sensor.entrance_door_contact", "object_id": "door_entrance"},
            {"entity": "binary_sensor.balcone_lato_cucina_contact", "object_id": "door_balcony"},
        ],
        "notes": "Starter dimensions are estimates. Edit ROOMS/WALLS in make_model.py and re-run.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("wrote", ", ".join(sorted(p.name for p in OUT.glob("home.*"))))


if __name__ == "__main__":
    main()
