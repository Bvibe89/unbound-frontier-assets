# Asset Index

Every shipped game-ready asset: what it is, its verified real-world dimensions,
and how it is meant to be used.

`ASSET_BIBLE.md` requires explicit dimensions to be recorded rather than implied by
a size-class label. This file is that record, and it is the authoritative answer to
"how big is this thing". The TINY/SMALL/MEDIUM/LARGE/HUGE/MASSIVE label is shorthand
only; because the bands are height-derived it reads low for wide flat assets, so
`Desert Rock Outcrop` spans 2.4 m while labelling SMALL.

**W x D x H in metres**, measured from the shipped GLB's own accessor bounds, not
from anything in a Blender session. Every asset is scaled against the 1.78 m / 5'10"
human anchor and has its origin X/Z centred with ground contact at 0 - verified for
every asset listed here, with no exceptions.

77 assets across 11 families.

## Characters

The player rig. `Human Base v4 Rigged` is the only one kept: full rig, 20 finger bones, 12 animation clips. Earlier versions and a rejected retexture experiment were removed. Its authoring scripts live in `Blender Source` and were written during the v3 pass, since v4 is v3's rig plus a face-texture transfer.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Human Base v4 Rigged | player rig, v3 plus transferred face texture - current best | 1.91 x 0.34 x 1.86 | MEDIUM | 1754 |  |

## Creatures

Living desert fauna. Heights are standing height; depth is body length.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Desert Predator Small | small spiked predator, crouched; same species family as the large one | 0.83 x 1.40 x 0.75 | SMALL | 1178 |  |
| Desert Anteater | long-snouted burrowing forager | 1.04 x 2.90 x 1.70 | MEDIUM | 820 |  |
| Desert Armadillo | armour-plated quadruped | 2.28 x 4.38 x 1.70 | MEDIUM | 855 |  |
| Desert Grazer | deer-like herbivore | 0.59 x 1.78 x 1.70 | MEDIUM | 1102 |  |
| Desert Predator Large | large spiked apex predator | 1.57 x 3.45 x 1.70 | MEDIUM | 1068 |  |

## Creature Lairs

Burrows, dens and nests belonging to the creatures above.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Desert Grazer Lair | grazer bedding hollow | 2.30 x 2.30 x 0.51 | SMALL | 456 |  |
| Desert Anteater Lair | anteater burrow mound | 3.39 x 3.80 x 1.34 | MEDIUM | 632 |  |
| Desert Predator Lair | predator den entrance | 4.30 x 4.25 x 2.12 | LARGE | 658 |  |
| Desert Armadillo Lair | armadillo den mound | 5.33 x 5.50 x 2.17 | LARGE | 864 |  |

## Environment

The natural world: geology, flora, and fauna remains. Bulk scatter lives here. The Deadwood family is bare dead wood - no foliage and no alpha cutout anywhere in this set.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Desert Succulent Cluster | smooth-lobed succulent clump | 0.63 x 0.57 x 0.45 | TINY | 168 | none |
| Desert Scavenger Carcass | dead scavenger quadruped, curled | 1.26 x 1.70 x 0.51 | SMALL | 906 | none |
| Desert Water Bulb | bulbous water-storing succulent | 0.59 x 0.46 x 0.55 | SMALL | 242 | none |
| Desert Grazer Carcass | dead grazer lying on its side | 1.90 x 1.29 x 0.57 | SMALL | 1216 | none |
| Desert Aloe | blunt-leaf aloe clump | 0.70 x 0.66 x 0.70 | SMALL | 154 | none |
| Desert Deadwood Root | fallen dead root chunk | 1.40 x 0.66 x 0.74 | SMALL | 196 | trunk proxy |
| Desert Burrower Carcass | dead armour-plated burrower | 1.48 x 1.60 x 0.74 | SMALL | 882 | none |
| Desert Scrub Rock | rock slab with succulents growing beside it | 1.60 x 1.31 x 0.83 | SMALL | 184 | trimesh |
| Desert Agave | agave/yucca spiky rosette | 0.88 x 0.83 x 0.85 | SMALL | 168 | none |
| Desert Rock Shelf | stacked flat slabs | 2.20 x 1.72 x 0.87 | SMALL | 438 | trimesh |
| Desert Rock Outcrop | broad flat outcrop plate | 2.36 x 2.40 x 0.94 | SMALL | 382 | trimesh |
| Desert Prickly Pear | prickly pear cactus | 1.12 x 0.59 x 1.00 | SMALL | 228 | none |
| Desert Rock Boulder Pair | two rounded boulders and a low slab | 1.94 x 2.20 x 1.27 | MEDIUM | 312 | trimesh |
| Desert Rock Boulder Group | four rounded boulders | 2.60 x 1.90 x 1.44 | MEDIUM | 478 | trimesh |
| Desert Deadwood Stump | splayed dead root/stump mass | 1.90 x 1.90 x 1.51 | MEDIUM | 198 | trunk proxy |
| Desert Rock Block | blocky boulder with base rocks | 2.61 x 2.53 x 1.55 | MEDIUM | 614 | trimesh |
| Desert Rock Pile | tall angular pile, landmark | 2.70 x 2.10 x 2.10 | LARGE | 398 | trimesh |
| Desert Deadwood Snag | thick broken stump | 2.19 x 1.39 x 2.60 | LARGE | 302 | trunk proxy |
| Desert Deadwood Leaning | windswept leaning dead tree | 3.50 x 1.60 x 3.60 | HUGE | 442 | trunk proxy |
| Desert Deadwood Fork | twin-trunk dead tree | 3.41 x 2.44 x 3.90 | HUGE | 618 | trunk proxy |
| Desert Deadwood Tall | multi-limb dead tree | 2.88 x 2.08 x 4.20 | HUGE | 550 | trunk proxy |

