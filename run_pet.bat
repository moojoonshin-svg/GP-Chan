@echo off
cd /d "%~dp0"
set NEED_BUILD=
if not exist "assets\source_clean\gpzz_sheet_green.png" (
  if exist "assets\source_raw_green\gpzz_sheet_green.png" (
    python scripts\remove_green_and_despill.py
    set NEED_BUILD=1
  ) else (
    echo Missing assets\source_clean. Green raw assets are not included in this repo.
    exit /b 1
  )
)
if not exist "assets\source_mastered\gpzz_sheet_green.png" (
  python scripts\remaster_assets.py
  set NEED_BUILD=1
)
if defined NEED_BUILD (
  python scripts\build_pet_assets.py
) else if not exist "assets\generated\manifest.json" (
  python scripts\build_pet_assets.py
)
start "" pythonw pet.py
