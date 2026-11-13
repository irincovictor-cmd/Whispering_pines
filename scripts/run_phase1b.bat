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
if not exist "source\WhisperingPines_Blockout_v01.blend" (
 echo Missing source\WhisperingPines_Blockout_v01.blend
 pause
 exit /b 1
)
"%BLENDER_EXE%" -b "source\WhisperingPines_Blockout_v01.blend" --python "scripts\01b_visible_landmass.py"
if errorlevel 1 (
 echo Blender script failed. Please copy this error output into ChatGPT.
 pause
 exit /b 1
)
echo Created blender\WhisperingPines_Main.blend
echo Open the scene to visually inspect before committing.
pause
