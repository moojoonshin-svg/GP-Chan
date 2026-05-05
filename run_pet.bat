@echo off
cd /d "%~dp0"
set NEED_BUILD=
if not exist "assets\source_mastered\gpzz_sheet_green.png" (
  if not exist "assets\source_clean\gpzz_sheet_green.png" (
    if exist "assets\source_raw_green\gpzz_sheet_green.png" (
      python scripts\remove_green_and_despill.py
    ) else (
      echo Missing assets\source_mastered. Build source assets are not included.
      exit /b 1
    )
  )
  if exist "assets\source_clean\gpzz_sheet_green.png" (
    python scripts\remaster_assets.py
    set NEED_BUILD=1
  ) else (
    echo Missing assets\source_clean. Remaster source could not be prepared.
    exit /b 1
  )
)
if defined NEED_BUILD (
  python scripts\build_pet_assets.py
) else if not exist "assets\generated\manifest.json" (
  python scripts\build_pet_assets.py
)
start "" pythonw pet.py
