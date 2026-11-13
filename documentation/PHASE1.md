# Phase 1 — Balanced island expansion

**Branch:** `phase-1-island-expansion` (work in progress, not approved).

## Objective
Expand the main floating island roughly 30% toward its outer sides and 26% toward the campsite-facing front. Keep the waterfall-facing rear nearly unchanged. Preserve the waterfall, campfire, bridge, camera and lighting objects.

## Run locally
1. Ensure Git LFS is installed and your original `WhisperingPines_Blockout_v01.blend` is in `source/`.
2. Open a terminal at the repository root and run `git switch phase-1-island-expansion`, then `git pull --ff-only`.
3. Close the working scene or save changes before running this phase.
4. Double-click `scripts/run_phase1.bat`. Alternatively, open the original in Blender and run `scripts/01_island_reconstruction.py` in Blender's Scripting workspace.
5. Open `blender/WhisperingPines_Phase1_Expanded.blend` and inspect top/front/underside views.
6. Inspect `blender/WhisperingPines_Phase1_report.json` for disconnected terrain components and moved decorations.

**Safety:** script refuses to overwrite an existing checkpoint and will not delete unnamed sub-island geometry. It only deletes explicitly identifiable `sub_island` objects or those marked with `whispering_pines_sub_island`. If a disconnected sub-island survives, mark the relevant object in Blender and revise the cleanup after visual review.

**Verification pending:** Blender was not available in the tool runtime, so this scene output hasn't been executed or visually tested. Do not merge the scene checkpoint to `main` until you inspect it.

## Acceptance checklist
- [ ] Terrain appears larger without stretching the center
- [ ] Campfire, river and waterfall align
- [ ] Bridge remains anchored
- [ ] Sub-island is gone (if separately identified)
- [ ] New edge vegetation is grounded on the terrain
- [ ] Underside stays aligned with top mesh
- [ ] No missing materials / Blender errors
- [ ] Approved checkpoint committed with Git LFS
