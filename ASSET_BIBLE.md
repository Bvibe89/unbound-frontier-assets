# Unbound Frontier Asset Bible

This repository is the source workspace for Unbound Frontier art and game assets. The goal is consistency, readability, and a production pipeline that a very small team can sustain.

## Visual Direction

Unbound Frontier uses a stylized low-poly, PS2-era science-fiction aesthetic.

Core principles:
- Function over graphics.
- Strong, readable silhouettes matter more than tiny surface detail.
- Prefer broad, chunky shapes over dense greebling.
- Avoid photorealism and modern AAA-style micro-detail.
- Materials should be simple, restrained, and readable at third-person gameplay distance.
- Slight asymmetry and rugged utilitarian construction are encouraged where appropriate.
- Assets should feel like they belong to the same world rather than looking like unrelated AI generations.

## Design Continuity

When creating or modifying an asset:
- Preserve the approved silhouette unless explicitly asked to redesign it.
- Do not randomly add or remove major components between revisions.
- Maintain proportions across reference views and iterations.
- Reuse established shape language, material language, and construction logic within an asset family.
- Related props, weapons, buildings, creatures, and machines should look like they were made by the same world/art pipeline.

## Geometry

Triangle targets are guidelines, not hard limits. Use the lowest complexity that preserves the intended silhouette and gameplay readability.

General guidance:
- Small clutter and simple props: very low poly.
- Standard environment props: low poly, with complexity concentrated in silhouette-changing areas.
- Large buildings and structures: modular geometry preferred over dense single meshes.
- Weapons: enough geometry for a readable third-person silhouette, but avoid unnecessary tiny detail.
- Characters and creatures: reserve geometry for deformation, silhouette, hands/feet/head, and recognizable anatomy.
- Hero assets may exceed normal budgets when justified, but only deliberately.

Do not retain high-density generated topology just because Meshy produced it. Generated assets should be remeshed, simplified, or rebuilt where necessary.

## Scale and Orientation

- Use metric scale.
- Final exported assets must have predictable real-world scale.
- Grounded props should have a useful origin at or near their ground-contact base unless the asset requires another pivot.
- Apply transforms before final export unless there is a specific reason not to.
- Keep orientation consistent across related assets.

## Grounded Asset Scale Standard

All creatures, characters, and large props must use believable physical proportions, grounded in a single consistent real-world scale anchor.

