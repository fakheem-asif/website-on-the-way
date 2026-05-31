"""Small text helpers: slugs, duration estimates, SRT timecodes, wrapping."""
from __future__ import annotations

import re


def slugify(value: str) -> str:
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[\s_-]+", "-", value) or "subject"


def estimate_seconds(text: str, words_per_second: float, minimum: float) -> float:
    words = len(re.findall(r"\S+", text))
    return max(minimum, round(words / max(words_per_second, 0.5), 2))


def srt_timecode(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    millis = int(round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def build_srt(cues: list[tuple[float, float, str]]) -> str:
    """cues: list of (start_s, end_s, text)."""
    out: list[str] = []
    for i, (start, end, text) in enumerate(cues, start=1):
        out.append(str(i))
        out.append(f"{srt_timecode(start)} --> {srt_timecode(end)}")
        out.append(text.strip())
        out.append("")
    return "\n".join(out)


def wrap_to_width(draw, text: str, font, max_width: int) -> list[str]:
    """Greedy word-wrap using a Pillow draw context to measure pixels."""
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if _text_width(draw, trial, font) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _text_width(draw, text: str, font) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]
