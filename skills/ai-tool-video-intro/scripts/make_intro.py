from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/simsun.ttc"),
    Path("C:/Windows/Fonts/Deng.ttf"),
)

PALETTE = {
    "bg": (5, 12, 18),
    "cyan": (51, 224, 255),
    "cyan_soft": (55, 160, 190),
    "amber": (245, 177, 67),
    "white": (238, 246, 246),
    "muted": (132, 154, 160),
}


def ease_out_cubic(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def ease_in_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3.0 - 2.0 * x)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def fitted_font(text: str, target_width: int, start_size: int) -> ImageFont.ImageFont:
    size = start_size
    while size > 18:
        font = load_font(size)
        box = ImageDraw.Draw(Image.new("RGB", (1, 1))).textbbox((0, 0), text, font=font)
        if box[2] - box[0] <= target_width:
            return font
        size -= 2
    return load_font(size)


def cover_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    new_size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resized = image.resize(new_size, Image.Resampling.LANCZOS)
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def read_source_frame(path: Path | None, size: tuple[int, int]) -> Image.Image:
    if not path or not path.exists():
        return Image.new("RGB", size, PALETTE["bg"])

    try:
        reader = imageio.get_reader(path)
        frame = reader.get_data(0)
        reader.close()
        image = Image.fromarray(frame[:, :, :3]).convert("RGB")
        return cover_resize(image, size)
    except Exception:
        return Image.new("RGB", size, PALETTE["bg"])


def read_video_size(path: Path | None) -> tuple[int, int]:
    if not path or not path.exists():
        return 1920, 1080
    try:
        reader = imageio.get_reader(path)
        meta = reader.get_meta_data()
        reader.close()
        width, height = meta.get("source_size") or meta.get("size") or (1920, 1080)
        return int(width), int(height)
    except Exception:
        return 1920, 1080


