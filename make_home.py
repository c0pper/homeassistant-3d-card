#!/usr/bin/env python3
"""
Build a 3D model of the floor plan in floorplan.jpg for floor3d-card.

Plan coordinates are the pixel coordinates of the source image (x right,
y down). They are converted to metres with SCALE px/m. Edit SCALE and the
ROOMS / WALLS tables, then re-run.

Outputs: home.obj, home.mtl, home.svg, card.yaml, manifest.json
"""

import json
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent
SCALE = 70.0          # pixels per metre (placeholder: plan has no dimensions)
UNIT = 100.0          # OBJ units per metre: floor3d-card expects centimetres
H = 2.90              # wall height, m
EXT_T = 0.28          # exterior wall thickness, m
INT_T = 0.14          # interior wall thickness, m
THICK_T = 0.50        # south / south-east exterior wall thickness, m
DOOR_H = 2.10
BALCONY_HEAD = 2.85     # balcony doors go almost to ceiling
BALCONY_SILL = 0.05
WIN_SILL = 0.90
WIN_HEAD = 2.20

# plan origin (top-left outer corner is at 95,246; top-right at 1118,132)
OX, OY = 95.0, 132.0


def X(px):
    return (px - OX) / SCALE


def Z(py):
    return (py - OY) / SCALE


def P(px, py):
    return (X(px), Z(py))


# ---------------------------------------------------------------- floor polygons
# full outer footprint: the slab runs under the exterior walls
BASE = [(95, 246), (1118, 132), (1118, 570), (706, 570), (706, 876), (95, 876)]

ROOMS = [
    # id, label, polygon (px), floor material
    ("room_left", "Bedroom", [(115, 258), (324, 235), (324, 468), (115, 468)], "wood"),
    ("room_kitchen", "Kitchen", [(324, 235), (600, 204), (600, 468), (324, 468)], "tile"),
    ("room_living", "Living room (assumed)", [(600, 204), (870, 174), (870, 515), (688, 515), (688, 468), (600, 468)], "wood"),
    ("room_corridor", "Corridor", [(324, 468), (688, 468), (688, 588), (324, 588)], "stone"),
    ("room_right", "Studio", [(870, 174), (1098, 149), (1098, 515), (870, 515)], "wood"),
    ("room_ca", "C.A.", [(115, 468), (267, 468), (267, 568), (115, 568)], "tile"),
    ("room_wc1", "WC 1", [(115, 597), (267, 597), (267, 819), (115, 819)], "tile"),
    ("room_wc2", "WC 2", [(267, 597), (375, 597), (375, 819), (267, 819)], "tile"),
    ("room_stairs", "Stairs", [(375, 588), (688, 588), (688, 838), (375, 838)], "stone"),
    ("room_rip", "RIP", [(470, 405), (585, 405), (585, 524), (470, 524)], "stone"),
]

# ---------------------------------------------------------------- walls
# (name, p1, p2, thickness, [(start_m, end_m, "door"|"window"), ...])
def top_d(px):
    length = math.hypot(1118 - 95, 132 - 246)
    return (px - 95) / (1118 - 95) * length / SCALE


def bottom_d(px):
    return (706.0 - px) / SCALE


def right_bottom_d(px):
    return (1118.0 - px) / SCALE


def M(px):
    """distance in plan pixels -> metres"""
    return px / SCALE


