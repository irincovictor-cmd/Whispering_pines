# Production workflow

## Design constraints
- Preserve the current stylized low-poly fantasy aesthetic.
- Keep waterfall as a focal point; preserve campsite, bridge and camera composition unless reviewed.
- Make natural variation through geometry/silhouettes, not color alone.
- Avoid destructive broad object deletions or global rescaling.
- Use deterministic names / prefixes for script-generated objects.

## Branch policy
- `main`: approved, opened and verified in Blender.
- `phase-1-island-expansion`, `phase-2-environment-variation`, etc.: work in progress.
- Review changes visually before merging.
- Commit source scripts and relevant modified scene together.
- Tag approved milestones `v0.1-baseline`, `v0.2-phase1`, etc.

## Phase checklist
1. Inspect Blender Outliner and mesh bounds; record planned edits.
2. Make an immutable backup of the original scene.
3. Implement one limited scope in Python or Blender.
4. Run with Blender and save into a *new* scene path.
5. Inspect from top/front/bottom, preview materials and lighting.
6. Verify no missing objects, broken modifiers or external dependencies.
7. Capture before/after screenshots; only then approve merge.
8. Keep notes in the changelog.

## Phase 1 acceptance criteria
- Expanded main island toward front and sides, aiming for about 25–35% more usable footprint.
- Central campsite and waterfall remain visually recognizable.
- Bridge remains properly anchored; water connections aren't visibly broken.
- Smaller island removed only after verifying which mesh(es) compose it.
- Terrain top and underside remain joined visually.
- Original baseline remains unchanged.
- Script can be safely rerun or explains its output/rollback procedure.
- Opened and visually checked in Blender 5.x before promotion to `main`.

## Blender local workflow
```powershell
git switch main
git pull --ff-only
git lfs pull
```
Open the .blend. After pulling while the same scene is open, save any local edits elsewhere and use File > Revert.

## Git LFS
Run `git lfs install` before the first binary commit. `.gitattributes` tracks .blend files in LFS. Avoid large history of unnecessary render outputs; Git LFS still consumes storage/bandwidth over time.
