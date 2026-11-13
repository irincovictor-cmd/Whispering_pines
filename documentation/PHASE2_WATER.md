# Phase 2 — Continuous water prototype (review required)

This script builds a separate non-destructive replacement water collection inside the **existing** `blender/WhisperingPines_Main.blend`. It preserves the original named WATER objects in a hidden archive.

## Run on Windows

```bat
cd /d C:\Users\vtemp\whispering_pines
git switch phase-1-island-expansion
git pull --ff-only
scripts\run_phase2.bat
```

The stable working filename stays `blender/WhisperingPines_Main.blend`, as requested. A safety copy of the pre-water scene is saved to `blender/checkpoints/WhisperingPines_PreWater_Phase1B.blend` before it is overwritten. **Close the scene in Blender or save your unsaved edits first.** Open it again after running, or use File > Revert.

## Scope
- Preserve all existing clouds, trees, rocks, terrain, tent, bridge, and lights.
- Replace the visible original water with a single full waterfall ribbon, connector toward pool, and continuous curving river.
- Find river direction from pond toward bridge, then locate the approximate island edge using terrain raycasts.
- Add animated noise colors (shader animation, **not** fluid simulation).
- Save `blender/WhisperingPines_Phase2_Water_Report.json` with diagnostic values.

## Important limitations
1. This is a **procedural prototype**. The current Phase 1B scene is not available here for executing or rendering the water changes. Correct contact, width, bank geometry and water physics require checking in Blender.
2. River channel excavation is **not** yet implemented. A surface might sit over or intersect the terrain. The script reports uphill sections instead of pretending they flow physically.
3. The waterfall might need a sculpted plunge pool or cliff adjustment to look natural.
4. If you run again on an already modified Main, the script **stops safely** when it finds `WP2_Continuous_Water`. Restore the backup before retrying.
5. Do not commit the scene to `main` until reviewed and approved.

## What to send for review
A screenshot with Material Preview enabled, another from above showing stream to front edge, and the numerical console/report output. Verify that the river actually passes under the bridge and terminates at the rim. If terrain clips or flow goes in the wrong direction, use the report and screenshots to fix the geometry.