WALLS = [
    # exterior
    ("top", P(96.1, 255.7), P(1119.1, 141.7), EXT_T, [
        (top_d(145), top_d(195), "window"),
        (top_d(210), top_d(255), "window"),
        (top_d(350), top_d(430), "balcony"),
        (top_d(460), top_d(515), "balcony"),
        (top_d(600), top_d(660), "balcony"),
        (top_d(700), top_d(760), "balcony"),
        (top_d(900), top_d(970), "window"),
        (top_d(990), top_d(1050), "window"),
    ]),
    ("right", P(1108.2, 132), P(1108.2, 570), EXT_T, []),
    ("right_bottom", P(1118, 542.5), P(706, 542.5), 0.786, [
        (right_bottom_d(970), right_bottom_d(900), "window"),
    ]),
    ("lower_east", P(697, 570), P(697, 876), 0.257, []),
    ("bottom", P(706, 857), P(95, 857), 0.543, [
        (bottom_d(670), bottom_d(600), "window"),
        (bottom_d(490), bottom_d(420), "window"),
        (bottom_d(355), bottom_d(285), "window"),
        (bottom_d(220), bottom_d(150), "window"),
    ]),
    ("left", P(105, 876), P(105, 246), 0.286, []),
    # interior
    ("left_south", P(95, 468), P(324, 468), INT_T, [(M(175), M(225), "door")]),
    ("left_east", P(324, 240), P(324, 524), INT_T, []),
    ("ca_east", P(267, 468), P(267, 597), INT_T, [(M(12), M(57), "door")]),
    ("ca_south", P(115, 568), P(267, 568), INT_T, []),
    ("wc_north", P(115, 597), P(375, 597), INT_T, [(M(35), M(85), "door"), (M(165), M(215), "door")]),
    ("wc_div", P(267, 597), P(267, 819), INT_T, []),
    ("wc_east", P(375, 597), P(375, 838), INT_T, []),
    ("wc_south", P(115, 819), P(375, 819), INT_T, []),
    ("corridor_south", P(324, 588), P(688, 588), INT_T, [(M(276), M(356), "door")]),
    ("stair_east", P(688, 588), P(688, 838), INT_T, []),
    ("rip_west", P(470, 405), P(470, 524), INT_T, []),
    ("rip_north", P(470, 405), P(585, 405), INT_T, []),
    ("rip_east", P(585, 405), P(585, 524), INT_T, [(M(25), M(85), "door")]),
    ("right_west", P(870, 178), P(870, 515), INT_T, [(M(267), M(327), "door")]),
]

# ---------------------------------------------------------------- lights
# name, px, py, height m, kind (sphere|strip)
LIGHTS = [
    ("light_living_room_ball_lamp", 740, 380, 2.55, "sphere"),
    ("light_bedroom_ceiling_bulbs", 185, 300, 2.55, "sphere"),
    ("light_bedside_lamp", 265, 330, 0.62, "sphere"),
    ("light_mood_lights", 185, 420, 2.55, "sphere"),
    ("light_pc_keyboard_led_strip", 985, 380, 0.80, "strip"),
]

# provisional room for the light legend / manifest
LIGHT_ROOMS = {
    "light_living_room_ball_lamp": "Living room",
    "light_bedroom_ceiling_bulbs": "Bedroom",
    "light_bedside_lamp": "Bedroom",
    "light_mood_lights": "Bedroom",
    "light_pc_keyboard_led_strip": "Studio",
}

# ---------------------------------------------------------------- furniture
# name, px0, py0, px1, py1, y0, y1, material
FURNITURE = [
    ("furniture_kitchen_island", 390, 330, 560, 390, 0.00, 0.90, "counter"),
    ("furniture_kitchen_top", 380, 245, 590, 290, 0.86, 0.92, "dark"),
    ("furniture_dining_table", 650, 320, 780, 420, 0.72, 0.78, "wood"),
    ("furniture_dining_leg1", 658, 328, 668, 338, 0.00, 0.72, "dark"),
    ("furniture_dining_leg2", 762, 328, 772, 338, 0.00, 0.72, "dark"),
    ("furniture_dining_leg3", 658, 402, 668, 412, 0.00, 0.72, "dark"),
    ("furniture_dining_leg4", 762, 402, 772, 412, 0.00, 0.72, "dark"),
    ("furniture_bed", 120, 300, 250, 450, 0.00, 0.52, "fabric"),
    ("furniture_bed_head", 120, 300, 250, 315, 0.00, 1.00, "wood"),
    ("furniture_nightstand", 255, 310, 295, 350, 0.00, 0.50, "wood"),
    ("furniture_desk", 930, 330, 1040, 390, 0.72, 0.76, "wood"),
    ("furniture_desk_leg1", 934, 334, 944, 344, 0.00, 0.72, "dark"),
    ("furniture_desk_leg2", 1026, 334, 1036, 344, 0.00, 0.72, "dark"),
    ("furniture_desk_leg3", 934, 376, 944, 386, 0.00, 0.72, "dark"),
    ("furniture_desk_leg4", 1026, 376, 1036, 386, 0.00, 0.72, "dark"),
    ("furniture_wardrobe", 930, 400, 1050, 455, 0.00, 2.10, "wood"),
]

