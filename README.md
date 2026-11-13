# Whispering Pines — Blender 3D Environment

A stylized low-poly floating forest island featuring a campsite, pine trees, a waterfall, a bridge, and environmental animation.

## Development approach

This repository is the **single source of truth** for the Blender project, procedural Python scripts, visual references, approved renders, and documentation.

We work incrementally:
1. Inspect and preserve the baseline Blender scene.
2. Implement one phase on a dedicated branch.
3. Open the result in Blender and visually verify geometry, materials, and animations.
4. Commit scripts and a tested Blender checkpoint.
5. Merge approved changes to `main`.

See [the development workflow](documentation/WORKFLOW.md).

## Roadmap

| Phase | Scope | Status |
| --- | --- | --- |
| 1 | Expand main island, remove identifiable sub-island, retain waterfall focal point | Planned |
| 2 | Distinct rock, bush, and plant variations | Planned |
| 3 | Under-island cliffs, roots, vines, moss | Planned |
| 4 | Animated river, waterfall, foam, and ripples | Planned |
| 5 | Animated fire, lighting, embers, subtle environmental motion | Planned |
| 6 | Lighting, camera work, 5 renders and a 10–20 second MP4 | Planned |
| 7 | Verification, cleanup and documentation | Planned |

## Layout

- `blender/` — current working scene and approved checkpoints (Git LFS)
- `source/` — immutable baseline scene, added once through Git LFS
- `scripts/` — reproducible Blender Python scripts and Windows launchers
- `assets/` — source textures/models (respect asset licenses)
- `renders/` — selected preview and final images
- `animation/` — final deliverable videos, preferably releases if large
- `documentation/` — design rules, progress and production notes

## First local setup

Install [Git](https://git-scm.com/), [Git LFS](https://git-lfs.com/), and Blender. Then:

```powershell
git lfs install
git clone https://github.com/irincovictor-cmd/Whispering_pines.git
cd Whispering_pines
git lfs pull
```

**Initial baseline status:** The original `.blend` file has not yet been uploaded to this repository. Do not run a Phase 1 script against a guessed scene path; first install the original in `source/WhisperingPines_Blockout_v01.blend` and commit it using Git LFS.

## Pulling changes while Blender is open

Save your local work before pulling. Run `git pull` and `git lfs pull`, then in Blender use **File → Revert** (or open the updated `.blend` file). Revert discards uncommitted in-memory Blender edits.

## Important safeguards

- Never overwrite the original `source/` baseline.
- Scripts should only alter named/managed objects and be safe to rerun when practical.
- Do not promote a modified `.blend` to `main` before visually testing it in Blender.
- Never commit generated `.blend1` backups, temporary renders, caches, or private data.
