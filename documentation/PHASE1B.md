# Phase 1B: visible landmass and permanent working filename

This is an **unverified development candidate**. It does not alter the original `source/WhisperingPines_Blockout_v01.blend`.

## Changes from the earlier experiments
- Increase outer side terrain reach (up to +48%) and front reach (up to +35%), with the center protected.
- Update BOTH terrain top and underside with identical XY expansion so their seams remain aligned.
- Add 13 low-poly hanging rocks beneath the island for a more pronounced lower silhouette.
- Preserve pink floating cloud meshes, all pine trees, props, tent, bridge, water and waterfall in their existing positions.
- No automatic repositioning of 204 decorations.
- Do **not** delete suspected sub-island pieces without identification.

**Important:** The river will still be too short after a much wider terrain expansion; the next phase needs an intentional waterfall-to-edge river redesign. The current trees, bushes and tent plant clipping also require future fixes.

## Local commands

From Command Prompt:

```bat
cd /d C:\Users\vtemp\whispering_pines
git switch phase-1-island-expansion
git pull --ff-only
scripts\run_phase1b.bat
```

Open `blender/WhisperingPines_Main.blend` in Blender. New runs use the untouched original as an input, creating/replacing the **same working filename**. If an existing Main scene is present, the first run also copies it to `blender/checkpoints/WhisperingPines_Before_Phase1B.blend`. This backup is not overwritten by later runs.

## Publish the actual Blender file

This repo is configured for Git LFS but the GitHub connector cannot run a local Blender render or upload the .blend binary through a Git LFS push. To make future `git pull` update the .blend itself, push it **once after visually verifying**:

```bat
git add blender/WhisperingPines_Main.blend
git commit -m "Add reviewed Phase 1B working Blender scene"
git push origin phase-1-island-expansion
```

Once the binary is tracked by Git LFS, subsequent edits to that same file can be versioned normally using `git add`, `git commit`, and `git push`. Don't commit it until you check the terrain and bridge/water alignments.

## Verification
- [ ] Island is visibly wider and with a natural edge silhouette
- [ ] Under-island rock additions are actually attached, not dangling disconnected in space
- [ ] Camp, bridge, and waterfall have no new critical intersections
- [ ] Cloud meshes preserved
- [ ] No new accidental tent plant intersections
- [ ] Blender scene opens and renders successfully
- [ ] Sub-island identified before removal
- [ ] Only then promote as an approved scene on main
