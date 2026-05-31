import json
import os
import subprocess
from pathlib import Path


def _run(cmd: list[str]):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{proc.stderr[-2000:]}")
    return proc


def probe_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(r.stdout)["format"]["duration"])


def _normalize(in_path: str, out_path: str):
    _run([
        "ffmpeg", "-y", "-i", in_path,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30",
        "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", out_path,
    ])


def _escape_for_subtitles_filter(path: str) -> str:
    # ffmpeg subtitles filter interprets ':' as an argument separator and '\' as escape.
    p = path.replace("\\", "/")
    p = p.replace(":", r"\:")
    p = p.replace("'", r"\'")
    return p


def assemble(footage_paths: list[str], audio_path: str, srt_path: str,
             out_path: str, workdir: str) -> str:
    audio_dur = probe_duration(audio_path)
    workdir = Path(workdir)

    normalized = []
    for i, fp in enumerate(footage_paths):
        out = workdir / f"norm_{i}.mp4"
        _normalize(fp, str(out))
        normalized.append(str(out))

    total = sum(probe_duration(p) for p in normalized)
    repeats = max(1, int(audio_dur // total) + 1)
    concat_file = workdir / "concat.txt"
    with open(concat_file, "w") as f:
        for _ in range(repeats):
            for p in normalized:
                f.write(f"file '{os.path.abspath(p)}'\n")

    style = (
        "Fontname=Arial,Fontsize=18,Bold=-1,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,"
        "BorderStyle=1,Outline=3,Shadow=0,"
        "Alignment=2,MarginV=240"
    )
    sub_path = _escape_for_subtitles_filter(os.path.abspath(srt_path))
    vf = f"subtitles='{sub_path}':force_style='{style}'"

    _run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-i", audio_path,
        "-vf", vf,
        "-t", f"{audio_dur:.3f}",
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        out_path,
    ])
    return out_path
