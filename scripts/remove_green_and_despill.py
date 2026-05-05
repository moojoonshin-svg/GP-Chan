from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "assets" / "source_raw_green"
CLEAN_DIR = ROOT / "assets" / "source_clean"
REPORT_PATH = CLEAN_DIR / "_despill_report.json"

NEIGHBORS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def is_background_green(r: int, g: int, b: int) -> bool:
    return g >= 135 and g > r + 35 and g > b + 35


def is_spill_green(r: int, g: int, b: int) -> bool:
    return g > 85 and g > r + 14 and g > b + 14


def find_connected_background(rgba: Image.Image) -> set[tuple[int, int]]:
    pixels = rgba.load()
    width, height = rgba.size
    background: set[tuple[int, int]] = set()
    stack: list[tuple[int, int]] = []

    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    while stack:
        x, y = stack.pop()
        if (x, y) in background:
            continue
        r, g, b, _ = pixels[x, y]
        if not is_background_green(r, g, b):
            continue
        background.add((x, y))
        for dx, dy in NEIGHBORS:
            nx = x + dx
            ny = y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in background:
                stack.append((nx, ny))
    return background


def near_background(x: int, y: int, background: set[tuple[int, int]], width: int, height: int) -> bool:
    for radius in (1, 2):
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                nx = x + dx
                ny = y + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) in background:
                    return True
    return False


def clean_image(image: Image.Image) -> tuple[Image.Image, dict[str, int]]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    background = find_connected_background(rgba)

    transparent_pixels = 0
    despilled_pixels = 0
    for x, y in background:
        pixels[x, y] = (0, 0, 0, 0)
        transparent_pixels += 1

    for y in range(height):
        for x in range(width):
            if (x, y) in background:
                continue
            r, g, b, a = pixels[x, y]
            if a and is_spill_green(r, g, b) and near_background(x, y, background, width, height):
                pixels[x, y] = (r, min(g, max(r, b) + 8), b, a)
                despilled_pixels += 1

    return rgba, {
        "transparent_pixels": transparent_pixels,
        "despilled_pixels": despilled_pixels,
    }


def iter_source_pngs(sample: int | None) -> list[Path]:
    paths = sorted(path for path in RAW_DIR.rglob("*.png") if path.is_file())
    if sample is None:
        return paths
    return paths[:sample]


def run(sample: int | None = None) -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(f"Missing raw green source directory: {RAW_DIR}")

    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict[str, int | str]] = {}
    for raw_path in iter_source_pngs(sample):
        relative = raw_path.relative_to(RAW_DIR)
        clean_path = CLEAN_DIR / relative
        clean_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned, stats = clean_image(Image.open(raw_path))
        cleaned.save(clean_path)
        report[str(relative).replace("\\", "/")] = {
            **stats,
            "width": cleaned.width,
            "height": cleaned.height,
            "mode": cleaned.mode,
        }

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    mode = "sample" if sample is not None else "full"
    print(f"Despill {mode}: {len(report)} files -> {CLEAN_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove green screen background and green spill without changing canvas geometry.")
    parser.add_argument("--sample", type=int, default=None, help="Process only the first N source PNG files for preview/testing.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(sample=args.sample)