MATERIALS = {
    "wood":    (0.62, 0.45, 0.30),
    "tile":    (0.80, 0.82, 0.84),
    "stone":   (0.55, 0.55, 0.52),
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
        self.verts.append((x * UNIT, y * UNIT, z * UNIT))
        self.vcount += 1
        return self.vcount

    def _n(self, x, y, z):
        ln = math.sqrt(x * x + y * y + z * z) or 1.0
        self.norms.append((x / ln, y / ln, z / ln))
        self.ncount += 1
        return self.ncount

    def face(self, pts, hint):
        # pts: list of 3 or 4 (x,y,z); hint: approximate outward normal
        p0, p1, p2 = pts[0], pts[1], pts[2]
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        if nx * hint[0] + ny * hint[1] + nz * hint[2] < 0:
            pts = list(reversed(pts))
        n = self._n(*hint)
        idx = " ".join(f"{self._v(*p)}//{n}" for p in pts)
        self.lines.append(f"f {idx}")

    def box(self, name, mat, x0, y0, z0, x1, y1, z1):
        x0, x1 = sorted((x0, x1))
        y0, y1 = sorted((y0, y1))
        z0, z1 = sorted((z0, z1))
        self.lines.append(f"o {name}")
        self.lines.append(f"usemtl {mat}")
        c = [
            (x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1),
            (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1),
        ]
        self.face([c[0], c[3], c[2], c[1]], (0, -1, 0))
        self.face([c[4], c[5], c[6], c[7]], (0, 1, 0))
        self.face([c[0], c[1], c[5], c[4]], (0, 0, -1))
        self.face([c[3], c[7], c[6], c[2]], (0, 0, 1))
        self.face([c[0], c[4], c[7], c[3]], (-1, 0, 0))
        self.face([c[1], c[2], c[6], c[5]], (1, 0, 0))

    def poly_prism(self, name, mat, poly, y0, y1):
        """Extrude a CCW (x,z) polygon between y0 and y1."""
        pts = [(x, z) for x, z in poly]
        # ensure CCW in (x,z)
        area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] -
                   pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
        if area < 0:
            pts.reverse()
        self.lines.append(f"o {name}")
        self.lines.append(f"usemtl {mat}")
        for tri in triangulate(pts):
            a, b, c = [pts[i] for i in tri]
            self.face([(a[0], y0, a[1]), (b[0], y0, b[1]), (c[0], y0, c[1])], (0, -1, 0))
            self.face([(a[0], y1, a[1]), (b[0], y1, b[1]), (c[0], y1, c[1])], (0, 1, 0))
        cx = sum(p[0] for p in pts) / len(pts)
        cz = sum(p[1] for p in pts) / len(pts)
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            hint = (mx - cx, 0, mz - cz)
            self.face([(a[0], y0, a[1]), (b[0], y0, b[1]),
                       (b[0], y1, b[1]), (a[0], y1, a[1])], hint)

    def sphere(self, name, mat, cx, cy, cz, r, slices=12, stacks=8):
        self.lines.append(f"o {name}")
        self.lines.append(f"usemtl {mat}")
        grid = []
        for i in range(stacks + 1):
            theta = math.pi * i / stacks
            row = []
            for j in range(slices):
                phi = 2 * math.pi * j / slices
                row.append((cx + r * math.sin(theta) * math.cos(phi),
                            cy + r * math.cos(theta),
                            cz + r * math.sin(theta) * math.sin(phi)))
            grid.append(row)
        for i in range(stacks):
            for j in range(slices):
                j2 = (j + 1) % slices
                a, b = grid[i][j], grid[i][j2]
                c, d = grid[i + 1][j2], grid[i + 1][j]
                mid = ((a[0] + c[0]) / 2 - cx, (a[1] + c[1]) / 2 - cy, (a[2] + c[2]) / 2 - cz)
                if i == 0:
                    # top pole: a == b, use a triangle instead of a degenerate quad
                    self.face([a, c, d], mid)
                elif i == stacks - 1:
                    # bottom pole: c == d
                    self.face([a, b, c], mid)
                else:
                    self.face([a, b, c, d], mid)

    def write(self, path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("# floor plan model for floor3d-card\n")
            fh.write("mtllib home.mtl\n")
            for v in self.verts:
                fh.write("v %.4f %.4f %.4f\n" % v)
            for n in self.norms:
                fh.write("vn %.4f %.4f %.4f\n" % n)
            fh.write("\n".join(self.lines))
            fh.write("\n")


def triangulate(poly):
    """Ear clipping for a simple polygon; returns index triples."""
    n = len(poly)
    if n < 3:
        return []
    idx = list(range(n))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 1000:
        guard += 1
        ear = False
        for i in range(len(idx)):
            ia, ib, ic = idx[i - 1], idx[i], idx[(i + 1) % len(idx)]
            a, b, c = poly[ia], poly[ib], poly[ic]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if cross <= 1e-9:
                continue
            inside = False
            for j in idx:
                if j in (ia, ib, ic):
                    continue
                p = poly[j]
                if point_in_tri(p, a, b, c):
                    inside = True
                    break
            if not inside:
                tris.append((ia, ib, ic))
                idx.pop(i)
                ear = True
                break
        if not ear:
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    return tris


def point_in_tri(p, a, b, c):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = sign(p, a, b), sign(p, b, c), sign(p, c, a)
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


_wall_no = 0


def add_wall(obj, name, p1, p2, t, openings):
    global _wall_no
    dx, dz = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dz)
    if length < 1e-6:
        return
    ux, uz = dx / length, dz / length
    vx, vz = -uz * t / 2, ux * t / 2

    def solid(a, b, y0, y1, tag=""):
        global _wall_no
        if b - a < 1e-4 or y1 - y0 < 1e-4:
            return
        _wall_no += 1
        ax, az = p1[0] + ux * a, p1[1] + uz * a
        bx, bz = p1[0] + ux * b, p1[1] + uz * b
        poly = [(ax + vx, az + vz), (bx + vx, bz + vz),
                (bx - vx, bz - vz), (ax - vx, az - vz)]
        obj.poly_prism(f"wall_{_wall_no:03d}", "wall", poly, y0, y1)

    cur = 0.0
    for a, b, kind in sorted(openings):
        a, b = max(0.0, a), min(length, b)
        if a > cur:
            solid(cur, a, 0.0, H)
        if kind == "door":
            solid(a, b, DOOR_H, H)
        elif kind == "balcony":
            # full-height glass door; small wall transom above near ceiling
            solid(a, b, BALCONY_HEAD, H)
            # glass panel (full opening, thin)
            _wall_no += 1
            gx = -uz * 0.02
            gz = ux * 0.02
            ax, az = p1[0] + ux * a, p1[1] + uz * a
            bx, bz = p1[0] + ux * b, p1[1] + uz * b
            obj.poly_prism(f"balcony_{_wall_no:03d}", "glass",
                           [(ax + gx, az + gz), (bx + gx, bz + gz),
                            (bx - gx, bz - gz), (ax - gx, az - gz)], BALCONY_SILL, BALCONY_HEAD)
        else:
            solid(a, b, 0.0, WIN_SILL)
            solid(a, b, WIN_HEAD, H)
            # glass pane (thin oriented box)
            _wall_no += 1
            gx = -uz * 0.02
            gz = ux * 0.02
            ax, az = p1[0] + ux * a, p1[1] + uz * a
            bx, bz = p1[0] + ux * b, p1[1] + uz * b
            obj.poly_prism(f"window_{_wall_no:03d}", "glass",
                           [(ax + gx, az + gz), (bx + gx, bz + gz),
                            (bx - gx, bz - gz), (ax - gx, az - gz)], WIN_SILL, WIN_HEAD)
        cur = b
    if cur < length:
        solid(cur, length, 0.0, H)


