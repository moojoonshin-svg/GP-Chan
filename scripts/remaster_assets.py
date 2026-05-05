from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "assets" / "source_clean"
MASTERED_DIR = ROOT / "assets" / "source_mastered"
REPORT_PATH = MASTERED_DIR / "_remaster_report.json"


def alpha_edge_mask(alpha: Image.Image) -> Image.Image:
    expanded = alpha.filter(ImageFilter.MaxFilter(3))
    contracted = alpha.filter(ImageFilter.MinFilter(3))
    return ImageChops.subtract(expanded, contracted)


def sharpen_luminance(rgba: Image.Image) -> Image.Image:
    rgb = Image.new("RGB", rgba.size, (0, 0, 0))
    rgb.paste(rgba.convert("RGB"), mask=rgba.getchannel("A"))
    sharp = rgb.filter(ImageFilter.UnsharpMask(radius=0.8, percent=65, threshold=5))
    out = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    out.paste(sharp, mask=rgba.getchannel("A"))
    out.putalpha(rgba.getchannel("A"))
    return out


def restore_edges(original: Image.Image, sharpened: Image.Image) -> Image.Image:
    rgba = original.convert("RGBA")
    alpha = rgba.getchannel("A")
    edge = alpha_edge_mask(alpha)
    edge = edge.point(lambda value: min(180, value))

    smoothed_alpha = alpha.filter(ImageFilter.MedianFilter(3))
    out = Image.composite(sharpened, rgba, edge)
    out.putalpha(smoothed_alpha)
    return out


def remaster_image(image: Image.Image) -> tuple[Image.Image, dict[str, int | str]]:
    rgba = image.convert("RGBA")
    sharpened = sharpen_luminance(rgba)
    mastered = restore_edges(rgba, sharpened)
    if mastered.size != rgba.size:
        raise ValueError("Remaster changed canvas size.")
    return mastered, {
        "width": mastered.width,
        "height": mastered.height,
        "mode": mastered.mode,
    }


def iter_clean_pngs(sample: int | None) -> list[Path]:
    paths = sorted(
        path for path in CLEAN_DIR.rglob("*.png")
        if path.is_file()
    )
    if sample is None:
        return paths
    return paths[:sample]


def run(sample: int | None = None) -> None:
    if not CLEAN_DIR.exists():
        raise FileNotFoundError(f"Missing clean source directory: {CLEAN_DIR}. Run scripts/remove_green_and_despill.py first.")

    MASTERED_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict[str, int | str]] = {}
    for clean_path in iter_clean_pngs(sample):
        relative = clean_path.relative_to(CLEAN_DIR)
        mastered_path = MASTERED_DIR / relative
        mastered_path.parent.mkdir(parents=True, exist_ok=True)
        mastered, stats = remaster_image(Image.open(clean_path))
        mastered.save(mastered_path)
        report[str(relative).replace("\\", "/")] = stats

    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    mode = "sample" if sample is not None else "full"
    print(f"Remaster {mode}: {len(report)} files -> {MASTERED_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Conservative transparent PNG remaster that preserves canvas, pose, framing, and filenames.")
    parser.add_argument("--sample", type=int, default=None, help="Process only the first N cleaned PNG files for preview/testing.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(sample=args.sample)