def draw_glow_line(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    color: tuple[int, int, int],
    alpha: int,
    width: int,
) -> None:
    for glow_width, glow_alpha in ((width + 8, alpha // 7), (width + 4, alpha // 4)):
        draw.line((start, end), fill=(*color, glow_alpha), width=glow_width)
    draw.line((start, end), fill=(*color, alpha), width=width)


def draw_partial_polyline(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    progress: float,
    color: tuple[int, int, int],
    alpha: int,
    width: int,
) -> None:
    if len(points) < 2 or progress <= 0:
        return

    lengths: list[float] = []
    total = 0.0
    for a, b in zip(points, points[1:]):
        length = math.dist(a, b)
        lengths.append(length)
        total += length

    remaining = total * max(0.0, min(1.0, progress))
    for (a, b), length in zip(zip(points, points[1:]), lengths):
        if remaining <= 0:
            break
        if remaining >= length:
            draw_glow_line(draw, a, b, color, alpha, width)
            remaining -= length
        else:
            ratio = remaining / max(length, 1e-6)
            partial = (a[0] + (b[0] - a[0]) * ratio, a[1] + (b[1] - a[1]) * ratio)
            draw_glow_line(draw, a, partial, color, alpha, width)
            break


def draw_grid(draw: ImageDraw.ImageDraw, w: int, h: int, t: float, progress: float) -> None:
    spacing = max(28, int(min(w, h) * 0.055))
    offset_x = int((t * 42) % spacing)
    offset_y = int((t * 18) % spacing)
    alpha_base = int(24 + 26 * progress)

    for x in range(-spacing, w + spacing, spacing):
        alpha = alpha_base if (x // spacing) % 4 else alpha_base + 18
        draw.line(((x + offset_x, 0), (x + offset_x - int(w * 0.08), h)), fill=(*PALETTE["cyan_soft"], alpha), width=1)

    for y in range(-spacing, h + spacing, spacing):
        alpha = alpha_base if (y // spacing) % 4 else alpha_base + 18
        draw.line(((0, y + offset_y), (w, y + offset_y + int(h * 0.04))), fill=(*PALETTE["cyan_soft"], alpha), width=1)


def draw_cad_geometry(draw: ImageDraw.ImageDraw, w: int, h: int, t: float) -> None:
    p = ease_out_cubic((t - 0.35) / 0.9)
    base_x = w * 0.58
    base_y = h * 0.48
    scale = min(w, h) / 860

    outline = [
        (base_x - 320 * scale, base_y - 105 * scale),
        (base_x - 95 * scale, base_y - 185 * scale),
        (base_x + 120 * scale, base_y - 150 * scale),
        (base_x + 260 * scale, base_y - 20 * scale),
        (base_x + 205 * scale, base_y + 150 * scale),
        (base_x - 70 * scale, base_y + 200 * scale),
        (base_x - 300 * scale, base_y + 110 * scale),
        (base_x - 320 * scale, base_y - 105 * scale),
    ]
    draw_partial_polyline(draw, outline, p, PALETTE["cyan"], 185, max(2, int(3 * scale)))

    circles = [
        (base_x - 120 * scale, base_y + 8 * scale, 92 * scale),
        (base_x + 80 * scale, base_y + 18 * scale, 72 * scale),
        (base_x - 245 * scale, base_y - 80 * scale, 42 * scale),
        (base_x + 205 * scale, base_y + 95 * scale, 45 * scale),
    ]
    circle_progress = ease_out_cubic((t - 0.68) / 0.75)
    for i, (cx, cy, r) in enumerate(circles):
        if circle_progress <= i * 0.12:
            continue
        local = max(0.0, min(1.0, (circle_progress - i * 0.12) / 0.7))
        bbox = (cx - r, cy - r, cx + r, cy + r)
        draw.arc(bbox, start=0, end=int(360 * local), fill=(*PALETTE["white"], 160), width=max(2, int(2.2 * scale)))
        if local > 0.45:
            draw.arc((cx - r * 0.42, cy - r * 0.42, cx + r * 0.42, cy + r * 0.42), 0, int(360 * local), fill=(*PALETTE["cyan"], 150), width=max(1, int(1.5 * scale)))

    detail_p = ease_out_cubic((t - 1.0) / 0.85)
    for i, y_off in enumerate((-155, -45, 64, 154)):
        start = (base_x - 385 * scale, base_y + y_off * scale)
        end = (base_x + (-250 + i * 115) * scale, base_y + (y_off + 8) * scale)
        draw_partial_polyline(draw, [start, end], detail_p, PALETTE["muted"], 125, 1)

    scan_x = int((t / 3.2) * (w + w * 0.2) - w * 0.1)
    draw.rectangle((scan_x - 2, 0, scan_x + 2, h), fill=(*PALETTE["cyan"], 55))


def draw_text_with_shadow(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
) -> None:
    x, y = xy
    draw.text((x + 4, y + 5), text, font=font, fill=(0, 0, 0, min(180, fill[3])))
    draw.text((x, y), text, font=font, fill=fill)


def draw_lockup(
    draw: ImageDraw.ImageDraw,
    w: int,
    h: int,
    t: float,
    title: str,
    subtitle: str,
    caption: str,
    highlights: list[str],
) -> None:
    title_progress = ease_out_cubic((t - 0.78) / 0.75)
    sub_progress = ease_out_cubic((t - 1.25) / 0.75)
    highlight_progress = ease_out_cubic((t - 1.45) / 0.7)

    left = int(w * 0.075)
    center_y = int(h * 0.47)
    title_font = fitted_font(title, int(w * 0.48), max(48, int(h * 0.088)))
    subtitle_font = fitted_font(subtitle, int(w * 0.45), max(24, int(h * 0.038)))
    caption_font = load_font(max(16, int(h * 0.022)))
    highlight_font = load_font(max(18, int(h * 0.026)))

    title_shift = int((1.0 - title_progress) * -42)
    title_alpha = int(245 * title_progress)
    accent_w = int((w * 0.28) * ease_out_cubic((t - 0.55) / 0.8))

    draw.rectangle((left, center_y - int(h * 0.105), left + accent_w, center_y - int(h * 0.1) + 4), fill=(*PALETTE["amber"], 210))
    draw_text_with_shadow(
        draw,
        (left + title_shift, center_y - int(h * 0.085)),
        title,
        title_font,
        (*PALETTE["white"], title_alpha),
    )

    sub_alpha = int(210 * sub_progress)
    draw_text_with_shadow(
        draw,
        (left, center_y + int(h * 0.025)),
        subtitle,
        subtitle_font,
        (*PALETTE["cyan"], sub_alpha),
    )

    tag_alpha = int(160 * sub_progress)
    draw.text((left, center_y + int(h * 0.098)), caption, font=caption_font, fill=(*PALETTE["muted"], tag_alpha))

    tag_y = center_y + int(h * 0.145)
    tags = ("AUTO CAD", "AI WORKFLOW", "PRACTICAL GUIDE")
    x = left
    for tag in tags:
        box = draw.textbbox((0, 0), tag, font=caption_font)
        tw = box[2] - box[0]
        pad = int(h * 0.012)
        alpha = int(90 * sub_progress)
        draw.rounded_rectangle((x, tag_y, x + tw + pad * 2, tag_y + int(h * 0.04)), radius=6, outline=(*PALETTE["cyan"], alpha), fill=(6, 22, 28, int(80 * sub_progress)), width=1)
        draw.text((x + pad, tag_y + int(h * 0.008)), tag, font=caption_font, fill=(*PALETTE["white"], int(155 * sub_progress)))
        x += tw + pad * 3

    if highlights:
        panel_x = int(w * 0.075)
        panel_y = center_y + int(h * 0.205)
        panel_w = int(w * 0.42)
        row_h = int(h * 0.048)
        panel_alpha = int(125 * highlight_progress)
        draw.rounded_rectangle(
            (panel_x, panel_y, panel_x + panel_w, panel_y + row_h * min(3, len(highlights)) + int(h * 0.026)),
            radius=8,
            fill=(4, 18, 23, panel_alpha),
            outline=(*PALETTE["cyan"], int(75 * highlight_progress)),
            width=1,
        )
        draw.text(
            (panel_x + int(h * 0.018), panel_y + int(h * 0.01)),
            "本期亮点",
            font=caption_font,
            fill=(*PALETTE["amber"], int(205 * highlight_progress)),
        )
        for index, item in enumerate(highlights[:3], start=1):
            y = panel_y + int(h * 0.012) + row_h * index
            local = ease_out_cubic((highlight_progress - (index - 1) * 0.16) / 0.65)
            if local <= 0:
                continue
            marker_x = panel_x + int(h * 0.02)
            marker_y = y + int(row_h * 0.18)
            draw.rounded_rectangle(
                (marker_x, marker_y, marker_x + int(h * 0.036), marker_y + int(h * 0.028)),
                radius=5,
                fill=(*PALETTE["amber"], int(185 * local)),
            )
            draw.text(
                (marker_x + int(h * 0.01), marker_y + 1),
                f"{index}",
                font=caption_font,
                fill=(5, 12, 18, int(230 * local)),
            )
            draw.text(
                (marker_x + int(h * 0.05), y),
                item,
                font=highlight_font,
                fill=(*PALETTE["white"], int(220 * local)),
            )


def make_frame(
    source: Image.Image,
    size: tuple[int, int],
    t: float,
    duration: float,
    title: str,
    subtitle: str,
    caption: str,
    highlights: list[str],
) -> Image.Image:
    w, h = size
    progress = ease_in_out(t / duration)
    zoom = 1.02 + 0.065 * progress
    pan_x = int(22 * progress)
    pan_y = int(-10 * progress)

    bg = source.resize((int(w * zoom), int(h * zoom)), Image.Resampling.LANCZOS)
    left = (bg.width - w) // 2 + pan_x
    top = (bg.height - h) // 2 + pan_y
    bg = bg.crop((left, top, left + w, top + h))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=4.5))

    dark = Image.new("RGB", (w, h), PALETTE["bg"])
    frame = Image.blend(bg, dark, 0.68).convert("RGBA")
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    vignette = Image.new("L", (w, h), 0)
    vg = ImageDraw.Draw(vignette)
    max_r = int(math.hypot(w, h) * 0.62)
    for i in range(max_r, 0, -18):
        alpha = int(175 * (1 - i / max_r) ** 1.8)
        vg.ellipse((w // 2 - i, h // 2 - i, w // 2 + i, h // 2 + i), fill=alpha)
    overlay.alpha_composite(Image.new("RGBA", (w, h), (0, 0, 0, 0)))

    draw_grid(draw, w, h, t, progress)
    draw_cad_geometry(draw, w, h, t)
    draw_lockup(draw, w, h, t, title, subtitle, caption, highlights)

    sweep = ease_out_cubic((t - (duration - 0.45)) / 0.38)
    if sweep > 0:
        bar_w = int(w * 0.22)
        x = int(-bar_w + sweep * (w + bar_w))
        draw.polygon(
            [(x, 0), (x + bar_w, 0), (x + bar_w - int(w * 0.04), h), (x - int(w * 0.04), h)],
            fill=(*PALETTE["amber"], 95),
        )

    frame = Image.alpha_composite(frame, overlay)

    fade = 1.0
    if t < 0.25:
        fade = t / 0.25
    alpha = int(255 * fade)
    if alpha < 255:
        black = Image.new("RGBA", (w, h), (0, 0, 0, 255 - alpha))
        frame = Image.alpha_composite(frame, black)

    return frame.convert("RGB")


def write_intro(
    input_video: Path | None,
    output_intro: Path,
    duration: float,
    fps: int,
    title: str,
    subtitle: str,
    caption: str,
    highlights: list[str],
) -> tuple[int, int]:
    size = read_video_size(input_video)
    source = read_source_frame(input_video, size)
    output_intro.parent.mkdir(parents=True, exist_ok=True)

    frame_count = max(1, int(round(duration * fps)))
    writer = imageio.get_writer(output_intro, fps=fps, codec="libx264", quality=8, macro_block_size=1)
    try:
        for index in range(frame_count):
            t = index / fps
            frame = make_frame(source, size, t, duration, title, subtitle, caption, highlights)
            writer.append_data(np.asarray(frame))
    finally:
        writer.close()

    return size


def prepend_intro(intro: Path, source: Path, output: Path, size: tuple[int, int], fps: int) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    width, height = size

    command = [
        ffmpeg,
        "-y",
        "-i",
        str(intro),
        "-i",
        str(source),
        "-filter_complex",
        (
            f"[0:v]fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];"
            f"[1:v]fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1[v1];"
            "[v0][v1]concat=n=2:v=1:a=0[v]"
        ),
        "-map",
        "[v]",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-crf",
        "20",
        "-preset",
        "veryfast",
        str(output),
    ]
    subprocess.run(command, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a fixed-style 3-second AI + traditional tools video intro.")
    parser.add_argument("--input", default=None, help="Source recording used for size/background and optional prepending.")
    parser.add_argument("--output-intro", required=True, help="Output intro MP4 path.")
    parser.add_argument("--output-combined", default=None, help="Optional combined video path with intro prepended.")
    parser.add_argument("--title", default="AI + 传统工具", help="Main title text.")
    parser.add_argument("--subtitle", default="自动绘图 / 攻略 / 实战分享", help="Subtitle text.")
    parser.add_argument("--caption", default="WORKFLOW NOTES", help="Small caption text.")
    parser.add_argument(
        "--highlight",
        action="append",
        default=None,
        help="Highlight line to show in the opener. Pass up to three times.",
    )
    parser.add_argument("--duration", type=float, default=3.2, help="Intro duration in seconds.")
    parser.add_argument("--fps", type=int, default=30, help="Intro and combined output FPS.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = Path(args.input).resolve() if args.input else None
    intro = Path(args.output_intro).resolve()
    highlights = args.highlight or [
        "全自动调用 AutoCAD 绘制",
        "复杂机械图纸从零生成",
        "录屏 / 字幕 / 配音一体化",
    ]

    size = write_intro(
        input_video=source,
        output_intro=intro,
        duration=args.duration,
        fps=args.fps,
        title=args.title,
        subtitle=args.subtitle,
        caption=args.caption,
        highlights=highlights,
    )
    print(f"Saved intro: {intro}")
    print(f"Intro size: {size[0]}x{size[1]}, duration={args.duration:.2f}s, fps={args.fps}")

    if args.output_combined:
        if source is None or not source.exists():
            raise ValueError("--output-combined requires an existing --input video")
        combined = Path(args.output_combined).resolve()
        prepend_intro(intro, source, combined, size=size, fps=args.fps)
        print(f"Saved combined video: {combined}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
