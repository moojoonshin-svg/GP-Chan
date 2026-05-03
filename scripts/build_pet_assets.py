from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source" / "gpzz_sheet_green.png"
OUTPUT = ROOT / "assets" / "generated"
FRAMES_DIR = OUTPUT / "frames"
SPRITE_SHEET = OUTPUT / "sprite_sheet.png"
MANIFEST = OUTPUT / "manifest.json"
REAL_SHEETS_DIR = ROOT / "assets" / "source" / "real_frames"
CELL_SIZE = 160
GRID_COLS = 5
GRID_ROWS = 2
ALPHA_CUTOFF = 12
HARD_ALPHA_THRESHOLD = 96
SOURCE_ACTION_NAMES = [
    "idle",
    "wave",
    "typing",
    "sweep",
    "sleep",
    "pout",
    "surprise",
    "think",
    "cheer",
    "sit",
]
SPECIAL_ACTION_NAMES = ["half_right", "welcome_agi", "agi_box"]
ACTION_NAMES = [*SOURCE_ACTION_NAMES, "walk", *SPECIAL_ACTION_NAMES]
REAL_FRAME_ACTIONS = {
    "idle": "idle_sheet_green.png",
    "wave": "wave_sheet_green.png",
    "typing": "typing_sheet_green.png",
    "sweep": "sweep_sheet_green.png",
    "sleep": "sleep_sheet_green.png",
    "pout": "pout_sheet_green.png",
    "surprise": "surprise_sheet_green.png",
    "think": "think_sheet_green.png",
    "cheer": "cheer_sheet_green.png",
    "sit": "sit_sheet_green.png",
    "walk": "walk_sheet_green.png",
}
SPECIAL_DISPLAY_NAMES = {
    "half_right": "Half Right",
    "welcome_agi": "Welcome AGI",
    "agi_box": "AGI Box",
}
SPECIAL_DURATIONS = {
    "half_right": 260,
    "welcome_agi": 160,
    "agi_box": 220,
}
FONT_FILES = [
    Path("C:/Windows/Fonts/H2SA1M.TTF"),
    Path("C:/Windows/Fonts/HMKMAMI.TTF"),
    Path("C:/Windows/Fonts/malgunbd.ttf"),
]


@dataclass(frozen=True)
class PoseMotion:
    x: tuple[int, ...]
    y: tuple[int, ...]
    rotation: tuple[float, ...]
    scale_x: tuple[float, ...]
    scale_y: tuple[float, ...]
    shadow: tuple[float, ...]


MOTIONS: dict[str, PoseMotion] = {
    "idle": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, -1, -1, 0, 0, -1, -1),
        rotation=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.0, 1.01, 1.01, 1.0, 1.0, 1.01, 1.01),
        shadow=(1.0, 1.0, 0.98, 0.98, 1.0, 1.0, 0.98, 0.98),
    ),
    "wave": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, -1, -1, 0, 0, -1, -1),
        rotation=(0.0, 0.0, 1.0, 1.0, 0.0, 0.0, -1.0, -1.0),
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.0, 1.01, 1.01, 1.0, 1.0, 1.01, 1.01),
        shadow=(1.0, 1.0, 0.98, 0.98, 1.0, 1.0, 0.98, 0.98),
    ),
    "typing": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, 0, 1, 0, 0, 0, 1),
        rotation=(0.0,) * 8,
        scale_x=(1.0,) * 8,
        scale_y=(1.0,) * 8,
        shadow=(1.0,) * 8,
    ),
    "sweep": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, -1, -1, 0, 0, -1, -1),
        rotation=(-1.0, -1.0, 1.0, 1.0, 0.0, 0.0, -1.0, -1.0),
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.0, 1.01, 1.01, 1.0, 1.0, 1.01, 1.01),
        shadow=(1.0, 1.0, 0.98, 0.98, 1.0, 1.0, 0.98, 0.98),
    ),
    "sleep": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, 1, 1, 2, 2, 1, 1),
        rotation=(0.0,) * 8,
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.0, 0.99, 0.99, 0.98, 0.98, 0.99, 0.99),
        shadow=(1.0,) * 8,
    ),
    "pout": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, 0, -1, -1, 0, 0, -1),
        rotation=(0.0,) * 8,
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.0, 1.0, 1.01, 1.01, 1.0, 1.0, 1.01),
        shadow=(1.0, 1.0, 1.0, 0.98, 0.98, 1.0, 1.0, 0.98),
    ),
    "surprise": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, -2, -4, -2, 0, -2, -4, -2),
        rotation=(0.0,) * 8,
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.01, 1.02, 1.01, 1.0, 1.01, 1.02, 1.01),
        shadow=(1.0, 0.95, 0.9, 0.95, 1.0, 0.95, 0.9, 0.95),
    ),
    "think": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, -1, -1, 0, 0, -1, -1),
        rotation=(0.0, 0.0, -0.5, -0.5, 0.0, 0.0, 0.5, 0.5),
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.0, 1.01, 1.01, 1.0, 1.0, 1.01, 1.01),
        shadow=(1.0, 1.0, 0.98, 0.98, 1.0, 1.0, 0.98, 0.98),
    ),
    "cheer": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, -2, -3, -2, 0, -2, -3, -2),
        rotation=(0.0,) * 8,
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.01, 1.02, 1.01, 1.0, 1.01, 1.02, 1.01),
        shadow=(1.0, 0.95, 0.92, 0.95, 1.0, 0.95, 0.92, 0.95),
    ),
    "sit": PoseMotion(
        x=(0, 0, 0, 0, 0, 0, 0, 0),
        y=(0, 0, 1, 1, 0, 0, 1, 1),
        rotation=(0.0,) * 8,
        scale_x=(1.0,) * 8,
        scale_y=(1.0, 1.0, 0.99, 0.99, 1.0, 1.0, 0.99, 0.99),
        shadow=(1.0,) * 8,
    ),
}


