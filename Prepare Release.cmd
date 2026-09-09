@echo off
setlocal EnableExtensions
title CASTR website - prepare release
REM ---------------------------------------------------------------------------
REM  Prepare Release.cmd  -  double-click to put a new CASTR Spreadsheet version
REM  on the website. It asks for the version number, then:
REM    1. copies "CASTR Spreadsheet <ver>.xlsm" into this folder
REM       (from here or from D:\aShare\Claude\Projects\PRBE Excel)
REM    2. removes the previous version's .xlsm
REM    3. rewrites every version reference in spreadsheet.html
REM    4. runs the consistency check
REM    5. hands over to "Release Website.cmd" to commit and push
REM  Nothing is pushed until you answer Y in the final step.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"

set "PY=D:\Python\python.exe"
if not exist "%PY%" set "PY=python"

echo.
for /f "usebackq delims=" %%V in (`"%PY%" scripts\check_release.py --version`) do set "CUR=%%V"
echo Version currently on the website page: %CUR%
echo The release file must be saved as:  CASTR Spreadsheet ^<version^>.xlsm
echo (in this folder or in D:\aShare\Claude\Projects\PRBE Excel)
echo.
set "VER="
set /p "VER=New version number (e.g. 75.1.0), or Enter to cancel: "
if not defined VER (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo ===== Updating files for %VER% =====
"%PY%" scripts\set_version.py %VER%
if errorlevel 1 (
    echo.
    echo *** Preparation failed - nothing was changed on GitHub. Fix the error above and run again.
    pause
    exit /b 1
)

echo.
call "Release Website.cmd"
exit /b %errorlevel%
