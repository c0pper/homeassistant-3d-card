# Home Assistant 3D Card Glossary

## Cardinal Directions

| Term | Definition | Example |
|------|------------|---------|
| **North** | Toward the top of the floor plan (positive Z). |
| **South** | Toward the bottom of the floor plan (negative Z). |
| **East** | Toward the right of the floor plan (positive X). |
| **West** | Toward the left of the floor plan (negative X). |
| **Center** | Midpoint of a room or object. |

## Rooms & Areas

| Term | Definition | Object ID |
|------|------------|-----------|
| **Main** | The only floor in this project – the 5th floor apartment. All rooms are on this floor. | — |
| **Bedroom** | Primary sleeping space. | `room_left` |
| **Kitchen** | Kitchen area. | `room_kitchen` |
| **Living room** | Common open space used for relaxation. | `room_living` |
| **Corridor** | Hall inside the main entrance, open to the living room. | `room_corridor` |
| **Studio** | Open-plan living/working space. | `room_right` |
| **C.A. (wardrobe room)** | Walk-in wardrobe (*cabina armadio*), 4.0 m², entered from the bedroom. Its old door to the corridor was removed. | `room_ca` |
| **WC 1 (master bathroom)** | Master bathroom. | `room_wc1` |
| **WC 2 (second bathroom)** | Second bathroom. | `room_wc2` |
| **RIP (storage)** | Storage room (*ripostiglio*), north of the corridor, with a rounded north-east corner and its door in the south wall. | `room_rip` |

## Floors

| Term | Definition | Value |
|------|------------|-------|
| **Main** | The only floor in this project (5th floor). |

## 3D Modeling

| Term | Definition | Example |
|------|------------|---------|
| **Object Name** | The 3D model file/name that corresponds to a HA entity. |
| **Entity ID** | The HA entity ID (e.g., `light.living_room_ball_lamp`). |
| **Naming Convention** | Use `room_<type>_<feature>` for 3D objects (e.g., `living_room_light`, `kitchen_counter`, `bedroom_ceiling`). **Resolution**: 3D object names mirror HA entity IDs directly (e.g., `light.living_room_ball_lamp` → `living_room_ball_lamp`); no synonyms. One-to-one mapping. | `light.living_room_ball_lamp` → `living_room_ball_lamp` |

## HA Entity Naming

| Term | Definition | Example |
|------|------------|---------|
| **Device‑centric** | Naming by physical location (e.g., `light.bedroom_ceiling`). |
| **Function‑centric** | Naming by what the entity does (e.g., `light.living_room_ball_lamp`). |
| **Rule** | Treat Home Assistant entity IDs as the **source of truth** — stick to HA naming even where inconsistent; do not invent alternative names. |
| **3D object mapping** | Strip the domain prefix from the HA entity ID to form the 3D object name (e.g., `light.living_room_ball_lamp` → `living_room_ball_lamp`). |

## Architectural Details

| Term | Definition | Value |
|------|------------|-------|
| **Wall Thickness** | Confirmed: interior walls 0.14 m; exterior walls 0.28 m. |
| **Wall Height** | 2.70 m (standard ceiling height). |
| **Floor** | Only floor present: **Main** (5th floor). |

## Exterior Areas

| Term | Definition | Value |
|------|------------|-------|
| **Stairwell** | The common stairwell outside the apartment, beyond the main entrance. Outside the apartment boundary, so it is not modelled. | — |
| **Main entrance** | The apartment's entrance door, in the corridor's south wall (object `corridor_south`). It opens towards the stairwell landing. | — |

## Storage

RIP is listed under [Rooms & Areas](#rooms--areas).

## Design Decisions (to be documented in ADRs)

- **Model format**: OBJ + MTL + GLB (for 3D export)
- **3D object naming**: Mirrors HA entity IDs directly (e.g., `light.living_room_ball_lamp` → `living_room_ball_lamp` in OBJ group/`o` names). Keeps it consistent and easy to bind.
- **No synonyms**: Each entity has exactly one 3D object name; one-to-one mapping.
- **Performance**: GLB compressed with Draco. See [ADR 0001: Performance decisions](docs/adr/0001-performance-decisions.md).
- **Material naming**: Use material names that match HA entity names (e.g., `light.living_room_ball_lamp` → `material_living_room_ball`).
- **Card type**: Custom card that renders the 3D model in the dashboard.
- **Choice**: floor3d‑card fork (active, updated) vs original (dormant). We chose the fork.
- **Binding**: Object‑level binding (each entity maps to one 3D object). One binding per entity.
- **Architectural details**: Wall thickness 0.14m (interior), 0.28m (exterior); wall height 2.70m.
- **Locations**: Only one floor: **Main** (5th floor apartment). Rooms: Bedroom, Kitchen, Living room, Corridor, Studio, C.A. wardrobe, WC 1, WC 2, RIP.
- **Naming**: HA entity IDs as source of truth; 3D object names mirror them.
- **Scale**: Metric units; all dimensions in meters.

## Furniture & Placement

| Term | Definition | Example |
|------|------------|---------|
| **Furniture** | Objects placed inside rooms (e.g., bed, desk, chair). |
| **Placement** | Describes where furniture goes using cardinal directions (north/south/east/west) relative to the room, or room-relative language (center, wall-aligned, western side of kitchen). |
| **Position** | Final placement determined by both cardinal direction and room-relative language combined. |

## Walls

| Term | Definition | Example |
|------|------------|---------|
| **Wall (direction)** | Named by cardinal direction relative to room (e.g., north wall, south wall). |
| **Wall (adjacency)** | Named by room connection (e.g., wall between living room and kitchen). |
| **Wall thickness** | Confirmed: interior 0.14 m; exterior 0.28 m. |
| **Wall height** | Confirmed: 2.70 m. |

## Windows, Balconies & Doors

| Term | Definition | Example |
|------|------------|---------|
| **Window** | Separate 3D object, named like `window.living_room`, `window.kitchen`. Can be linked to sensors. |
| **Balcony** | Separate 3D object, named like `balcony.kitchen`, `balcony.studio`. Two are modelled on the north wall: `balcony_living` (over both living-room doors) and `balcony_kitchen` (over both kitchen doors), each a slab with a glass parapet and a dark handrail. |
| **Door (opening)** | Separate 3D object linked to binary sensors (`binary_sensor.entrance_door_contact`). Can represent open/closed states in 3D. |

## Performance Concepts

| Term | Definition | Example / Note |
|------|------------|---------------|
| **Draw call** | Number of GPU draw calls — fewer is faster; group objects with same material to reduce. | Keep separate objects per material group. |
| **Texture atlas** | Combining textures into one image to reduce draw calls and improve load time. | Use atlas for room surfaces if model grows. |
| **Draco compression** | Google Draco compression for GLB; reduces file size ~50%+ with minimal visual loss. | Standard for production GLB export. |
| **Meshopt compression** | Alternative to Draco; can be combined with Draco for even smaller files. | Optional if size is critical. |
| **LOD** | Level of Detail — using simpler mesh for distant objects to improve render performance. | Not implemented yet; consider if model gets very large. |
| **Shadow rendering** | Real-time shadow calculation; expensive on mobile. | Optional per-object; disable for small objects. |
| **Ambient Occlusion** | Simulated shadowing in crevices for depth; cheaper than full shadows. | Used in floor3d-card for depth. |

---

*This glossary is the single source of truth for terminology in the floor3d-starter project.*
