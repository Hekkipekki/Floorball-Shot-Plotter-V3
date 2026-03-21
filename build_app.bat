@echo off
setlocal enabledelayedexpansion

REM === Bygginställningar ===
set APP_NAME=FloorballShotPlotter
set MAIN_SCRIPT=main.py
set ICON_PATH=Resources\Icons\Icon.ico
set VERSION=3.0

REM === Tidsstämpel för zip-filen ===
for /f %%a in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set DATESTAMP=%%a
set ZIP_NAME=%APP_NAME%_v%VERSION%_%DATESTAMP%.zip

set DIST_DIR=dist\%APP_NAME%
set RELEASE_DIR=release

cd /d %~dp0
echo 🔧 Building %APP_NAME% v%VERSION%...

REM === 1. Kontrollera PyInstaller ===
where pyinstaller >nul 2>nul
if errorlevel 1 (
    echo ⬇️ Installing PyInstaller...
    pip install pyinstaller
)

REM === 2. Rensa gamla builds ===
echo 🧹 Cleaning previous builds...
if exist build (rmdir /s /q build)
if exist dist (rmdir /s /q dist)
if exist %RELEASE_DIR% (rmdir /s /q %RELEASE_DIR%)
if exist %ZIP_NAME% (del /f /q %ZIP_NAME%)

REM === 3. Bygg i onedir-läge ===
echo 🔨 Compiling with PyInstaller...
pyinstaller --onedir --windowed ^
 --icon="%ICON_PATH%" ^
 --name="%APP_NAME%" ^
 %MAIN_SCRIPT%

REM === 4. Kopiera resurser manuellt (fallback) ===
echo 📁 Copying resource folders manually (fallback)...
for %%F in (Resources Games Images CSV Videoklipp) do (
    if exist "%%F" (
        echo   ✅ Found %%F – copying...
        xcopy /s /e /y /i "%%F" "%DIST_DIR%\%%F" >nul
    ) else (
        echo   ⚠️ Skipping %%F – not found.
    )
)

REM === 5. Verifiera .exe ===
if not exist "%DIST_DIR%\%APP_NAME%.exe" (
    echo ❌ Build failed – .exe not found!
    pause
    exit /b
)

REM === 6. Förbered release ===
echo 📦 Creating release folder...
mkdir %RELEASE_DIR%
xcopy /s /e /y /i "%DIST_DIR%\*" "%RELEASE_DIR%\" >nul

echo %APP_NAME% v%VERSION% > %RELEASE_DIR%\version.txt
echo Built: %DATESTAMP% >> %RELEASE_DIR%\version.txt
echo Double-click %APP_NAME%.exe to launch. >> %RELEASE_DIR%\README.txt

REM === 7. Lista kritiska filer
echo 📄 Verifying key runtime files...
dir "%RELEASE_DIR%\python*.dll"
dir "%RELEASE_DIR%\%APP_NAME%.exe"

REM === 8. Skapa zip
echo 📦 Zipping release...
powershell -Command "Compress-Archive -Path '%RELEASE_DIR%\*' -DestinationPath '%ZIP_NAME%'" >nul

REM === 9. Klar!
echo ✅ DONE! Created: %ZIP_NAME%
start "" "%RELEASE_DIR%"
pause
endlocal
