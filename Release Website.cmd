@echo off
setlocal EnableExtensions
title CASTR website - release
REM ---------------------------------------------------------------------------
REM  Release Website.cmd  -  double-click to publish a CASTR Spreadsheet release
REM
REM  1. Runs scripts\check_release.py (all 5 version references in
REM     spreadsheet.html must agree and the named .xlsm must be in this folder).
REM  2. Shows what will be committed and asks for confirmation.
REM  3. git add -A / git commit / git push origin
REM
REM  Nothing is committed or pushed if the check fails.
REM  See RELEASE_CHECKLIST.md for the full procedure.
REM ---------------------------------------------------------------------------
cd /d "%~dp0"

set "PY=D:\Python\python.exe"
if not exist "%PY%" set "PY=python"

echo.
echo ===== Step 1: checking spreadsheet.html =====
"%PY%" scripts\check_release.py
if errorlevel 1 (
    echo.
    echo *** CHECK FAILED - nothing was committed or pushed.
    echo *** Fix the items above, then double-click this file again.
    echo.
    pause
    exit /b 1
)

for /f "usebackq delims=" %%V in (`"%PY%" scripts\check_release.py --version`) do set "VER=%%V"
if not defined VER (
    echo *** Could not read the version from spreadsheet.html.
    pause
    exit /b 1
)

echo.
echo ===== Step 2: changes to be published =====
echo   (M = modified file,  ?? = new file,  D = deleted file  - compared with GitHub)
git status --short
if errorlevel 1 (
    echo *** git is not available or this folder is not a git repository.
    pause
    exit /b 1
)
echo.
echo Version on the page: %VER%
echo Commit message:      Release CASTR Spreadsheet %VER%
echo.
choice /c YN /n /m "Commit and push these changes to GitHub now? [Y/N] "
if errorlevel 2 (
    echo Cancelled - nothing was committed or pushed.
    pause
    exit /b 0
)

echo.
echo ===== Step 3: commit and push =====
if exist ".git\index.lock" (
    echo A stale git lock file exists: .git\index.lock
    echo If no other git program ^(GitHub Desktop, VS Code^) is open, it is safe to remove.
    choice /c YN /n /m "Remove the lock file and continue? [Y/N] "
    if errorlevel 2 (
        echo Cancelled - nothing was committed or pushed.
        pause
        exit /b 1
    )
    del /f /q ".git\index.lock"
)
git add -A
if errorlevel 1 (
    echo.
    echo *** git add failed - NOTHING was committed or pushed. Fix the error above and run again.
    pause
    exit /b 1
)
git diff --cached --quiet
if not errorlevel 1 (
    echo Nothing new to commit - the repository already matches this folder.
) else (
    git commit -m "Release CASTR Spreadsheet %VER%"
    if errorlevel 1 (
        echo *** git commit failed.
        pause
        exit /b 1
    )
)
git push origin
if errorlevel 1 (
    echo *** git push failed - check your GitHub sign-in / network and run again.
    pause
    exit /b 1
)

echo.
echo ===== Done =====
echo Pushed. GitHub Pages rebuilds in about a minute.
echo Then: in the workbook click ribbon "Check Updates" - expect version %VER%.
echo The "Spreadsheet release check" Action on GitHub must show green.
echo.
pause
exit /b 0