def build():
    obj = Obj()
    # base slab
    obj.poly_prism("floor_base", "stone", [P(*p) for p in BASE], -0.10, 0.0)
    # room floors
    for rid, label, poly, mat in ROOMS:
        y0, y1 = (0.0, 0.014) if rid != "room_rip" else (0.02, 0.034)
        obj.poly_prism(rid, mat, [P(*p) for p in poly], y0, y1)
    # walls
    for name, p1, p2, t, openings in WALLS:
        add_wall(obj, name, p1, p2, t, openings)
    # stairs: straight flight, 14 steps, rising south from the corridor door
    x0, x1 = X(458), X(610)
    z0, z1 = Z(588), Z(838)
    steps = 14
    for i in range(steps):
        za = z0 + (z1 - z0) * i / steps
        zb = z0 + (z1 - z0) * (i + 1) / steps
        obj.box(f"stair_{i + 1:02d}", "stone", x0, 0.0, za, x1, H * (i + 1) / steps, zb)
    # stair railings
    obj.box("stair_rail_left", "dark", x0 - 0.04, 0.0, z0, x0, 1.05, z1)
    obj.box("stair_rail_right", "dark", x1, 0.0, z0, x1 + 0.04, 1.05, z1)
    # lights
    for name, px, py, y, kind in LIGHTS:
        if kind == "sphere":
            obj.sphere(name, "light", X(px), y, Z(py), 0.09)
        else:
            obj.box(name, "light", X(px - 18), y - 0.015, Z(py) - 0.03,
                    X(px + 18), y + 0.015, Z(py) + 0.03)
    # furniture
    for name, px0, py0, px1, py1, y0, y1, mat in FURNITURE:
        obj.box(name, mat, X(px0), y0, Z(py0), X(px1), y1, Z(py1))
    obj.write(OUT / "home.obj")

    with open(OUT / "home.mtl", "w", encoding="utf-8") as fh:
        fh.write("# floor plan model materials\n")
        for name, (r, g, b) in MATERIALS.items():
            fh.write(f"newmtl {name}\nKd {r:.3f} {g:.3f} {b:.3f}\nKa 0.05 0.05 0.05\nKs 0.10 0.10 0.10\nNs 20\n")
            if name == "light":
                fh.write("Ke 0.90 0.80 0.50\n")
            if name == "glass":
                fh.write("d 0.35\n")
            fh.write("\n")
    return obj


