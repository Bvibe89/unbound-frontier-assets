# Unbound Frontier Asset Pipeline

This repository is the production workspace for Unbound Frontier assets. It is separate from the main Godot game repository.

## Pipeline Overview

Preferred flow:

1. Concept / reference
2. Meshy generation or manual Blender creation
3. Raw source preservation
4. Blender cleanup and optimization
5. Validation
6. GLB export
7. Review / approval
8. Copy or integrate approved GLB into the main game repository when needed

Do not skip source preservation when a generated asset may need to be repaired later.

## Folder Intent

Recommended top-level roles:
- `Concept Art` — approved or exploratory visual references
- `Reference` — miscellaneous references, source images, and comparison material
- `Raw Meshy` — untouched or minimally renamed Meshy outputs, including failed/WIP generations worth keeping
- `Blender Source` — `.blend` working files and cleanup/rebuild sources
- `GLB` — cleaned, exported, game-ready or review-ready GLBs organized by category
- `Textures` — source or processed textures not embedded in a source file
- `Sounds` — audio source/game-ready sound assets

Existing more granular subfolders under `GLB` may be retained. Do not flatten or restructure them without approval.

## Meshy Rules

Meshy output is considered source material, not automatically game-ready.

When generating through Meshy:
- Follow the approved visual direction in `ASSET_BIBLE.md`.
- Avoid excessive AAA detail and dense greebling.
- Prefer readable silhouettes and simple construction.
- Keep generation batches deliberate to avoid unnecessary credit usage.
- Do not repeatedly regenerate large batches without approval.
- Preserve useful raw outputs in `Raw Meshy` before destructive cleanup.

If Meshy produces holes, broken geometry, bad topology, or incorrect details, repair or rebuild in Blender rather than hiding the issue.

## Blender Cleanup

Typical cleanup checklist:
- inspect the entire mesh before editing,
- confirm scale and intended dimensions,
- repair obvious holes where practical,
- remove stray/loose/unintended geometry,
- remove obvious internal junk,
- correct normals,
- simplify/remesh/retopologize when generated density is excessive,
- reduce unnecessary material slots,
- preserve approved silhouette and proportions,
- set an appropriate origin/pivot,
- apply transforms when appropriate,
- validate UV/material behavior,
- save a `.blend` source before final export.

Do not use destructive operations on the only copy of a raw generated asset.

## Optimization

Optimization is asset-dependent. Do not apply a single triangle target to everything.

Priorities:
1. Preserve silhouette.
2. Preserve important gameplay readability.
3. Remove invisible or unnecessary complexity.
4. Keep topology sufficient for animation/deformation where required.
5. Prefer reusable modular pieces for large environment sets.

For generated static props, aggressive simplification is usually acceptable when the visible result remains intact.

## Textures and Materials

- Generated textures may be retained as source material even if final game resolution is lower.
- Do not assume every available PBR map is required.
- Keep final materials simple and consistent with the stylized PS2-era direction.
- Avoid multiplying material slots unnecessarily.
- Keep source textures separate from final exports when doing so improves maintainability.

## Export Validation

Before placing an asset into `GLB`, verify:
- correct object is exported,
- sane scale,
- sane orientation,
- useful origin/pivot,
- no temporary helpers/cameras/lights unless intentionally required,
- no obvious mesh defects,
- no unnecessary high-density hidden geometry,
- materials survive export,
- GLB reopens/imports successfully,
- filename is descriptive and follows project naming conventions.

## Raw vs Final

Raw assets and final assets serve different purposes.

Never replace a raw source merely because a cleaned version exists. Keep source assets where practical until the final asset is proven stable.

A file in `GLB` should represent a deliberate export, not an untouched random generation.

## Git and Git LFS

Large binary asset formats should follow the repository `.gitattributes` LFS rules.

General workflow:
- inspect `git status`,
- review generated/modified files,
- avoid staging caches, autosaves, temp files, or failed bulk generations unless intentionally archived,
- show the user a concise commit summary before committing,
- do not push without explicit approval.

Do not use Git commits as a substitute for keeping source and final folders organized.

## Main Game Repository Boundary

This repository is an asset workshop. The main Godot project is separate.

Do not modify the main Godot repository from this workspace unless explicitly instructed.

Only approved assets should move into the game repo. The game repo should not become a dumping ground for raw Meshy generations, Blender experiments, rejected assets, or high-resolution working files.

## World-Building Intent

Environment production should favor modularity and reuse.

Preferred approach:
- build reusable prop/building kits,
- graybox important layouts first in the game,
- use procedural or automated dressing for repetitive clutter,
- keep important combat/traversal/landmark placement intentional,
- avoid creating every building as a unique one-off asset.

## Final Principle

The pipeline should reduce repetitive labor without giving up art direction. AI tools generate and process assets; the project rules decide what belongs in the game.
