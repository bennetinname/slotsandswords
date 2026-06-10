@echo off
REM ============================================================
REM  Baut SlotsAndSwords.exe als einzelne Datei (One-File)
REM  Voraussetzung: Python + pygame + pyinstaller installiert
REM ============================================================
echo Baue SlotsAndSwords.exe ...

python -m PyInstaller ^
  --onefile ^
  --windowed ^
  --name "SlotsAndSwords" ^
  --add-data "assets;assets" ^
  --clean ^
  --noconfirm ^
  main.py

echo.
echo Fertig! Die EXE liegt in:  dist\SlotsAndSwords.exe
echo Zum Spielen einfach die EXE doppelklicken.
pause