def preview():
    """Top-view SVG in plan pixels: rooms, walls, furniture, lights + legends."""
    pad = 50
    minx, maxx = 60, 1160
    miny, maxy = 95, 910
    panel_x = 1180
    panel_w = 300
    w = panel_x + panel_w + pad
    h = int(maxy - miny + pad * 2)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
             f'viewBox="0 0 {w} {h}" font-family="system-ui, sans-serif">',
             f'<rect width="100%" height="100%" fill="#0b1220"/>',
             '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" '
             'orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#cbd5e1"/></marker></defs>']
    ox, oy = pad - minx, pad - miny

    def px(x):
        return x + ox

    def py(y):
        return y + oy

    # WALLS are stored in metres; the SVG uses plan pixels
    def wx(x):
        return x * SCALE + OX + ox

    def wy(z):
        return z * SCALE + OY + oy

    fills = {"wood": "#6b4f37", "tile": "#3d4b56", "stone": "#4b4b47"}
    edge = {"wood": "#a98462", "tile": "#7f9aad", "stone": "#7f7f75"}

    # title
    width_m = (1118 - 95) / SCALE
    depth_m = (876 - 132) / SCALE
    parts.append(f'<text x="{pad}" y="28" fill="#f8fafc" font-size="19" font-weight="700">'
                 f'3D floor-plan model — provisional layout</text>')
    parts.append(f'<text x="{pad}" y="46" fill="#94a3b8" font-size="11">'
                 f'{width_m:.1f} × {depth_m:.1f} m · {SCALE:.0f} px/m placeholder · '
                 f'OBJ vertices in cm · room numbers match the legend</text>')

    # base slab under the rooms/walls (keeps gaps from reading as holes)
    d = " ".join(("M" if i == 0 else "L") + f"{px(x)} {py(y)}" for i, (x, y) in enumerate(BASE)) + " Z"
    parts.append(f'<path d="{d}" fill="#343a40" stroke="none"/>')

    # room floors
    for idx, (rid, label, poly, mat) in enumerate(ROOMS, 1):
        d = " ".join(("M" if i == 0 else "L") + f"{px(x)} {py(y)}" for i, (x, y) in enumerate(poly)) + " Z"
        parts.append(f'<path d="{d}" fill="{fills[mat]}" stroke="{edge[mat]}" stroke-width="1.2"/>')

    # furniture outlines + a few labels
    flabels = {
        "furniture_kitchen_island": "island",
        "furniture_dining_table": "table",
        "furniture_bed": "bed",
        "furniture_desk": "desk",
        "furniture_wardrobe": "wardrobe",
        "furniture_kitchen_top": "counter",
    }
    for name, x0, y0, x1, y1, z0, z1, mat in FURNITURE:
        if "leg" in name:
            continue
        parts.append(f'<rect x="{px(x0)}" y="{py(y0)}" width="{px(x1) - px(x0)}" height="{py(y1) - py(y0)}" '
                     f'fill="none" stroke="#cbd5e1" stroke-width="0.9" stroke-dasharray="3 3" opacity="0.55"/>')
        if name in flabels:
            parts.append(f'<text x="{(px(x0) + px(x1)) / 2}" y="{(py(y0) + py(y1)) / 2 + 3}" '
                         f'fill="#cbd5e1" font-size="7" text-anchor="middle" opacity="0.85">{flabels[name]}</text>')

    # walls + openings
    for name, p1, p2, t, openings in WALLS:
        parts.append(f'<line x1="{wx(p1[0]):.1f}" y1="{wy(p1[1]):.1f}" x2="{wx(p2[0]):.1f}" y2="{wy(p2[1]):.1f}" '
                     f'stroke="#e5edf7" stroke-width="{max(3, t * SCALE):.1f}" stroke-linecap="butt"/>')
        for a, b, kind in openings:
            dx, dz = p2[0] - p1[0], p2[1] - p1[1]
            L = math.hypot(dx, dz)
            ux, uz = dx / L, dz / L
            ax, az = p1[0] + ux * a, p1[1] + uz * a
            bx, bz = p1[0] + ux * b, p1[1] + uz * b
            color = "#45c4e8" if kind == "window" else ("#e879d6" if kind == "balcony" else "#f2b84b")
            parts.append(f'<line x1="{wx(ax):.1f}" y1="{wy(az):.1f}" x2="{wx(bx):.1f}" y2="{wy(bz):.1f}" '
                         f'stroke="{color}" stroke-width="5"/>')

    # stairs
    x0, x1 = 458, 610
    z0, z1 = 588, 838
    for i in range(15):
        z = z0 + (z1 - z0) * i / 14
        parts.append(f'<line x1="{px(x0)}" y1="{py(z)}" x2="{px(x1)}" y2="{py(z)}" stroke="#cbd5e1" stroke-width="0.8"/>')
    parts.append(f'<line x1="{px(534)}" y1="{py(610)}" x2="{px(534)}" y2="{py(820)}" stroke="#cbd5e1" '
                 f'stroke-width="1.3" stroke-dasharray="4 4" marker-end="url(#arrow)"/>')
    parts.append(f'<text x="{px(544)}" y="{py(700)}" fill="#cbd5e1" font-size="9">UP</text>')

    # room markers (numbers refer to the legend)
    roo_pos = {
        "room_left": (205, 295),
        "room_kitchen": (445, 292),
        "room_living": (820, 235),
        "room_corridor": (370, 545),
        "room_right": (995, 220),
        "room_ca": (185, 505),
        "room_wc1": (185, 690),
        "room_wc2": (315, 690),
        "room_stairs": (405, 645),
        "room_rip": (522, 462),
    }
    room_rows = []
    for idx, (rid, label, poly, mat) in enumerate(ROOMS, 1):
        area = abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
                       poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2 / SCALE ** 2
        short = label.replace(" (assumed)", "")
        x, y = roo_pos.get(rid, (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)))
        parts.append(f'<circle cx="{px(x)}" cy="{py(y)}" r="9" fill="#0b1220" stroke="#f8fafc" stroke-width="1.5"/>')
        parts.append(f'<text x="{px(x)}" y="{py(y) + 3}" fill="#f8fafc" font-size="8" font-weight="700" '
                     f'text-anchor="middle">{idx}</text>')
        parts.append(f'<text x="{px(x) + 13}" y="{py(y) + 1}" fill="#f8fafc" font-size="9" font-weight="700">{short}</text>')
        parts.append(f'<text x="{px(x) + 13}" y="{py(y) + 11}" fill="#94a3b8" font-size="7.5">{area:.1f} m²</text>')
        room_rows.append((idx, short + (" *" if "assumed" in label else ""), area, mat))

    # lights
    for i, (name, x, y, height, kind) in enumerate(LIGHTS, 1):
        parts.append(f'<circle cx="{px(x)}" cy="{py(y)}" r="8" fill="#fbbf24" stroke="#111827" stroke-width="1.2"/>')
        parts.append(f'<text x="{px(x)}" y="{py(y) + 3}" fill="#111827" font-size="8" font-weight="700" '
                     f'text-anchor="middle">L{i}</text>')

    # legend panel
    parts.append(f'<rect x="{panel_x}" y="{pad}" width="{panel_w}" height="{h - 2 * pad}" rx="12" '
                 f'fill="#111a2e" stroke="#24324a"/>')
    ly = pad + 28
    parts.append(f'<text x="{panel_x + 18}" y="{ly}" fill="#f8fafc" font-size="14" font-weight="700">Rooms</text>')
    ly += 18
    for idx, label, area, mat in room_rows:
        parts.append(f'<rect x="{panel_x + 18}" y="{ly - 9}" width="10" height="10" rx="2" fill="{fills[mat]}" '
                     f'stroke="{edge[mat]}" stroke-width="0.8"/>')
        parts.append(f'<text x="{panel_x + 36}" y="{ly}" fill="#e2e8f0" font-size="10">'
                     f'{idx}&#160;&#160;{label}</text>')
        parts.append(f'<text x="{panel_x + panel_w - 18}" y="{ly}" fill="#94a3b8" font-size="9" '
                     f'text-anchor="end">{area:.1f} m²</text>')
        ly += 18
    ly += 12
    parts.append(f'<text x="{panel_x + 18}" y="{ly}" fill="#f8fafc" font-size="14" font-weight="700">Lights</text>')
    ly += 18
    for i, (name, x, y, height, kind) in enumerate(LIGHTS, 1):
        parts.append(f'<circle cx="{panel_x + 23}" cy="{ly - 3}" r="6" fill="#fbbf24" stroke="#111827" stroke-width="1"/>')
        parts.append(f'<text x="{panel_x + 23}" y="{ly}" fill="#111827" font-size="6" font-weight="700" '
                     f'text-anchor="middle">L{i}</text>')
        parts.append(f'<text x="{panel_x + 36}" y="{ly}" fill="#e2e8f0" font-size="8.5">'
                     f'{name.replace("light_", "")}</text>')
        parts.append(f'<text x="{panel_x + 36}" y="{ly + 10}" fill="#94a3b8" font-size="7.5">'
                     f'{LIGHT_ROOMS.get(name, "?")}</text>')
        ly += 24
    ly += 6
    parts.append(f'<text x="{panel_x + 18}" y="{ly}" fill="#f8fafc" font-size="14" font-weight="700">Legend</text>')
    ly += 17
    for color, label in (("#e5edf7", "wall"), ("#45c4e8", "window / glazing"), ("#e879d6", "balcony door / glass"), ("#f2b84b", "door opening")):
        parts.append(f'<line x1="{panel_x + 18}" y1="{ly - 3}" x2="{panel_x + 42}" y2="{ly - 3}" stroke="{color}" stroke-width="4"/>')
        parts.append(f'<text x="{panel_x + 50}" y="{ly}" fill="#cbd5e1" font-size="9">{label}</text>')
        ly += 16
    ly += 10
    note = [
        "* room name is an assumption from the layout.",
        "Confirmed: left = Bedroom, right = Studio,",
        "WC 1 = Master bathroom.",
        f"Scale: {SCALE:.0f} px/m, no dimensions on the plan.",
        f"Overall {width_m:.1f} x {depth_m:.1f} m (placeholder).",
        "Remaining: Living / Kitchen split.",
    ]
    for line in note:
        parts.append(f'<text x="{panel_x + 18}" y="{ly}" fill="#94a3b8" font-size="8.5">{line}</text>')
        ly += 13

    # scale bar
    parts.append(f'<line x1="{px(60)}" y1="890" x2="{px(130)}" y2="890" stroke="#cbd5e1" stroke-width="3"/>')
    parts.append(f'<line x1="{px(60)}" y1="884" x2="{px(60)}" y2="896" stroke="#cbd5e1" stroke-width="2"/>')
    parts.append(f'<line x1="{px(130)}" y1="884" x2="{px(130)}" y2="896" stroke="#cbd5e1" stroke-width="2"/>')
    parts.append(f'<text x="{px(95)}" y="880" fill="#cbd5e1" font-size="9" text-anchor="middle">1 m</text>')

    parts.append("</svg>")
    (OUT / "home.svg").write_text("\n".join(parts), encoding="utf-8")


