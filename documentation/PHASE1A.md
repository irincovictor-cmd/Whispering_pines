# Phase 1A — Terrain-only rebuild (unverified)

This supersedes the **first test**, `scripts/run_phase1.bat`, which moved 204 unrelated objects and gave visible clipping. **Do not run the old script again.**

## Run locally

From `C:\Users\vtemp\whispering_pines`:

```bat
git switch phase-1-island-expansion
git pull --ff-only
scripts\run_phase1a.bat
```

The new script always loads `source/WhisperingPines_Blockout_v01.blend` and creates `blender/WhisperingPines_Phase1A_Terrain.blend`, without overwriting the original or the old Phase 1 result. It refuses to overwrite an existing Phase 1A file.

## Changes

- Expand only main island terrain top and underside: +22% toward far sides, +19% toward front, +2% near waterfall rear (maximum local edge offsets, not total area gain).
- Preserve inner 42% of layout to minimize central campsite distortion.
- Add subtle depth-dependent unevenness to existing underside vertices, without creating separate floating spikes.
- Move **zero** trees, bushes, water meshes, tent objects, bridge objects, cameras, or lights.
- Report disconnected terrain mesh components with centers, but do not delete unidentified 'sub-island' geometry.

## What remains unresolved

This is a *terrain review candidate*, **not an approved final scene**. Waterfall segmentation, short river, pine silhouettes, stone-shaped bushes, tent vegetation, and hanging vines are separate follow-up tasks. Because water and decorations are intentionally untouched, parts may not yet align with the newly expanded terrain. The screenshot-based review is required.

## Inspection

Check top/front/bottom in Blender and inspect `blender/WhisperingPines_Phase1A_report.json` for disconnected components. Compare with original file; do not commit a generated .blend to main until verified.