**Scale anchor:** average human height ≈ 1.78 m (5'10").

**Visual scale classes** (shorthand labels only — they carry no implication about combat difficulty, boss status, HP, strength, or rarity):

- TINY: under 0.5 m
- SMALL: 0.5–1.2 m
- MEDIUM: 1.2–2.0 m
- LARGE: 2.0–3.5 m
- HUGE: 3.5–6.0 m
- MASSIVE: over 6.0 m

**Critical rule: never choose a class first.** Do not pick a size class and then enlarge or shrink an asset to fit it. Determine scale in this order:

1. Intended creature/object function.
2. Real-world analogy, when one exists.
3. Plausible explicit dimensions in meters.
4. Only then assign the nearest scale-class label, as shorthand.

Examples:

- "Human-sized" stays around realistic human dimensions.
- "Camel-sized" uses plausible camel-like dimensions, not an inflated size merely because LARGE sounds appropriate.
- A small predator stays genuinely small unless its design explicitly calls for something bigger.
- HUGE should visually feel enormous beside a 1.78 m human, not merely somewhat taller.

**Owner-specified analogies take priority.** When the owner gives an explicit comparison (dog-sized, human-sized, camel-sized, horse-sized, elephant-sized, etc.), that comparison overrides the generic class bands unless the owner explicitly changes it.

**Record explicit dimensions before modeling.** For every creature/character/large-prop spec, capture the measurements that actually describe its footprint:

- Upright humanoid/biped: standing height.
- Quadruped/transport creature: shoulder height + body length.
- Long/low creature: body length + body height.
- Flying creature: body length + wingspan.
- Unusually shaped assets: whatever dimensions are needed to understand its actual footprint.

Example record:

`Shoulder height: 1.9 m | Body length: 2.8 m | Scale class: LARGE | Analogy: camel-sized`

The explicit dimensions and approved analogy are authoritative. The TINY/SMALL/MEDIUM/LARGE/HUGE/MASSIVE label is shorthand only, never the source of truth.

Measured dimensions for shipped assets are recorded in `ASSET_INDEX.md`.

**Verify before finalizing.** Before finalizing a model, compare it against a 1.78 m human reference placed in the Blender scene, to catch accidental scale drift.

## Materials and Textures

- Prefer simple material setups.
- Avoid unnecessary material slots.
- Texture resolution should be appropriate to the asset's screen importance; bigger is not automatically better.
- Generated 2K textures are acceptable as source material, but may be reduced or repacked for final game use.
- PBR maps should only be retained when they contribute meaningfully to the intended look.
- Do not create modern hyper-real surface complexity that conflicts with the PS2-era stylization.

## Mesh Quality

Before an asset is considered game-ready, check for:
- obvious holes or unintended open geometry,
- loose or floating geometry,
- accidental internal geometry,
- broken normals,
- unusable topology,
- extreme polygon density,
- bad origins or transforms,
- duplicate unnecessary material slots,
- unexpected scale,
- obvious generation artifacts.

Do not silently redesign an asset while repairing it.

## Asset Families

`GLB/` is organised by **gameplay system where one exists, and by art family where
one does not**. That is why walls and workbenches sit together under Housing: the
game treats them as one build kit, and splitting them by art category would break
up something the player experiences as a unit.

- `Characters` - player and humanoid rigs
- `Creatures` - living fauna
- `Creature Lairs` - burrows, dens and nests
- `Environment` - the natural world: geology, flora, fauna remains. Bulk scatter.
- `Housing` - the settlement build kit: modular shelter pieces plus the furniture
  and fixtures that go inside them
- `Structures` - large standalone architecture and landmarks, placed whole
- `Props` - manufactured set dressing, placed one at a time
- `Lighting` - light fixtures
- `Mechanical` - robots and mechanical units
- `Vehicles` - rideable vehicles
- `Weapons` - player weapons

The dividing line between Environment and Props is **natural versus manufactured**,
not indoor versus outdoor. The line between Structures and Props is whether the
asset is architecture you place whole, or an object you dress a scene with.

Shipped assets and their measured dimensions are recorded in `ASSET_INDEX.md`.

Do not flatten an established folder taxonomy without approval. Folder renames
break Godot resource paths exactly as file renames do, so settle a family's home
before its assets are placed in scenes.

## Creature and Character Considerations

Humanoids and creatures may use different anatomy standards. Do not assume every creature has humanoid limbs or proportions.

For rigged assets:
- Preserve consistent bone naming and hierarchy once a standard has been approved.
- Do not invent a new rig convention per asset.
- Keep deformation simple and reliable rather than sophisticated for its own sake.

## Export

Preferred game-ready interchange format: GLB.

Final exports should:
- open correctly in Blender,
- import cleanly into Godot,
- use sane transforms,
- contain only intended geometry/materials,
- have meaningful filenames,
- avoid embedding temporary test junk.

Raw/source files belong in source folders; approved game exports belong in the GLB hierarchy.

## Naming

Use descriptive, stable names.

**Format: Title Case With Spaces.** This is the established convention across the
library and matches the shipped assets. Godot handles spaces in resource paths
without issue.

Prefer names such as:
- `Mission Terminal.glb`
- `Raider Watch Tower.glb`
- `Desert Rock Outcrop.glb`
- `Human Base v4 Rigged.blend`

Avoid filenames such as:
- final_final2,
- random UUIDs,
- Untitled,
- New Object,
- names truncated mid-word,
- vague names with no category meaning.

**Name for what the asset is, not how big it is.** A shape or function word
(Outcrop, Shelf, Snag, Boulder, Stump) communicates an asset's role and its
believable size far better than a size word does, and it does not go stale when
the size is revised. "Small" in a filename ages badly and tells a level designer
nothing useful.

**Name for what it actually is, not what it resembles.** Bare dead wood is
Deadwood, not Tree; otherwise the name a living tree will need is already taken.

**Variants should be intentional and clearly named.** Prefer a distinguishing
word over a letter wherever a natural one exists. Two rules for variant sets:
- Do not keep a bare base name alongside lettered variants (`Desert Tree`
  together with `Desert Tree A`). It is then ambiguous whether the bare name
  belongs to the series.
- Never reuse an existing name for a different asset, including mid-way through
  a rename pass.

**Names are load-bearing once an asset is placed.** Godot scenes reference assets
by file path, so renaming after placement breaks those references. Settle the
name before an asset goes into a scene: renaming is nearly free beforehand and
expensive afterwards.

## Final Principle

The asset pipeline exists to make a coherent game, not to preserve every generated result. Generated content is raw material. Keep what serves the game, simplify aggressively where appropriate, and protect approved designs from unnecessary drift.
