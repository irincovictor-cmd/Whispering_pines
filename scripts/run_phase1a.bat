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
if not exist "source\WhisperingPines_Blockout_v01.blend" (
 echo Missing source\WhisperingPines_Blockout_v01.blend
 pause
 exit /b 1
)
"%BLENDER_EXE%" -b "source\WhisperingPines_Blockout_v01.blend" --python "scripts\01a_terrain_only.py"
if errorlevel 1 (
 echo Phase 1A failed. Original scene remains unchanged.
 pause
 exit /b 1
)
echo Open blender\WhisperingPines_Phase1A_Terrain.blend
pause
