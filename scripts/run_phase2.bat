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
 echo Blender not found.
 pause
 exit /b 1
)
if not exist "blender\WhisperingPines_Main.blend" (
 echo Missing working file blender\WhisperingPines_Main.blend
 echo Run scripts\run_phase1b.bat first.
 pause
 exit /b 1
)
"%BLENDER_EXE%" -b "blender\WhisperingPines_Main.blend" --python "scripts\02_water_rebuild.py"
if errorlevel 1 (
 echo Phase 2 failed. Copy the Blender console output for review.
 pause
 exit /b 1
)
echo Updated blender\WhisperingPines_Main.blend
echo Reopen or use File - Revert in Blender after saving local edits.
pause