## Housing

The settlement build kit: modular shelter pieces plus the furniture and fixtures that go inside them. Grouped by gameplay system rather than art category, so walls and workbenches sit together.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Cot | steel-framed single cot | 1.05 x 1.90 x 0.56 | SMALL | 1202 |  |
| Utility Table | small square steel utility table | 0.90 x 0.83 x 0.75 | SMALL | 944 |  |
| Workbench | steel workbench with cabinet | 1.60 x 0.98 x 0.92 | SMALL | 1639 |  |
| Shelf Unit | three-tier open steel shelving rack | 1.74 x 1.11 x 1.70 | MEDIUM | 1283 |  |
| Door Frame | modular shelter doorway | 1.34 x 0.66 x 2.00 | LARGE | 526 |  |
| Door | modular shelter door | 0.91 x 0.26 x 2.00 | LARGE | 304 |  |
| Double Wall | modular shelter wall, double width | 1.88 x 0.34 x 2.00 | LARGE | 588 |  |
| Single Wall | modular shelter wall panel | 1.20 x 0.13 x 2.00 | LARGE | 602 |  |
| Settlement Sign | blank steel signboard on a post | 2.10 x 0.76 x 2.20 | LARGE | 542 |  |
| Frontier Outpost | single-storey prefab outpost building with entry ramp | 5.23 x 5.86 x 3.40 | LARGE | 14049 |  |

## Structures

Large standalone architecture and landmarks, placed whole.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Comms Tower | communications mast | 2.13 x 1.53 x 3.00 | LARGE | 1470 |  |
| Raider Gate | raider camp gateway | 3.30 x 1.04 x 3.50 | HUGE | 1340 |  |
| Raider Watch Tower | raider lookout tower | 2.34 x 2.23 x 4.00 | HUGE | 1522 |  |
| Windmill | wind pump / windmill | 4.77 x 4.34 x 5.00 | HUGE | 1068 |  |

## Props

Manufactured set dressing, placed one at a time.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Tool Box | carryable steel toolbox | 0.55 x 0.29 x 0.35 | TINY | 590 |  |
| Supply Case | flat latched supply case | 1.00 x 0.68 x 0.42 | TINY | 326 |  |
| Fuel Jug | hand-carried fuel jug | 0.33 x 0.26 x 0.45 | TINY | 313 |  |
| Chest | latched storage chest | 0.90 x 0.61 x 0.55 | SMALL | 364 |  |
| Openable Crate | sealed container with latch and indicator | 1.00 x 0.64 x 0.59 | SMALL | 576 |  |
| Scrap Container | empty open steel container | 1.10 x 0.70 x 0.66 | SMALL | 548 |  |
| Scrap Parts Bin | open crate filled with scrap metal parts | 1.00 x 0.65 x 0.78 | SMALL | 771 |  |
| Raider Weapon Rack | raider weapon rack | 1.30 x 0.74 x 0.80 | SMALL | 578 |  |
| Frame Crate | open-topped crate in a tubular frame | 1.20 x 1.12 x 1.01 | SMALL | 433 |  |
| Satellite Box | satellite uplink box | 0.62 x 0.63 x 1.20 | MEDIUM | 521 |  |
| Generator | portable power generator | 2.00 x 1.55 x 1.30 | MEDIUM | 854 |  |
| Broken Machinery Block | wrecked industrial machine block | 1.00 x 1.84 x 1.35 | MEDIUM | 892 |  |
| Barricade | portable barricade | 1.80 x 1.20 x 1.49 | MEDIUM | 538 |  |
| Water Tank | horizontal water tank on a steel frame | 1.46 x 0.88 x 1.50 | MEDIUM | 690 |  |
| Scrap Shrine | raider scrap shrine | 2.00 x 1.32 x 2.00 | MEDIUM | 957 |  |
| Contract Terminal | contract/bounty posting obelisk | 0.83 x 0.65 x 2.00 | LARGE | 936 |  |
| Locker | upright steel locker | 0.98 x 0.84 x 2.00 | LARGE | 550 |  |
| Mission Terminal | mission dispensing terminal | 1.32 x 1.20 x 2.00 | LARGE | 878 |  |
| Raider Bone Totem | raider bone totem marker | 1.39 x 0.88 x 2.00 | LARGE | 710 |  |
| Raider Territory Mark | raider territory marker | 1.04 x 0.81 x 2.00 | LARGE | 602 |  |

