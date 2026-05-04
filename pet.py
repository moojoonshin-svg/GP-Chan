from __future__ import annotations

import ctypes
import json
import math
import random
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import Menu

from PIL import Image, ImageDraw, ImageFont, ImageTk


ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "assets" / "generated" / "manifest.json"
WINDOW_CHROMA = "#010203"
DEFAULT_ACTIONS = [
    "idle",
    "wave",
    "think",
    "typing",
    "cheer",
    "sit",
    "sleep",
    "pout",
    "surprise",
    "sweep",
    "walk",
    "half_right",
    "welcome_agi",
    "agi_box",
    "drag_dangle",
    "scroll_tickle",
]
ACTION_LABELS = {
    "idle": "멍때리는 중",
    "wave": "하이",
    "think": "생각 중",
    "typing": "타닥타닥",
    "cheer": "힘내 지피짱",
    "sit": "쉬는 중",
    "sleep": "자는 중",
    "pout": "삐진 중",
    "surprise": "꺄악",
    "sweep": "청소 중",
    "walk": "산책 중",
    "half_right": "반만 맞습니다",
    "welcome_agi": "AGI 즈라",
    "agi_box": "박스행",
    "drag_dangle": "대롱대롱",
    "scroll_tickle": "간지러워!",
}
SCALE_CHOICES = [1.0, 1.5, 2.0, 2.5, 3.0]
DEFAULT_SCALE = 1.0
DEFAULT_RESAMPLE = Image.Resampling.NEAREST
TK_ALPHA_THRESHOLD = 96
STATUS_FONT_FILES = [
    Path("C:/Windows/Fonts/H2SA1M.TTF"),
    Path("C:/Windows/Fonts/HMKMAMI.TTF"),
    Path("C:/Windows/Fonts/segoeprb.ttf"),
    Path("C:/Windows/Fonts/comicbd.ttf"),
    Path("C:/Windows/Fonts/malgunbd.ttf"),
]
SMART_UPDATE_MS = 20000
RESOURCE_UPDATE_MS = 10000
BEHAVIOR_TICK_MS = 120
TYPING_GAUGE_PER_KEY = 100
TYPING_GAUGE_DECAY_PER_100MS = 10
TYPING_GAUGE_THRESHOLD = 200
TYPING_GAUGE_MAX = 300
POST_TYPING_IDLE_MS = 2000
CLICK_REACTION_HOLD_MS = 2000
MANUAL_OVERRIDE_MS = 45000
HOVER_OVERRIDE_MS = 9000
MENU_ACTION_LOCK_MS = 3000
PASSIVE_REACTION_MIN_MS = 14000
PASSIVE_REACTION_MAX_MS = 28000
DRAG_HOLD_REFRESH_MS = 1200
TICKLE_STOP_MS = 500
FOLLOW_RADIUS = 286
FOLLOW_STOP_RADIUS = 90
FOLLOW_STEP = 8
WANDER_STEP = 5
STATUS_SHOW_MS = 2600
LETTER_VKS = tuple(range(0x41, 0x5B))
NUMBER_VKS = tuple(range(0x30, 0x3A))
TEXT_TYPING_VKS = (0x0D, 0x20)
KEYBOARD_VIRTUAL_KEYS = LETTER_VKS + NUMBER_VKS + TEXT_TYPING_VKS
SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]


class SYSTEM_POWER_STATUS(ctypes.Structure):
    _fields_ = [
        ("ACLineStatus", ctypes.c_byte),
        ("BatteryFlag", ctypes.c_byte),
        ("BatteryLifePercent", ctypes.c_byte),
        ("SystemStatusFlag", ctypes.c_byte),
        ("BatteryLifeTime", ctypes.c_uint),
        ("BatteryFullLifeTime", ctypes.c_uint),
    ]


class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", ctypes.c_uint32), ("dwHighDateTime", ctypes.c_uint32)]


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_uint32),
        ("dwMemoryLoad", ctypes.c_uint32),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]


@dataclass
class PCState:
    idle_seconds: int
    on_ac_power: bool | None
    battery_percent: int | None
    hour: int


