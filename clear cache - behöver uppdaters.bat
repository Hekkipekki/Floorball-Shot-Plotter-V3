@echo off
echo Rensar alla __pycache__-mappar i projektet...

set "PROJECT_DIR=C:\Users\danno\Hämtade filer\Floorball Shot Plotter V3"

REM Använd pushd för att byta till katalog och säkerställa sökvägen hanteras rätt
pushd "%PROJECT_DIR%"

REM Radera alla __pycache__-mappar rekursivt
for /f "delims=" %%d in ('dir /ad /b /s __pycache__') do (
    echo Tar bort "%%d"
    rmdir /s /q "%%d"
)

popd

echo Klart!
pause