## Lighting

Light fixtures. None of these carry emissive materials - the lit look has to be added in Godot with an actual light and an emissive override.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Wall Light | hooded wall-mounted lamp | 0.40 x 0.45 x 0.34 | TINY | 628 |  |
| Flood Light | adjustable floodlight on a base plate | 0.34 x 0.34 x 0.55 | SMALL | 1223 |  |
| Settlement Beacon | caged amber beacon lamp on a hex base | 0.60 x 0.62 x 1.10 | SMALL | 1749 |  |
| Light Post | standing area light | 0.46 x 0.67 x 2.00 | LARGE | 452 |  |

## Mechanical

Robots and mechanical units.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Small Circular Droid | small spherical utility robot | 0.53 x 0.60 x 0.52 | SMALL | 756 |  |

## Vehicles

Rideable vehicles.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Hover Bike | single-rider hover bike | 2.00 x 1.19 x 0.69 | SMALL | 1518 |  |

## Weapons

Player weapons, in two families: scrap-built Junk and pre-collapse Old World.

| Asset | What it is | W x D x H | Class | Tris | Collision |
|---|---|---|---|---|---|
| Old World Pistol | old-world semi-automatic pistol | 0.22 x 0.07 x 0.15 | TINY | 820 |  |
| Junk Pistol | scrap-built pistol | 0.30 x 0.09 x 0.27 | TINY | 726 |  |
| Old World Shotgun | old-world pump shotgun | 1.02 x 0.13 x 0.30 | TINY | 1060 |  |
| Old World Sniper Rifle | old-world bolt-action sniper rifle | 1.20 x 0.16 x 0.31 | TINY | 1092 |  |
| Junk Sniper Rifle | scrap-built long rifle | 1.30 x 0.10 x 0.34 | TINY | 1068 |  |
| Junk Rifle | scrap-built rifle | 1.00 x 0.15 x 0.37 | TINY | 954 |  |

## Collision guidance

Collision is deliberately **not** baked into these GLBs. Do it on the Godot side,
either in per-mesh import settings or in a wrapper scene, so the assets stay purely
visual and never need re-exporting.

- **trimesh** - the render mesh makes a good collider at these triangle counts. A
  single convex hull is wrong for the multi-boulder assets: it bridges the gaps
  between separate rocks and creates invisible walls.
- **trunk proxy** - do NOT use the render mesh. Trimesh collision over bare branches
  snags the player, and a fitted primitive on a whole-tree mesh gives a giant box.
  Place a CylinderShape3D on the trunk and leave the branches with no collision.
- **none** - small scrub and carcasses the player should walk straight through.
- Blank means not yet decided; trimesh is the sane default for hard-surface props.

## Known outstanding items

- Six assets had their UVs re-unwrapped by an early normalization pass while their
  base-colour textures stayed baked to the original UVs: `Junk Pistol`,
  `Openable Crate`, `Frame Crate`, `Locker`, `Satellite Box`, `Barricade`.
  Measured at 95.5-99.5% UV overlap with the pre-pass versions, at identical
  triangle counts. The owner has since reviewed all six and their appearance is
  acceptable, so this is recorded as provenance rather than as a defect - useful
  only if a seam ever turns up on one of them. Their raw Meshy originals no longer
  exist, so any future re-derivation means regenerating from Meshy.
- `Junk Pistol` and `Locker` carry lossy JPEG textures where every comparable prop
  carries lossless PNG, and `Junk Pistol` sits a tier lower at a 512 base map. Its
  base colour is 34.6 KB against roughly 1.7 MB for its siblings. An optional
  quality upgrade, not a fault, and visible only on close inspection. This is
  unrelated to the UV item above; an earlier note here conflated the two.
- Texture tiers are not uniform across the library. Assets from the first
  normalization pass carry a 1024 base map; the newer small props and scatter carry
  512. That is deliberate - tiering follows screen importance - but it does mean
  file sizes are not comparable between old and new entries.
- Mesh and material names inside the GLBs still carry pre-rename identifiers in
  places. Files were renamed without re-exporting, to avoid disturbing verified
  output. Rename the node in the wrapper scene, or fold it into a future pass.