class DesktopPet:
    def __init__(self) -> None:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        self.actions = manifest["actions"]
        self.cell_size = int(manifest.get("cell_size", 80))
        self.frame_sources: dict[str, list[Image.Image]] = {}
        self.frame_cache: dict[tuple[str, float, str], list[ImageTk.PhotoImage]] = {}
        self.status_cache: dict[tuple[str, float], ImageTk.PhotoImage] = {}
        self.scale = DEFAULT_SCALE
        self.mouse_follow_enabled = True
        self.smart_job: str | None = None
        self.behavior_job: str | None = None
        self.resource_job: str | None = None
        self.manual_override_until = 0
        self.action_lock_until = 0
        self.status_until = 0
        self.next_passive_reaction_at = 0
        self.pointer_reaction_pause_until = 0
        self.is_hovering = False
        self.facing = "right"
        self.wander_target_x: int | None = None
        self.last_pointer_mode = False
        self.last_state_label = ""
        self.sparkle_phase = 0
        self.status_text_value = ""
        self.status_photo: ImageTk.PhotoImage | None = None
        self.resource_photo: ImageTk.PhotoImage | None = None
        self.cpu_snapshot: tuple[int, int] | None = None
        self.cpu_percent = 0
        self.ram_percent = 0
        self.drag_moved = False
        self.is_dragging = False
        self.drag_started_at = 0
        self.tickle_until = 0
        self.keyboard_down_vks: set[int] = set()
        self.typing_gauge = 0
        self.last_typing_gauge_update = 0
        self.system_typing_active = False
        self.post_typing_idle_until = 0

        self.root = tk.Tk()
        self.root.title("GPZZ Pet")
        self.root.configure(bg=WINDOW_CHROMA)
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        try:
            self.root.wm_attributes("-transparentcolor", WINDOW_CHROMA)
        except tk.TclError:
            pass

        self.canvas = tk.Canvas(
            self.root,
            width=1,
            height=1,
            bg=WINDOW_CHROMA,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack()
        self.pet_item = self.canvas.create_image(0, 0, anchor="center")
        self.sparkle_items = [
            self.canvas.create_line(0, 0, 0, 0, fill="#9fe8ff", width=2, capstyle=tk.ROUND),
            self.canvas.create_line(0, 0, 0, 0, fill="#9fe8ff", width=2, capstyle=tk.ROUND),
            self.canvas.create_oval(0, 0, 0, 0, fill="#dff8ff", outline="#9fe8ff", width=1),
        ]
        self.status_item = self.canvas.create_image(0, 0, anchor="center")
        self.resource_item = self.canvas.create_image(0, 0, anchor="center")

        self.action = "idle"
        self.frame_index = 0
        self.drag_offset = (0, 0)

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_click_release)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        self.canvas.bind("<Button-3>", self.show_menu)
        self.canvas.bind("<Enter>", self.on_hover_enter)
        self.canvas.bind("<Leave>", self.on_hover_leave)

        self.menu = Menu(self.root, tearoff=0)
        for action_name in DEFAULT_ACTIONS:
            self.menu.add_command(
                label=ACTION_LABELS.get(action_name, action_name),
                command=lambda name=action_name: self.select_action_from_menu(name),
            )
        self.menu.add_separator()
        scale_menu = Menu(self.menu, tearoff=0)
        for scale in SCALE_CHOICES:
            scale_menu.add_command(label=f"{scale:.1f}x", command=lambda value=scale: self.set_scale(value))
        self.menu.add_cascade(label="크기", menu=scale_menu)
        self.menu.add_separator()
        follow_menu = Menu(self.menu, tearoff=0)
        follow_menu.add_command(label="켜기", command=lambda: self.set_mouse_follow_enabled(True))
        follow_menu.add_command(label="끄기", command=lambda: self.set_mouse_follow_enabled(False))
        self.menu.add_cascade(label="마우스 따라가기", menu=follow_menu)
        self.menu.add_command(label="종료", command=self.root.destroy)

        self.apply_layout()
        left, top, _, _ = self.get_screen_bounds()
        self.set_window_position(left + 80, top + 80)
        self.set_action("idle")
        self.show_status("안녕")
        self.schedule_next_passive_reaction()
        self.schedule_smart_update(initial=True)
        self.schedule_behavior_tick(initial=True)
        self.schedule_resource_update(initial=True)

    def now_ms(self) -> int:
        return self.root.tk.getint(self.root.tk.call("clock", "milliseconds"))

    def is_action_locked(self) -> bool:
        return self.now_ms() < self.action_lock_until

    def weighted_action(self, choices: list[tuple[str, int]]) -> str:
        total = sum(weight for _, weight in choices)
        pick = random.randint(1, total)
        running = 0
        for action_name, weight in choices:
            running += weight
            if pick <= running:
                return action_name
        return choices[-1][0]

    def schedule_next_passive_reaction(self) -> None:
        self.next_passive_reaction_at = self.now_ms() + random.randint(PASSIVE_REACTION_MIN_MS, PASSIVE_REACTION_MAX_MS)

    def get_status_font(self, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        for font_path in STATUS_FONT_FILES:
            if not font_path.exists():
                continue
            try:
                return ImageFont.truetype(str(font_path), size=size)
            except OSError:
                continue
        return ImageFont.load_default()

    def filetime_to_int(self, value: FILETIME) -> int:
        return (int(value.dwHighDateTime) << 32) | int(value.dwLowDateTime)

    def read_cpu_snapshot(self) -> tuple[int, int] | None:
        idle = FILETIME()
        kernel = FILETIME()
        user = FILETIME()
        ok = ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle), ctypes.byref(kernel), ctypes.byref(user))
        if not ok:
            return None
        idle_time = self.filetime_to_int(idle)
        total_time = self.filetime_to_int(kernel) + self.filetime_to_int(user)
        return idle_time, total_time

    def read_resource_usage(self) -> tuple[int, int]:
        cpu = self.cpu_percent
        current_snapshot = self.read_cpu_snapshot()
        if current_snapshot and self.cpu_snapshot:
            prev_idle, prev_total = self.cpu_snapshot
            idle, total = current_snapshot
            total_delta = total - prev_total
            idle_delta = idle - prev_idle
            if total_delta > 0:
                cpu = round(max(0, min(100, (1 - idle_delta / total_delta) * 100)))
        if current_snapshot:
            self.cpu_snapshot = current_snapshot

        memory = MEMORYSTATUSEX()
        memory.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ram = self.ram_percent
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
            ram = int(memory.dwMemoryLoad)
        return int(cpu), int(ram)

    def render_resource_panel(self, cpu: int, ram: int) -> Image.Image:
        scale = self.scale
        gauge_width = max(14, round(13 * scale))
        gauge_height = max(78, round(78 * scale))
        gap = max(5, round(5 * scale))
        margin_x = max(2, round(2 * scale))
        margin_y = max(2, round(2 * scale))
        width = gauge_width * 2 + gap + margin_x * 2
        height = gauge_height + margin_y * 2
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        label_font = self.get_status_font(max(8, round(7 * scale)))
        value_font = self.get_status_font(max(17, round(15 * scale)))
        radius = max(6, round(6 * scale))
        outline_width = max(1, round(1.4 * scale))
        inner_pad = max(3, round(3 * scale))
        label_pad = max(8, round(8 * scale))

        gauges = [
            ("CPU", cpu, (13, 178, 230, 255), (227, 249, 255, 250)),
            ("RAM", ram, (0, 188, 105, 255), (229, 255, 241, 250)),
        ]
        for index, (label, percent, color, track_fill) in enumerate(gauges):
            left = margin_x + index * (gauge_width + gap)
            top = margin_y
            right = left + gauge_width
            bottom = top + gauge_height
            track = (left, top, right, bottom)
            draw.rounded_rectangle(track, radius=radius, fill=track_fill, outline=color, width=outline_width)

            inner_left = left + inner_pad
            inner_right = right - inner_pad
            inner_top = top + label_pad
            inner_bottom = bottom - inner_pad
            fill_height = round((inner_bottom - inner_top) * max(0, min(100, percent)) / 100)
            fill_top = inner_bottom - fill_height
            if fill_height > 0:
                draw.rounded_rectangle(
                    (inner_left, fill_top, inner_right, inner_bottom),
                    radius=max(2, round(2 * scale)),
                    fill=color,
                )

            label_box = draw.textbbox((0, 0), label, font=label_font)
            label_x = left + (gauge_width - (label_box[2] - label_box[0])) // 2 - label_box[0]
            label_y = top + max(2, round(2 * scale)) - label_box[1]
            draw.text((label_x, label_y), label, font=label_font, fill=(45, 83, 96, 215))

            value = str(percent)
            value_box = draw.textbbox((0, 0), value, font=value_font, stroke_width=max(1, round(1 * scale)))
            value_x = left + (gauge_width - (value_box[2] - value_box[0])) // 2 - value_box[0]
            value_y = top + (gauge_height - (value_box[3] - value_box[1])) // 2 - value_box[1] + round(4 * scale)
            draw.text(
                (value_x, value_y),
                value,
                font=value_font,
                fill=(26, 38, 46, 255),
                stroke_width=max(1, round(1 * scale)),
                stroke_fill=(255, 255, 255, 210),
            )
        return image

    def render_status_bubble(self, text: str) -> Image.Image:
        font_size = max(12, round(12 * self.scale))
        stroke_width = max(1, round(1.35 * self.scale))
        padding_x = max(12, round(11 * self.scale))
        padding_y = max(8, round(7 * self.scale))
        radius = max(12, round(11 * self.scale))
        tail_width = max(12, round(12 * self.scale))
        tail_height = max(8, round(8 * self.scale))
        outline_width = max(2, round(1.3 * self.scale))

        font = self.get_status_font(font_size)
        probe = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        draw = ImageDraw.Draw(probe)
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
        text_width = right - left
        text_height = bottom - top
        bubble_width = max(round(44 * self.scale), text_width + padding_x * 2)
        body_height = max(round(28 * self.scale), text_height + padding_y * 2)
        image = Image.new("RGBA", (bubble_width, body_height + tail_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        body_rect = (outline_width, outline_width, bubble_width - outline_width - 1, body_height - 1)
        tail_tip = (round(bubble_width * 0.30), body_height + tail_height - outline_width)
        tail_left = (round(bubble_width * 0.40), body_height - outline_width - 1)
        tail_right = (round(bubble_width * 0.40) + tail_width, body_height - outline_width - 1)
        shadow_offset = max(1, round(1.3 * self.scale))

        shadow_fill = (113, 169, 190, 76)
        draw.rounded_rectangle(
            (
                body_rect[0] + shadow_offset,
                body_rect[1] + shadow_offset,
                body_rect[2] + shadow_offset,
                body_rect[3] + shadow_offset,
            ),
            radius=radius,
            fill=shadow_fill,
        )
        draw.polygon(
            [
                (tail_left[0] + shadow_offset, tail_left[1] + shadow_offset),
                (tail_right[0] + shadow_offset, tail_right[1] + shadow_offset),
                (tail_tip[0] + shadow_offset, tail_tip[1] + shadow_offset),
            ],
            fill=shadow_fill,
        )

        outline = (101, 205, 229, 255)
        fill = (255, 255, 252, 255)
        draw.rounded_rectangle(body_rect, radius=radius, fill=fill, outline=outline, width=outline_width)
        draw.polygon([tail_left, tail_right, tail_tip], fill=fill, outline=outline)
        draw.line([tail_left, tail_tip, tail_right], fill=outline, width=outline_width, joint="curve")

        text_x = (bubble_width - text_width) // 2 - left
        text_y = (body_height - text_height) // 2 - top - max(0, round(0.5 * self.scale))
        draw.text(
            (text_x, text_y),
            text,
            font=font,
            fill=(38, 70, 88, 255),
            stroke_width=stroke_width,
            stroke_fill=(255, 255, 255, 255),
        )
        return image

    def load_frame_sources(self, action_name: str) -> list[Image.Image]:
        if action_name not in self.frame_sources:
            self.frame_sources[action_name] = [
                Image.open(ROOT / frame_path).convert("RGBA")
                for frame_path in self.actions[action_name]["frames"]
            ]
        return self.frame_sources[action_name]

    def prepare_tk_sprite(self, image: Image.Image) -> Image.Image:
        sprite = image.convert("RGBA")
        pixels = sprite.load()
        for y in range(sprite.height):
            for x in range(sprite.width):
                r, g, b, a = pixels[x, y]
                if a < TK_ALPHA_THRESHOLD:
                    pixels[x, y] = (0, 0, 0, 0)
                else:
                    pixels[x, y] = (r, g, b, 255)
        return sprite

    def load_frames(self, action_name: str) -> list[ImageTk.PhotoImage]:
        cache_key = (action_name, self.scale, self.facing)
        if cache_key not in self.frame_cache:
            size = max(1, round(self.cell_size * self.scale))
            frames: list[ImageTk.PhotoImage] = []
            for image in self.load_frame_sources(action_name):
                source = image
                if self.facing == "left":
                    source = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
                resized = source.resize((size, size), DEFAULT_RESAMPLE)
                frames.append(ImageTk.PhotoImage(self.prepare_tk_sprite(resized)))
            self.frame_cache[cache_key] = frames
        return self.frame_cache[cache_key]

    def apply_layout(self) -> None:
        pet_size = max(1, round(self.cell_size * self.scale))
        bubble_space_x = max(94, round(94 * self.scale))
        bubble_space_y = max(34, round(38 * self.scale))
        canvas_width = pet_size + bubble_space_x + 24
        canvas_height = pet_size + bubble_space_y + 18
        center_x = 12 + pet_size // 2
        center_y = bubble_space_y + pet_size // 2
        self.canvas.configure(width=canvas_width, height=canvas_height)
        self.canvas.coords(self.pet_item, center_x, center_y)
        self.update_sparkles()
        self.redraw_status()
        self.redraw_resource_panel()

    def animate(self) -> None:
        frames = self.load_frames(self.action)
        self.canvas.itemconfigure(self.pet_item, image=frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(frames)
        delay = int(self.actions[self.action]["frame_duration_ms"])
        self.root.after(delay, self.animate)

    def show_status(self, text: str, duration_ms: int = STATUS_SHOW_MS) -> None:
        self.last_state_label = text
        self.status_text_value = text
        self.status_until = self.now_ms() + duration_ms
        cache_key = (text, self.scale)
        if cache_key not in self.status_cache:
            self.status_cache[cache_key] = ImageTk.PhotoImage(self.render_status_bubble(text))
        self.status_photo = self.status_cache[cache_key]
        self.canvas.itemconfigure(self.status_item, image=self.status_photo)
        self.redraw_status()

    def clear_status_if_needed(self) -> None:
        if self.status_until and self.now_ms() >= self.status_until:
            self.status_until = 0
            self.last_state_label = ""
            self.status_text_value = ""
            self.canvas.itemconfigure(self.status_item, image="")
            self.redraw_status()

    def redraw_status(self) -> None:
        if not self.status_text_value or self.status_photo is None:
            self.canvas.itemconfigure(self.status_item, state="hidden")
            return
        canvas_width = int(self.canvas.cget("width"))
        pet_size = max(1, round(self.cell_size * self.scale))
        center_x = 12 + pet_size // 2
        center_y = max(34, round(38 * self.scale)) + pet_size // 2
        wobble_x = round(math.sin(self.sparkle_phase * 1.2) * max(1, self.scale))
        wobble_y = -round(abs(math.sin(self.sparkle_phase * 0.9)) * max(1, self.scale))
        bubble_x = min(canvas_width - self.status_photo.width() // 2 - 4, center_x + round(pet_size * 0.31))
        bubble_y = max(self.status_photo.height() // 2 + 2, center_y - round(pet_size * 0.34))
        self.canvas.itemconfigure(self.status_item, state="normal")
        self.canvas.coords(self.status_item, bubble_x + wobble_x, bubble_y + wobble_y)
        self.canvas.tag_raise(self.status_item)

    def redraw_resource_panel(self) -> None:
        if self.resource_photo is None:
            self.canvas.itemconfigure(self.resource_item, state="hidden")
            return
        pet_size = max(1, round(self.cell_size * self.scale))
        bubble_space_y = max(34, round(38 * self.scale))
        center_x = 12 + pet_size // 2
        center_y = bubble_space_y + pet_size // 2
        panel_x = center_x + round(pet_size * 0.43)
        panel_y = center_y + round(pet_size * 0.18)
        self.canvas.itemconfigure(self.resource_item, state="normal", image=self.resource_photo)
        self.canvas.coords(self.resource_item, panel_x, panel_y)
        self.canvas.tag_raise(self.resource_item)

    def update_sparkles(self) -> None:
        canvas_width = int(self.canvas.cget("width"))
        pet_size = max(1, round(self.cell_size * self.scale))
        base_x = canvas_width // 2 + int(pet_size * 0.2)
        base_y = 18 + (self.sparkle_phase % 2)
        pulse = (self.sparkle_phase % 6)
        arm = 5 + (1 if pulse in {1, 4} else 0)
        dot = 2 + (1 if pulse in {2, 5} else 0)

        self.canvas.coords(self.sparkle_items[0], base_x - arm, base_y, base_x + arm, base_y)
        self.canvas.coords(self.sparkle_items[1], base_x, base_y - arm, base_x, base_y + arm)
        self.canvas.coords(self.sparkle_items[2], base_x + 10 - dot, base_y - 7 - dot, base_x + 10 + dot, base_y - 7 + dot)
        for item in self.sparkle_items:
            self.canvas.itemconfigure(item, state="normal")
        self.canvas.tag_raise(self.sparkle_items[0])
        self.canvas.tag_raise(self.sparkle_items[1])
        self.canvas.tag_raise(self.sparkle_items[2])

    def set_action(self, action_name: str, label: str | None = None, manual: bool = False, hold_ms: int = MANUAL_OVERRIDE_MS) -> None:
        if self.action != action_name:
            self.action = action_name
            self.frame_index = 0
        if label and (label != self.last_state_label or self.now_ms() >= self.status_until):
            self.show_status(label)
        if manual:
            self.manual_override_until = self.now_ms() + hold_ms

    def select_action_from_menu(self, action_name: str) -> None:
        if self.is_action_locked():
            return
        self.wander_target_x = None
        self.action_lock_until = self.now_ms() + MENU_ACTION_LOCK_MS
        self.set_action(
            action_name,
            label=ACTION_LABELS.get(action_name, action_name),
            manual=True,
            hold_ms=MENU_ACTION_LOCK_MS,
        )

    def set_scale(self, scale: float) -> None:
        self.scale = scale
        if self.status_text_value:
            cache_key = (self.status_text_value, self.scale)
            if cache_key not in self.status_cache:
                self.status_cache[cache_key] = ImageTk.PhotoImage(self.render_status_bubble(self.status_text_value))
            self.status_photo = self.status_cache[cache_key]
            self.canvas.itemconfigure(self.status_item, image=self.status_photo)
        self.resource_photo = ImageTk.PhotoImage(self.render_resource_panel(self.cpu_percent, self.ram_percent))
        self.apply_layout()
        self.frame_index = 0

    def set_mouse_follow_enabled(self, enabled: bool) -> None:
        self.mouse_follow_enabled = enabled
        self.last_pointer_mode = False
        if not enabled and self.action == "walk" and self.wander_target_x is None:
            self.set_action("idle", label="한가한 중", manual=True, hold_ms=MENU_ACTION_LOCK_MS)
        else:
            self.show_status("따라가기 켜짐" if enabled else "따라가기 꺼짐")

    def get_idle_seconds(self) -> int:
        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info))
        elapsed_ms = ctypes.windll.kernel32.GetTickCount() - info.dwTime
        return max(0, elapsed_ms // 1000)

    def get_power_state(self) -> tuple[bool | None, int | None]:
        status = SYSTEM_POWER_STATUS()
        ok = ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status))
        if not ok:
            return None, None
        on_ac = None if status.ACLineStatus == 255 else bool(status.ACLineStatus)
        battery = None if status.BatteryLifePercent == 255 else int(status.BatteryLifePercent)
        return on_ac, battery

    def get_cursor_pos(self) -> tuple[int, int]:
        point = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        return int(point.x), int(point.y)

    def update_keyboard_activity(self) -> None:
        now = self.now_ms()
        if not self.last_typing_gauge_update:
            self.last_typing_gauge_update = now
        elapsed_ms = max(0, now - self.last_typing_gauge_update)
        if elapsed_ms >= 100:
            decay_steps = elapsed_ms // 100
            self.typing_gauge = max(0, self.typing_gauge - decay_steps * TYPING_GAUGE_DECAY_PER_100MS)
            self.last_typing_gauge_update += decay_steps * 100

        down_vks = {
            vk for vk in KEYBOARD_VIRTUAL_KEYS
            if ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000
        }
        new_presses = len(down_vks - self.keyboard_down_vks)
        if new_presses and self.typing_gauge < TYPING_GAUGE_MAX:
            self.typing_gauge = min(
                TYPING_GAUGE_MAX,
                self.typing_gauge + new_presses * TYPING_GAUGE_PER_KEY,
            )
        self.keyboard_down_vks = down_vks

    def get_screen_bounds(self) -> tuple[int, int, int, int]:
        left = int(ctypes.windll.user32.GetSystemMetrics(SM_XVIRTUALSCREEN))
        top = int(ctypes.windll.user32.GetSystemMetrics(SM_YVIRTUALSCREEN))
        width = int(ctypes.windll.user32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
        height = int(ctypes.windll.user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))
        return left, top, left + width, top + height

    def get_pc_state(self) -> PCState:
        on_ac, battery = self.get_power_state()
        return PCState(
            idle_seconds=self.get_idle_seconds(),
            on_ac_power=on_ac,
            battery_percent=battery,
            hour=datetime.now().hour,
        )

    def choose_action_for_state(self, state: PCState) -> tuple[str, str]:
        if state.idle_seconds >= 600:
            return self.weighted_action([("sleep", 5), ("agi_box", 2), ("sit", 1)]), "자리비움"
        if state.battery_percent is not None and state.battery_percent <= 20:
            return self.weighted_action([("pout", 5), ("agi_box", 3), ("sleep", 1)]), f"배터리 {state.battery_percent}%"
        if state.on_ac_power and state.battery_percent is not None and state.battery_percent < 100:
            return self.weighted_action([("cheer", 5), ("welcome_agi", 2), ("think", 1)]), f"충전중 {state.battery_percent}%"
        if 0 <= state.hour < 6:
            return self.weighted_action([("sleep", 5), ("sit", 2), ("agi_box", 1)]), "늦은 밤"
        if state.idle_seconds >= 120:
            return self.weighted_action([("sit", 5), ("think", 3), ("sweep", 2), ("agi_box", 1)]), "멍때리는 중"
        if state.idle_seconds < 15:
            return self.weighted_action(
                [("think", 4), ("half_right", 2), ("surprise", 2), ("wave", 1), ("welcome_agi", 1)]
            ), "활동중"
        if state.idle_seconds < 90:
            return self.weighted_action(
                [("idle", 3), ("think", 3), ("wave", 2), ("sweep", 1), ("half_right", 1)]
            ), "한가한 중"
        return self.weighted_action(
            [("idle", 3), ("think", 3), ("wave", 2), ("sweep", 2), ("sit", 2), ("half_right", 1), ("welcome_agi", 1), ("agi_box", 1)]
        ), "한가한 중"

    def choose_passive_action(self) -> tuple[str, str]:
        action = self.weighted_action(
            [
                ("idle", 4),
                ("wave", 3),
                ("think", 3),
                ("sit", 2),
                ("sweep", 2),
                ("half_right", 2),
                ("welcome_agi", 1),
                ("agi_box", 1),
            ]
        )
        return action, ACTION_LABELS.get(action, "한가한 중")

    def schedule_smart_update(self, initial: bool = False) -> None:
        if self.smart_job:
            self.root.after_cancel(self.smart_job)
        self.smart_job = self.root.after(1200 if initial else SMART_UPDATE_MS, self.apply_smart_state)

    def schedule_resource_update(self, initial: bool = False) -> None:
        if self.resource_job:
            self.root.after_cancel(self.resource_job)
        delay = 1200 if initial else RESOURCE_UPDATE_MS
        self.resource_job = self.root.after(delay, self.update_resource_panel)

    def update_resource_panel(self) -> None:
        self.cpu_percent, self.ram_percent = self.read_resource_usage()
        self.resource_photo = ImageTk.PhotoImage(self.render_resource_panel(self.cpu_percent, self.ram_percent))
        self.canvas.itemconfigure(self.resource_item, image=self.resource_photo)
        self.redraw_resource_panel()
        self.schedule_resource_update()

    def apply_smart_state(self) -> None:
        if self.is_action_locked():
            self.schedule_smart_update()
            return
        if not self.is_hovering and self.now_ms() >= self.manual_override_until and self.wander_target_x is None:
            action, label = self.choose_action_for_state(self.get_pc_state())
            if self.action != "walk":
                self.set_action(action, label=label)
        self.schedule_smart_update()

    def distance_to_cursor(self) -> tuple[float, int, int]:
        cursor_x, cursor_y = self.get_cursor_pos()
        pet_x = self.root.winfo_x() + int(self.canvas.cget("width")) // 2
        pet_y = self.root.winfo_y() + int(self.canvas.cget("height")) // 2
        dx = cursor_x - pet_x
        dy = cursor_y - pet_y
        return math.hypot(dx, dy), dx, dy

    def move_by(self, dx: int, dy: int) -> None:
        self.set_window_position(self.root.winfo_x() + dx, self.root.winfo_y() + dy)

    def clamp_window_position(self, x: int, y: int) -> tuple[int, int]:
        left, top, right, bottom = self.get_screen_bounds()
        width = int(self.canvas.cget("width"))
        height = int(self.canvas.cget("height"))
        return max(left, min(right - width, x)), max(top, min(bottom - height, y))

    def set_window_position(self, x: int, y: int) -> None:
        x, y = self.clamp_window_position(x, y)
        hwnd = self.root.winfo_id()
        moved = ctypes.windll.user32.SetWindowPos(
            hwnd,
            HWND_TOPMOST,
            int(x),
            int(y),
            0,
            0,
            SWP_NOSIZE | SWP_NOACTIVATE,
        )
        if not moved:
            self.root.geometry(f"{x:+d}{y:+d}")

    def maybe_start_wander(self) -> None:
        if self.wander_target_x is not None or self.is_hovering or self.now_ms() < self.manual_override_until:
            return
        if random.random() > 0.01:
            return
        left, _, right, _ = self.get_screen_bounds()
        width = int(self.canvas.cget("width"))
        current_x = self.root.winfo_x()
        shift = random.randint(90, 240) * random.choice([-1, 1])
        self.wander_target_x = max(left, min(right - width, current_x + shift))

    def apply_mouse_follow(self) -> bool:
        if self.is_dragging or self.now_ms() < self.tickle_until or self.now_ms() < self.pointer_reaction_pause_until:
            return True
        if not self.mouse_follow_enabled:
            self.last_pointer_mode = False
            return False
        distance, dx, dy = self.distance_to_cursor()
        if distance > FOLLOW_RADIUS:
            if self.last_pointer_mode and self.wander_target_x is None and self.action == "walk":
                self.set_action(random.choice(["idle", "think", "sit", "agi_box"]), label="놓쳤다")
            self.last_pointer_mode = False
            return False

        self.facing = "right" if dx >= 0 else "left"
        self.last_pointer_mode = True
        if distance <= FOLLOW_STOP_RADIUS:
            if self.action != "wave":
                self.set_action(random.choice(["wave", "surprise", "cheer", "half_right"]), label="반가워")
            return True

        step_x = int(max(-FOLLOW_STEP, min(FOLLOW_STEP, dx * 0.14)))
        step_y = int(max(-3, min(3, dy * 0.05)))
        if step_x == 0 and dx != 0:
            step_x = 1 if dx > 0 else -1
        self.move_by(step_x, step_y)
        self.set_action("walk", label="따라가는중")
        return True

    def apply_wander(self) -> None:
        if self.wander_target_x is None:
            return
        current_x = self.root.winfo_x()
        delta = self.wander_target_x - current_x
        if abs(delta) <= WANDER_STEP:
            self.wander_target_x = None
            self.set_action(random.choice(["idle", "sit", "think"]), label="산책 끝")
            return
        self.facing = "right" if delta > 0 else "left"
        self.move_by(WANDER_STEP if delta > 0 else -WANDER_STEP, 0)
        self.set_action("walk", label="산책중")

    def apply_passive_reaction(self) -> None:
        if self.is_hovering or self.wander_target_x is not None or self.is_dragging or self.now_ms() < self.tickle_until:
            return
        if self.now_ms() < self.manual_override_until or self.now_ms() < self.next_passive_reaction_at:
            return
        action, label = self.choose_passive_action()
        self.set_action(action, label=label, manual=True, hold_ms=random.randint(5000, 9000))
        self.schedule_next_passive_reaction()

    def apply_system_typing(self) -> bool:
        if self.is_hovering or self.typing_gauge < TYPING_GAUGE_THRESHOLD:
            if self.system_typing_active:
                self.system_typing_active = False
                if self.action == "typing":
                    self.set_action("idle", label="한가한 중")
                self.post_typing_idle_until = self.now_ms() + POST_TYPING_IDLE_MS
            return False
        self.wander_target_x = None
        self.system_typing_active = True
        self.post_typing_idle_until = 0
        self.set_action("typing", label=ACTION_LABELS["typing"])
        return True

    def apply_post_typing_idle(self) -> bool:
        if not self.post_typing_idle_until:
            return False
        now = self.now_ms()
        if now < self.post_typing_idle_until:
            return True

        self.post_typing_idle_until = 0
        action, label = self.choose_action_for_state(self.get_pc_state())
        if action == "typing":
            action, label = "think", ACTION_LABELS["think"]
        self.set_action(action, label=label)
        return True

    def schedule_behavior_tick(self, initial: bool = False) -> None:
        if self.behavior_job:
            self.root.after_cancel(self.behavior_job)
        self.behavior_job = self.root.after(300 if initial else BEHAVIOR_TICK_MS, self.behavior_tick)

    def behavior_tick(self) -> None:
        self.sparkle_phase = (self.sparkle_phase + 1) % 6
        self.update_sparkles()
        self.redraw_status()
        self.clear_status_if_needed()
        self.update_keyboard_activity()
        if self.is_dragging:
            self.set_action("drag_dangle", label=ACTION_LABELS["drag_dangle"], manual=True, hold_ms=DRAG_HOLD_REFRESH_MS)
        elif self.now_ms() < self.tickle_until:
            self.set_action("scroll_tickle", label=ACTION_LABELS["scroll_tickle"], manual=True, hold_ms=TICKLE_STOP_MS + 300)
        if self.is_action_locked():
            self.schedule_behavior_tick()
            return
        handled = self.apply_mouse_follow()
        if not handled:
            if self.apply_system_typing():
                pass
            elif self.apply_post_typing_idle():
                pass
            else:
                self.maybe_start_wander()
                self.apply_wander()
                self.apply_passive_reaction()
        self.schedule_behavior_tick()

    def start_drag(self, event: tk.Event[tk.Misc]) -> None:
        if self.is_action_locked():
            return
        self.drag_offset = (event.x_root - self.root.winfo_x(), event.y_root - self.root.winfo_y())
        self.wander_target_x = None
        self.drag_moved = False
        self.is_dragging = True
        self.drag_started_at = self.now_ms()
        self.set_action("drag_dangle", label=ACTION_LABELS["drag_dangle"], manual=True, hold_ms=HOVER_OVERRIDE_MS)

    def on_drag(self, event: tk.Event[tk.Misc]) -> None:
        if self.is_action_locked():
            return
        self.is_dragging = True
        x = event.x_root - self.drag_offset[0]
        y = event.y_root - self.drag_offset[1]
        if abs(x - self.root.winfo_x()) > 2 or abs(y - self.root.winfo_y()) > 2:
            self.drag_moved = True
        self.set_action("drag_dangle", label=ACTION_LABELS["drag_dangle"], manual=True, hold_ms=HOVER_OVERRIDE_MS)
        self.set_window_position(x, y)

    def on_click_release(self, event: tk.Event[tk.Misc]) -> None:
        if self.is_action_locked():
            return
        held_ms = self.now_ms() - self.drag_started_at if self.drag_started_at else 0
        was_dragging = self.is_dragging
        self.is_dragging = False
        self.drag_started_at = 0
        if self.drag_moved or (was_dragging and held_ms > 250):
            self.drag_moved = False
            self.set_action(random.choice(["surprise", "wave", "idle"]), label="내려놨어", manual=True, hold_ms=3000)
            return
        if 0 <= event.x <= self.canvas.winfo_width() and 0 <= event.y <= self.canvas.winfo_height():
            self.wander_target_x = None
            self.pointer_reaction_pause_until = self.now_ms() + CLICK_REACTION_HOLD_MS
            action_name = random.choice(["wave", "cheer", "surprise", "half_right", "welcome_agi"])
            self.set_action(
                action_name,
                label=ACTION_LABELS[action_name],
                manual=True,
                hold_ms=CLICK_REACTION_HOLD_MS,
            )

    def on_mouse_wheel(self, _event: tk.Event[tk.Misc]) -> None:
        if self.is_action_locked():
            return
        self.wander_target_x = None
        self.tickle_until = self.now_ms() + TICKLE_STOP_MS
        self.set_action("scroll_tickle", label=ACTION_LABELS["scroll_tickle"], manual=True, hold_ms=TICKLE_STOP_MS + 300)

    def on_hover_enter(self, _event: tk.Event[tk.Misc]) -> None:
        if self.is_action_locked():
            return
        self.is_hovering = True
        if self.now_ms() < self.pointer_reaction_pause_until:
            return
        self.wander_target_x = None
        self.set_action(
            random.choice(["wave", "cheer", "surprise", "half_right"]),
            label="어서와",
            manual=True,
            hold_ms=HOVER_OVERRIDE_MS,
        )

    def on_hover_leave(self, _event: tk.Event[tk.Misc]) -> None:
        if self.is_action_locked():
            return
        self.is_hovering = False

    def show_menu(self, event: tk.Event[tk.Misc]) -> None:
        if self.is_action_locked():
            return
        self.menu.tk_popup(event.x_root, event.y_root)

    def run(self) -> None:
        self.animate()
        self.root.mainloop()


if __name__ == "__main__":
    DesktopPet().run()