def remove_green(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    out = Image.new("RGBA", rgba.size)
    src = rgba.load()
    dst = out.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, _ = src[x, y]
            green_excess = g - max(r, b)
            if g > 160 and green_excess > 20:
                alpha = int(max(0, min(255, 255 - (green_excess * 1.7))))
                if alpha < 10:
                    dst[x, y] = (0, 0, 0, 0)
                    continue
                # Despill remaining edge pixels so green fringing does not survive scaling.
                safe_green = min(g, max(r, b) + 10)
                dst[x, y] = (r, safe_green, b, alpha)
            else:
                dst[x, y] = (r, g, b, 255)
    return out


def resize_rgba_premultiplied(image: Image.Image, size: tuple[int, int], resample: Image.Resampling) -> Image.Image:
    rgba = image.convert("RGBA")
    src = rgba.load()
    premult = Image.new("RGBA", rgba.size)
    premult_pixels = premult.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = src[x, y]
            premult_pixels[x, y] = (
                (r * a) // 255,
                (g * a) // 255,
                (b * a) // 255,
                a,
            )

    resized = premult.resize(size, resample)
    dst = resized.load()
    for y in range(resized.height):
        for x in range(resized.width):
            r, g, b, a = dst[x, y]
            if a == 0:
                dst[x, y] = (0, 0, 0, 0)
            else:
                dst[x, y] = (
                    min(255, (r * 255) // a),
                    min(255, (g * 255) // a),
                    min(255, (b * 255) // a),
                    a,
                )
    return resized


def alpha_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    alpha = image.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > ALPHA_CUTOFF else 0)
    width, height = mask.size
    pixels = mask.load()
    visited: set[tuple[int, int]] = set()
    best_bbox: tuple[int, int, int, int] | None = None
    best_area = 0

    for y in range(height):
        for x in range(width):
            if pixels[x, y] == 0 or (x, y) in visited:
                continue

            stack = [(x, y)]
            visited.add((x, y))
            min_x = max_x = x
            min_y = max_y = y
            count = 0

            while stack:
                cx, cy = stack.pop()
                count += 1
                min_x = min(min_x, cx)
                max_x = max(max_x, cx)
                min_y = min(min_y, cy)
                max_y = max(max_y, cy)

                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if 0 <= nx < width and 0 <= ny < height and pixels[nx, ny] != 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        stack.append((nx, ny))

            if count > best_area:
                best_area = count
                best_bbox = (min_x, min_y, max_x + 1, max_y + 1)

    if not best_bbox:
        raise ValueError("No visible pixels found in pose.")
    return best_bbox


def fit_pose(image: Image.Image, max_size: int = 136) -> Image.Image:
    bbox = alpha_bbox(image)
    pose = image.crop(bbox)
    scale = min(max_size / pose.width, max_size / pose.height)
    resized = resize_rgba_premultiplied(
        pose,
        (max(1, round(pose.width * scale)), max(1, round(pose.height * scale))),
        Image.Resampling.LANCZOS,
    )
    return resized


def harden_alpha(image: Image.Image, threshold: int = HARD_ALPHA_THRESHOLD) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if a < 20:
                pixels[x, y] = (0, 0, 0, 0)
            elif a < threshold:
                pixels[x, y] = (r, g, b, max(0, min(255, int(a * 0.92))))
            else:
                pixels[x, y] = (r, g, b, 255)
    return rgba


def get_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for font_path in FONT_FILES:
        if not font_path.exists():
            continue
        try:
            return ImageFont.truetype(str(font_path), size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] | None = None,
) -> None:
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font=font, spacing=1, stroke_width=stroke_width)
    width = right - left
    height = bottom - top
    x = box[0] + ((box[2] - box[0]) - width) // 2 - left
    y = box[1] + ((box[3] - box[1]) - height) // 2 - top
    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=fill,
        spacing=1,
        align="center",
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def add_shadow(canvas: Image.Image, scale: float) -> None:
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow)
    width = max(18, int(30 * scale))
    height = max(6, int(9 * scale))
    left = (canvas.width - width) // 2
    top = canvas.height - height - 7
    draw.ellipse((left, top, left + width, top + height), fill=(20, 25, 35, 80))
    shadow = shadow.filter(ImageFilter.GaussianBlur(2))
    canvas.alpha_composite(shadow)


