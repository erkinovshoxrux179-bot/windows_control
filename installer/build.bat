@echo off
REM ============================================================
REM  Windows Controller — build skripti
REM  Bir buyruq bilan: kutubxonalar -> .exe (PyInstaller) -> setup.exe (Inno Setup)
REM
REM  Ishlatish (loyiha ildizidan yoki shu papkadan ikki marta bosing):
REM      installer\build.bat
REM ============================================================
setlocal enabledelayedexpansion

REM --- Skript joylashgan papka va loyiha ildizini aniqlaymiz ---
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%.."
set "ROOT=%CD%"

echo ============================================================
echo  Windows Controller - O'rnatgich yasash
echo  Loyiha papkasi: %ROOT%
echo ============================================================
echo.

REM --- 1) Python borligini tekshiramiz ---
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi. Avval Python 3.10+ o'rnating.
    goto :error
)

REM --- 2) Kutubxonalarni o'rnatamiz ---
echo [1/4] Kutubxonalar o'rnatilmoqda...
python -m pip install --upgrade pip
python -m pip install -r "%ROOT%\requirements.txt"
python -m pip install -r "%ROOT%\requirements-build.txt"
if errorlevel 1 (
    echo [XATO] Kutubxonalarni o'rnatishda muammo.
    goto :error
)

REM --- 3) Eski build'larni tozalaymiz ---
echo.
echo [2/4] Eski fayllar tozalanmoqda...
if exist "%ROOT%\build"  rmdir /s /q "%ROOT%\build"
if exist "%ROOT%\dist"   rmdir /s /q "%ROOT%\dist"

REM --- 4) PyInstaller bilan .exe yasaymiz ---
echo.
echo [3/4] PyInstaller bilan dastur yig'ilmoqda (biroz vaqt oladi)...
python -m PyInstaller --noconfirm "%ROOT%\installer\WindowsController.spec"
if errorlevel 1 (
    echo [XATO] PyInstaller xatosi.
    goto :error
)
if not exist "%ROOT%\dist\WindowsController\WindowsController.exe" (
    echo [XATO] .exe yaratilmadi. Yuqoridagi loglarni tekshiring.
    goto :error
)

REM --- 5) Inno Setup bilan setup.exe yasaymiz ---
echo.
echo [4/4] Inno Setup bilan o'rnatgich yasalmoqda...

REM ISCC.exe ni topamiz (PATH yoki standart joylar)
set "ISCC="
where iscc >nul 2>&1 && set "ISCC=iscc"
if not defined ISCC if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    echo [XATO] Inno Setup (ISCC.exe) topilmadi.
    echo        https://jrsoftware.org/isdl.php dan o'rnating.
    echo        .exe esa tayyor: %ROOT%\dist\WindowsController\
    goto :error
)

"%ISCC%" "%ROOT%\installer\installer.iss"
if errorlevel 1 (
    echo [XATO] Inno Setup kompilyatsiya xatosi.
    goto :error
)

echo.
echo ============================================================
echo  TAYYOR! O'rnatgich:
echo  %ROOT%\installer\Output\WindowsController-Setup.exe
echo ============================================================
goto :end

:error
echo.
echo *** Build muvaffaqiyatsiz yakunlandi. ***
popd
exit /b 1

:end
popd
exit /b 0
