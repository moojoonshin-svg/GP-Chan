@echo off
cd /d "%~dp0"
if not exist "assets\generated\manifest.json" (
  python scripts\build_pet_assets.py
)
start "" pythonw pet.py
