@echo off
setlocal
cd /d "%~dp0.."
set "BLENDER_EXE="
for %%B in (blender.exe) do if not "%%~$PATH:B"=="" set "BLENDER_EXE=%%~$PATH:B"
if not defined BLENDER_EXE (
 for /d %%D in ("C:\Program Files\Blender Foundation\Blender *") do (
  if exist "%%~fD\blender.exe" set "BLENDER_EXE=%%~fD\blender.exe"
 )
)
if not defined BLENDER_EXE (
 echo Blender executable not found.
 pause
 exit /b 1
)
if not exist "blender\WhisperingPines_Main.blend" (
 echo Working scene missing: blender\WhisperingPines_Main.blend
 pause
 exit /b 1
)
"%BLENDER_EXE%" -b "blender\WhisperingPines_Main.blend" --python "scripts\02d_edge_waterfall.py"
if errorlevel 1 (
 echo Phase 2D stopped. Please send the console error; do not rerun other water scripts.
 pause
 exit /b 1
)
echo Updated blender\WhisperingPines_Main.blend
echo In Blender: File ^> Revert (save any unsaved changes first).
pause