def render_frame(base: Image.Image, motion: PoseMotion, frame_index: int) -> Image.Image:
    scale_x = motion.scale_x[frame_index]
    scale_y = motion.scale_y[frame_index]
    transformed = resize_rgba_premultiplied(
        base,
        (
            max(1, round(base.width * scale_x)),
            max(1, round(base.height * scale_y)),
        ),
        Image.Resampling.LANCZOS,
    ).rotate(
        motion.rotation[frame_index],
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    frame = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    shadow_scale = motion.shadow[frame_index]
    if shadow_scale < 0.995 or frame_index == 0:
        add_shadow(frame, shadow_scale)

    x = (CELL_SIZE - transformed.width) // 2 + motion.x[frame_index]
    y = CELL_SIZE - transformed.height - 6 + motion.y[frame_index]
    frame.alpha_composite(transformed, (x, y))
    return harden_alpha(frame)


def slice_cells(sheet: Image.Image) -> list[Image.Image]:
    cell_w = sheet.width / GRID_COLS
    cell_h = sheet.height / GRID_ROWS
    cells: list[Image.Image] = []
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            left = round(col * cell_w)
            upper = round(row * cell_h)
            right = round((col + 1) * cell_w)
            lower = round((row + 1) * cell_h)
            cells.append(sheet.crop((left, upper, right, lower)))
    return cells


def slice_horizontal_frames(sheet: Image.Image, frame_count: int = 8) -> list[Image.Image]:
    frame_w = sheet.width / frame_count
    frames: list[Image.Image] = []
    for index in range(frame_count):
        left = round(index * frame_w)
        right = round((index + 1) * frame_w)
        frames.append(sheet.crop((left, 0, right, sheet.height)))
    return frames


def build_real_frames(action: str, action_dir: Path) -> list[Path]:
    real_sheet_path = REAL_SHEETS_DIR / REAL_FRAME_ACTIONS[action]
    sheet = remove_green(Image.open(real_sheet_path))
    raw_frames = slice_horizontal_frames(sheet, frame_count=8)
    if action == "walk":
        raw_frames = raw_frames[:-1]
    bbox_areas: list[int] = []
    for raw_frame in raw_frames:
        left, top, right, bottom = alpha_bbox(raw_frame)
        bbox_areas.append((right - left) * (bottom - top))
    median_area = sorted(bbox_areas)[len(bbox_areas) // 2]

    frame_paths: list[Path] = []
    for frame_index, raw_frame in enumerate(raw_frames):
        if bbox_areas[frame_index] < median_area * 0.55:
            replacement_index = (frame_index + 1) % len(raw_frames)
            if bbox_areas[replacement_index] < median_area * 0.55:
                replacement_index = (frame_index - 1) % len(raw_frames)
            raw_frame = raw_frames[replacement_index]
        pose = fit_pose(raw_frame)
        frame = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
        add_shadow(frame, 1.0)
        x = (CELL_SIZE - pose.width) // 2
        y = CELL_SIZE - pose.height - 6
        frame.alpha_composite(pose, (x, y))
        frame = harden_alpha(frame)
        frame_path = action_dir / f"{frame_index:02}.png"
        frame.save(frame_path)
        frame_paths.append(frame_path)
    return frame_paths


def load_generated_frame(action: str, index: int) -> Image.Image:
    frame_path = FRAMES_DIR / action / f"{index:02}.png"
    return Image.open(frame_path).convert("RGBA")


def draw_half_right_frame(frame: Image.Image, frame_index: int) -> Image.Image:
    canvas = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    canvas.alpha_composite(frame)
    draw = ImageDraw.Draw(canvas)
    wobble = -1 if frame_index % 2 else 0
    bubble = (4, 5 + wobble, 118, 48 + wobble)
    draw.rounded_rectangle(bubble, radius=12, fill=(255, 255, 252, 255), outline=(34, 34, 34, 255), width=2)
    draw.polygon([(34, 48 + wobble), (46, 48 + wobble), (39, 59 + wobble)], fill=(255, 255, 252, 255), outline=(34, 34, 34, 255))
    draw_centered_text(
        draw,
        (8, 7 + wobble, 114, 46 + wobble),
        "그건 반만\n맞습니다.",
        get_font(15),
        (26, 26, 30, 255),
    )
    draw.ellipse((104, 35 + wobble, 118, 49 + wobble), fill=(42, 189, 225, 255), outline=(20, 118, 154, 255), width=1)
    draw_centered_text(draw, (104, 34 + wobble, 118, 50 + wobble), "½", get_font(11), (255, 255, 255, 255))
    return canvas


def draw_welcome_agi_frame(frame: Image.Image, frame_index: int) -> Image.Image:
    canvas = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    center = (112, 50)
    for radius, alpha in ((58, 34), (43, 44), (29, 58)):
        draw.ellipse(
            (center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
            outline=(64, 181, 255, alpha),
            width=2,
        )
    for i in range(14):
        angle = (i * 31 + frame_index * 17) * math.pi / 180
        x1 = center[0] + int(math.cos(angle) * 18)
        y1 = center[1] + int(math.sin(angle) * 18)
        x2 = center[0] + int(math.cos(angle) * 61)
        y2 = center[1] + int(math.sin(angle) * 61)
        draw.line((x1, y1, x2, y2), fill=(45, 160, 255, 120), width=2)
    draw_centered_text(draw, (0, 7, 54, 90), "Feel\nthe\nAGI", get_font(23), (15, 15, 18, 255), 1, (255, 255, 255, 255))
    draw_centered_text(draw, (76, 4, 132, 28), "AGI", get_font(17), (52, 149, 255, 255), 1, (255, 255, 255, 255))
    shifted = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    shifted.alpha_composite(frame, (3 if frame_index % 2 else 0, -2 if frame_index % 3 == 0 else 0))
    canvas.alpha_composite(shifted)
    for i in range(4):
        x = 129 + ((frame_index * 5 + i * 11) % 22)
        y = 20 + ((frame_index * 7 + i * 17) % 80)
        draw.line((x - 3, y, x + 3, y), fill=(255, 255, 255, 230), width=1)
        draw.line((x, y - 3, x, y + 3), fill=(255, 255, 255, 230), width=1)
    return canvas


def draw_agi_box_frame(frame: Image.Image, frame_index: int) -> Image.Image:
    canvas = Image.new("RGBA", (CELL_SIZE, CELL_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw_centered_text(draw, (5, 2, 62, 33), "키워", get_font(22), (18, 18, 22, 255), 1, (255, 255, 255, 255))
    bbox = alpha_bbox(frame)
    character = frame.crop(bbox)
    character = resize_rgba_premultiplied(character, (round(character.width * 0.67), round(character.height * 0.67)), Image.Resampling.LANCZOS)
    x = (CELL_SIZE - character.width) // 2
    y = 52 + (frame_index % 2)
    canvas.alpha_composite(character, (x, y))
    box_top = 94
    draw.polygon([(38, box_top), (122, box_top), (111, 149), (49, 149)], fill=(207, 149, 75, 255), outline=(116, 72, 39, 255))
    draw.polygon([(38, box_top), (77, 82), (77, 103), (38, 115)], fill=(232, 181, 101, 255), outline=(116, 72, 39, 255))
    draw.polygon([(122, box_top), (83, 82), (83, 103), (122, 115)], fill=(232, 181, 101, 255), outline=(116, 72, 39, 255))
    draw.line((55, 133, 104, 133), fill=(122, 81, 48, 255), width=1)
    draw_centered_text(draw, (52, 134, 108, 147), "AGI 실패", get_font(9), (107, 71, 42, 255))
    for dx in (-7, 7):
        draw.arc((80 + dx, 45, 91 + dx, 62), 105, 250, fill=(42, 42, 48, 180), width=1)
    return canvas


def build_special_frames(action: str, action_dir: Path) -> list[Path]:
    if action == "half_right":
        source_frames = [load_generated_frame("think", i % 8) for i in range(6)]
        renderer = draw_half_right_frame
    elif action == "welcome_agi":
        source_frames = [load_generated_frame("cheer", i % 8) for i in range(8)]
        renderer = draw_welcome_agi_frame
    elif action == "agi_box":
        source_frames = [load_generated_frame("pout", i % 8) for i in range(6)]
        renderer = draw_agi_box_frame
    else:
        raise ValueError(f"Unknown special action: {action}")

    frame_paths: list[Path] = []
    for frame_index, source_frame in enumerate(source_frames):
        frame = renderer(source_frame, frame_index)
        frame_path = action_dir / f"{frame_index:02}.png"
        frame.save(frame_path)
        frame_paths.append(frame_path)
    return frame_paths


def save_sprite_sheet(action_frames: dict[str, list[Path]]) -> None:
    sheet = Image.new("RGBA", (CELL_SIZE * 8, CELL_SIZE * len(ACTION_NAMES)), (0, 0, 0, 0))
    for row, action in enumerate(ACTION_NAMES):
        for col, frame_path in enumerate(action_frames[action]):
            frame = Image.open(frame_path).convert("RGBA")
            sheet.alpha_composite(frame, (col * CELL_SIZE, row * CELL_SIZE))
    sheet.save(SPRITE_SHEET)


def build_assets() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    REAL_SHEETS_DIR.mkdir(parents=True, exist_ok=True)

    source = Image.open(SOURCE)
    transparent_sheet = remove_green(source)
    cells = slice_cells(transparent_sheet)

    if len(cells) != len(SOURCE_ACTION_NAMES):
        raise ValueError(f"Expected {len(SOURCE_ACTION_NAMES)} cells, got {len(cells)}")

    manifest: dict[str, object] = {
        "cell_size": CELL_SIZE,
        "frame_count": 8,
        "actions": {},
    }
    action_frames: dict[str, list[Path]] = {}

    source_cells = dict(zip(SOURCE_ACTION_NAMES, cells))

    for action in ACTION_NAMES:
        action_dir = FRAMES_DIR / action
        action_dir.mkdir(parents=True, exist_ok=True)
        for stale_file in action_dir.glob("*.png"):
            stale_file.unlink()
        if action in SPECIAL_ACTION_NAMES:
            frame_paths = build_special_frames(action, action_dir)
        elif action in REAL_FRAME_ACTIONS and (REAL_SHEETS_DIR / REAL_FRAME_ACTIONS[action]).exists():
            frame_paths = build_real_frames(action, action_dir)
        else:
            cell = source_cells[action]
            base = fit_pose(cell)
            motion = MOTIONS[action]
            frame_paths = []

            for frame_index in range(8):
                frame = render_frame(base, motion, frame_index)
                frame_path = action_dir / f"{frame_index:02}.png"
                frame.save(frame_path)
                frame_paths.append(frame_path)

        action_frames[action] = frame_paths
        manifest["actions"][action] = {
            "display_name": SPECIAL_DISPLAY_NAMES.get(action, action.title()),
            "frames": [str(path.relative_to(ROOT)).replace("\\", "/") for path in frame_paths],
            "frame_duration_ms": SPECIAL_DURATIONS.get(
                action,
                160 if action == "walk" else 220 if action in {"sleep", "typing", "idle"} else 180,
            ),
        }

    save_sprite_sheet(action_frames)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=True, indent=2), encoding="utf-8")


if __name__ == "__main__":
    build_assets()
    print(f"Built desktop pet assets at {OUTPUT}")
