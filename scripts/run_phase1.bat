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
 echo Blender not found. Add blender.exe to PATH or run the script from Blender Scripting.
 pause
 exit /b 1
)
if not exist "source\WhisperingPines_Blockout_v01.blend" (
 echo Missing original source\WhisperingPines_Blockout_v01.blend
 echo Copy your original .blend file into source first.
 pause
 exit /b 1
)
"%BLENDER_EXE%" -b "source\WhisperingPines_Blockout_v01.blend" --python "scripts\01_island_reconstruction.py"
if errorlevel 1 (
 echo Phase 1 failed. Original source was not modified.
 pause
 exit /b 1
)
echo Saved blender\WhisperingPines_Phase1_Expanded.blend
pause
