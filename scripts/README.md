# Blender automation

Scripts live here by phase. Each script should:

1. State compatible Blender version and required source scene path.
2. Open/modify only an explicitly named scene, avoiding global destructive operations.
3. Name generated objects deterministically.
4. Save output to a new `.blend` checkpoint, never overwrite the original in `source/`.
5. Report changes and any missing expected objects.

Phase 1 script will be reviewed and added on its own development branch after the baseline is committed.