def card_yaml():
    return """# Card for the floor-plan model.
# Permanent setup: copy home.obj + home.mtl to /config/www/floor3d/
# and keep path: /local/floor3d/.
# Temporary preview: set path: http://192.168.1.4:8765/
type: custom:floor3d-card
name: Home 3D
path: /local/floor3d/
objfile: home.obj
mtlfile: home.mtl
header: 'no'
backgroundColor: '#0f172a'
globalLightPower: 0.55
shadow: 'no'
click: 'yes'
walls: fade
walls_opacity: 0.18
camera_position:
  x: 0
  y: 1500
  z: 850
camera_target:
  x: 0
  y: 150
  z: 0
zoom_areas:
  - zoom: Whole home
    object_id: floor_base
    direction: {x: 0.2, y: 1, z: 0.55}
    distance: 1900
  - zoom: Bedroom
    object_id: room_left
    direction: {x: 0, y: 1, z: 0.45}
    distance: 650
  - zoom: Studio
    object_id: room_right
    direction: {x: 0, y: 1, z: 0.45}
    distance: 800
  - zoom: Kitchen
    object_id: room_kitchen
    direction: {x: 0, y: 1, z: 0.45}
    distance: 700
  - zoom: Living room
    object_id: room_living
    direction: {x: 0, y: 1, z: 0.45}
    distance: 800
  - zoom: Master bath
    object_id: room_wc1
    direction: {x: 0, y: 1, z: 0.45}
    distance: 600
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
"""


