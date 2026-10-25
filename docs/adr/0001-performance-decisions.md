# Performance optimizations for 3D model rendering

We chose the `floor3d-card` fork (`giosci1994/floor3d-card`) and use GLB with Draco compression to keep render times low and model load fast on mobile devices.

- **Format**: OBJ + MTL for editing, GLB for production (Draco‑compressed).
- **Compression**: Draco for geometry, meshopt for additional size reduction.
- **Loading**: Progressive streaming; smaller chunks load first, full model later if needed.
- **Materials**: One material per logical group (e.g., `material_living_room_ball`) to reduce draw calls.
- **Shadow and lighting**: Optional per‑object shadows for important items; ambient occlusion for depth.

**Consequences**: Faster loads on phones, responsive UI, but larger initial model size (a few MB) and need for initial Draco decompression CPU time. We accept this trade‑off for better user experience.