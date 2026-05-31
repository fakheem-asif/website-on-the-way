"""Compose documentary frames with Pillow, in two layers.

A scene's frame is split into:
  * a BASE image  — the underlying visual (styled background offline, or B-roll),
  * an OVERLAY     — a transparent layer holding the scrim, text, source citation,
                     and the always-on "AI-ASSISTED" bug.

Keeping them separate lets the assemble stage apply Ken Burns motion to the base
*underneath* a pixel-fixed overlay, so the disclosure bug and citations never
drift out of frame. Routing every scene through one overlay builder is what
makes the disclosure markings uniform and non-optional.
"""
from __future__ import annotations

import functools

from PIL import Image, ImageDraw, ImageFont

from .text import wrap_to_width

_DARK = (8, 10, 14)


@functools.lru_cache(maxsize=64)
def _font(path: str, size: int):
    for candidate in (path, path.replace("-Bold", ""), "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _block(draw, text, font, box, fill, leading=1.25, align="left"):
    """Word-wrap text inside box=(x, y, w); return the y below the block."""
    x, y, w = box
    lines: list[str] = []
    for para in text.split("\n"):
        lines.extend(wrap_to_width(draw, para, font, w) if para else [""])
    asc, desc = font.getmetrics()
    line_h = int((asc + desc) * leading)
    for line in lines:
        lx = x
        if align in ("center", "right"):
            bb = draw.textbbox((0, 0), line, font=font)
            tw = bb[2] - bb[0]
            lx = x + (w - tw) // 2 if align == "center" else x + (w - tw)
        draw.text((lx, y), line, font=font, fill=fill)
        y += line_h
    return y


def background(style) -> Image.Image:
    """A plain, on-brand background — the offline base image."""
    return Image.new("RGB", (style.width, style.height), style.bg)


def fit(img: Image.Image, style) -> Image.Image:
    """Scale/crop an arbitrary image to fill the frame."""
    img = img.convert("RGB")
    tw, th = style.width, style.height
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    img = img.resize((max(1, int(sw * scale)), max(1, int(sh * scale))), Image.LANCZOS)
    sw, sh = img.size
    left, top = (sw - tw) // 2, (sh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def base_frame(style, base_img: Image.Image) -> Image.Image:
    return fit(base_img, style)


def _scrim(draw, w, h, top=0.0, bottom=0.0):
    """Translucent black gradients top/bottom for text legibility over B-roll."""
    if bottom:
        n = int(h * bottom)
        for i in range(n):
            draw.line([(0, h - i), (w, h - i)], fill=(*_DARK, int(205 * (i / n))))
    if top:
        n = int(h * top)
        for i in range(n):
            draw.line([(0, i), (w, i)], fill=(*_DARK, int(185 * (i / n))))


def _bug(draw, style):
    """Persistent 'AI-ASSISTED' pill, top-right — present on every frame."""
    label = style.bug_label
    if not label:
        return
    font = _font(style.font_bold, 26)
    bb = draw.textbbox((0, 0), label, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad_x, pad_y = 18, 10
    w, h = tw + pad_x * 2, th + pad_y * 2
    x, y = style.width - w - 48, 40
    draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=style.accent)
    draw.text((x + pad_x, y + pad_y - bb[1]), label, font=font, fill=style.bg)


def _ribbon(draw, style, text):
    font = _font(style.font_bold, 24)
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    pad = 16
    x, y = 48, style.height - 64
    draw.rectangle([x - pad, y - pad, x + tw + pad, y + (bb[3] - bb[1]) + pad], fill="#7a1f1f")
    draw.text((x, y - bb[1]), text, font=font, fill="#ffffff")


def overlay_layer(style, scene, fictional=False) -> Image.Image:
    """Transparent RGBA layer with scrim + text + citation + bug for one scene."""
    img = Image.new("RGBA", (style.width, style.height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = int(style.width * 0.08)
    inner = style.width - margin * 2

    if scene.kind == "title":
        _scrim(draw, style.width, style.height, top=0.25, bottom=0.45)
        y = int(style.height * 0.40)
        if scene.chapter:
            y = _block(draw, scene.chapter.upper(), _font(style.font_bold, 30), (margin, y, inner), style.accent)
            y += 12
        y = _block(draw, scene.heading, _font(style.font_serif, 92), (margin, y, inner), style.fg, leading=1.1)
        y += 18
        if scene.on_screen_text:
            _block(draw, scene.on_screen_text, _font(style.font_regular, 40), (margin, y, inner), style.muted)

    elif scene.kind == "disclosure":
        _scrim(draw, style.width, style.height, top=0.2, bottom=0.2)
        draw.rounded_rectangle([margin - 30, int(style.height * 0.2),
                                style.width - margin + 30, int(style.height * 0.8)],
                               radius=22, outline=style.accent, width=4)
        y = int(style.height * 0.28)
        y = _block(draw, "AI-ASSISTED PRODUCTION", _font(style.font_bold, 44),
                   (margin, y, inner), style.accent, align="center")
        y += 26
        _block(draw, scene.narration, _font(style.font_regular, 38),
               (margin, y, inner), style.fg, leading=1.4, align="center")

    elif scene.kind == "credits":
        _scrim(draw, style.width, style.height, top=0.15, bottom=0.1)
        y = int(style.height * 0.12)
        y = _block(draw, scene.heading, _font(style.font_serif, 54), (margin, y, inner), style.fg)
        y += 8
        draw.line([(margin, y), (margin + 160, y)], fill=style.accent, width=5)
        y += 34
        for line in (scene.on_screen_text or "").split("\n"):
            if not line.strip():
                continue
            y = _block(draw, line, _font(style.font_regular, 30), (margin, y, inner), style.muted, leading=1.2)
            y += 14

    else:  # body — text pinned to the lower third
        _scrim(draw, style.width, style.height, top=0.18, bottom=0.5)
        if scene.chapter:
            _block(draw, scene.chapter.upper(), _font(style.font_bold, 26),
                   (margin, int(style.height * 0.1), inner), style.accent)
        y = int(style.height * 0.50)
        if scene.heading:
            y = _block(draw, scene.heading, _font(style.font_serif, 52), (margin, y, inner), style.fg, leading=1.12)
            y += 16
        _block(draw, scene.narration, _font(style.font_regular, 38), (margin, y, inner), "#e8ecf2", leading=1.3)
        if scene.citation_label:
            cy = style.height - int(style.height * 0.11)
            draw.line([(margin, cy - 16), (margin + inner, cy - 16)], fill=style.line, width=2)
            _block(draw, scene.citation_label, _font(style.font_regular, 26), (margin, cy, inner), style.muted)

    # Accent rule along the very bottom, then ribbon + bug last so they sit on top.
    draw.rectangle([0, style.height - 8, style.width, style.height], fill=style.accent)
    if fictional:
        _ribbon(draw, style, "FICTIONAL SUBJECT — DRAMATISATION")
    _bug(draw, style)
    return img


def compose_frame(style, scene, base: Image.Image, fictional=False) -> Image.Image:
    """Flatten base + overlay into a single RGB frame (used by tests/static export)."""
    bg = base_frame(style, base).convert("RGBA")
    bg.alpha_composite(overlay_layer(style, scene, fictional))
    return bg.convert("RGB")
