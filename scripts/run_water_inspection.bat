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
 echo Missing blender\WhisperingPines_Main.blend
 pause
 exit /b 1
)
"%BLENDER_EXE%" -b "blender\WhisperingPines_Main.blend" --python "scripts\inspect_water_scene.py"
if errorlevel 1 (
 echo Inspection failed. Copy the error output.
 pause
 exit /b 1
)
echo Inspection complete. No Blender scene was modified.
echo Report: documentation\inspections\WhisperingPines_WaterGeometry_Report.json
pause