def main():
    build()
    preview()
    (OUT / "card.yaml").write_text(card_yaml(), encoding="utf-8")
    area_map = {
        "room_left": "bedroom",
        "room_kitchen": "kitchen",
        "room_living": "living_room",
        "room_right": "studio",
        "room_wc1": "master_bathroom",
        "room_wc2": None,
        "room_ca": None,
        "room_corridor": None,
        "room_stairs": None,
        "room_rip": None,
    }
    rooms = []
    for idx, (rid, label, poly, mat) in enumerate(ROOMS, 1):
        area = abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] -
                       poly[(i + 1) % len(poly)][0] * poly[i][1]
                       for i in range(len(poly)))) / 2 / SCALE ** 2
        rooms.append({
            "number": idx,
            "object_id": rid,
            "label": label,
            "area_m2": round(area, 2),
            "material": mat,
            "ha_area": area_map.get(rid),
            "assuming_name": "assumed" in label,
            "assuming_area": False,
        })
    manifest = {
        "scale_px_per_m": SCALE,
        "rooms": rooms,
        "lights": [{"entity": "light." + name[6:], "object_id": name,
                    "px": px, "py": py, "height_m": h, "room": LIGHT_ROOMS.get(name)}
                   for name, px, py, h, _ in LIGHTS],
        "walls": len(WALLS),
        "note": ("Pixel coordinates from floorplan.jpg. Absolute scale is a placeholder; "
                 "OBJ vertices are centimetres. HA area mapping and room names marked "
                 "'assuming' are provisional."),
        "obj_units": "cm",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("wrote home.obj / home.mtl / home.svg / card.yaml")


if __name__ == "__main__":
    main()
