# Phase 2D: edge waterfall gravity fix

The Phase 2C scene has a river that reaches the front-right edge, but its spill geometry bends under the island. This script replaces **only** the edge spill using the actual top lip vertices of `WATER_EdgeSpill`.

## Run

Save unsaved work in Blender, then:

```bat
cd /d C:\Users\vtemp\whispering_pines
git switch phase-1-island-expansion
git pull --ff-only
scripts\run_phase2d.bat
```

Open or File > Revert the existing `blender/WhisperingPines_Main.blend`.

## Safety and scope

- A backup is copied to `blender/checkpoints/WhisperingPines_Before_Phase2D.blend`.
- The old deformed `WATER_EdgeSpill` is hidden, not deleted.
- Creates `WP2D_Edge_Waterfall` collection with one gravity-led cascade and a thin white foam lip.
- Does not edit the main river, upper waterfall, terrain, clouds, trees, tent, bridge or cameras.
- Verifies that the lip has usable width and is near original river geometry.
- Refuses to rerun over a Phase 2D result or overwrite the original backup.

## Verify before approval

Inspect the front-right outlet from the front and side with materials visible. The edge sheet should fall substantially straight down beneath its own lip, with only a tiny outward drift. Verify the river/waterfall connection. The upper cliff waterfall still needs a separate art-direction pass.

This script has NOT been executed/rendered by the assistant's environment. If Blender reports an error, share its full console output before trying other repairs.
