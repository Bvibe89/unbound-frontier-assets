# Asset Index

A record of shipped game-ready assets: what each one is, its verified real-world
dimensions, and how it is meant to be used.

`ASSET_BIBLE.md` requires explicit dimensions to be recorded rather than implied
by a size-class label. This file is that record. It is the authoritative answer
to "how big is this thing" — the TINY/SMALL/MEDIUM/LARGE/HUGE/MASSIVE label is
shorthand only, and because the bands are height-derived it can read low for
wide flat assets (a 2.4 m outcrop standing 0.94 m tall labels as SMALL).

Populated as assets pass through a normalization pass; it is not yet complete
for assets predating this file.

All dimensions in metres, measured from the shipped GLB. Every asset is scaled
against the 1.78 m / 5'10" human anchor, has its origin X/Y centred with ground
contact at 0, uses one mesh and one material, is two-sided, and is metallic 0.

## Desert Environment Props

Ground scatter and natural cover for the desert planet. Bare dead wood, not
living trees — there is no foliage and no alpha cutout in this set.

| Asset | What it is | X × Y × Z | Class | Tris | Base/Normal | Suggested collision |
|---|---|---|---|---|---|---|
| Desert Aloe | blunt-leaf aloe clump | 0.70 × 0.65 × 0.70 | SMALL | 154 | 512 / 256 | none — walk through |
| Desert Agave | agave/yucca spiky rosette | 0.88 × 0.83 × 0.85 | SMALL | 168 | 512 / 256 | none — walk through |
| Desert Rock Shelf | stacked flat slabs, knee-high | 2.20 × 1.72 × 0.87 | SMALL | 438 | 512 / 256 | trimesh |
| Desert Rock Outcrop | broad flat outcrop plate | 2.36 × 2.40 × 0.94 | SMALL | 382 | 512 / 256 | trimesh |
| Desert Rock Boulder Pair | two rounded boulders + low slab | 1.94 × 2.20 × 1.27 | MEDIUM | 312 | 512 / 256 | trimesh |
| Desert Rock Boulder Group | four rounded boulders | 2.60 × 1.90 × 1.44 | MEDIUM | 478 | 512 / 256 | trimesh |
| Desert Deadwood Stump | splayed dead root/stump mass | 1.90 × 1.90 × 1.51 | MEDIUM | 198 | 512 / 256 | trunk proxy |
| Desert Rock Block | blocky boulder + base rocks | 2.61 × 2.53 × 1.55 | MEDIUM | 614 | 512 / 256 | trimesh |
| Desert Rock Pile | tall angular pile, landmark | 2.70 × 2.09 × 2.10 | LARGE | 398 | 1024 / 512 | trimesh |
| Desert Deadwood Snag | thick broken stump | 2.19 × 1.39 × 2.60 | LARGE | 302 | 512 / 256 | trunk proxy |
| Desert Deadwood Leaning | windswept leaning dead tree | 3.50 × 1.60 × 3.60 | HUGE | 442 | 1024 / 512 | trunk proxy |
| Desert Deadwood Fork | twin-trunk dead tree | 3.41 × 2.44 × 3.90 | HUGE | 618 | 1024 / 512 | trunk proxy |
| Desert Deadwood Tall | multi-limb dead tree | 2.88 × 2.08 × 4.20 | HUGE | 550 | 1024 / 512 | trunk proxy |

Collision notes, for the wrapper scenes on the Godot side:

- **trimesh** — the render mesh makes a good collider at these triangle counts.
  Set it in Godot's per-mesh import settings or a wrapper scene; nothing needs
  to be baked into the GLB. A single convex hull is wrong for the multi-boulder
  assets, as it would bridge the gaps between separate rocks.
- **trunk proxy** — do NOT use the render mesh. Trimesh collision over bare
  branches snags the player. Place a CylinderShape3D on the trunk only and give
  the branches no collision.
- **none** — small scrub the player should walk straight through.

A known cosmetic mismatch: the mesh/material names inside these GLBs still
carry the pre-rename identifiers (e.g. `Desert_Rock_Cluster_D` inside
`Desert Rock Block.glb`). The files were renamed without re-exporting, to avoid
disturbing verified output. Rename the node in the wrapper scene, or fold the
fix into a future pass.
