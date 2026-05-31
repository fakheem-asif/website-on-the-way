"""Thin wrapper over an ffmpeg binary.

Prefers the static binary shipped by `imageio-ffmpeg` (so the pipeline runs
with zero system installs) and falls back to a system `ffmpeg` on PATH.
ffprobe is intentionally avoided — `imageio-ffmpeg` does not bundle it — so
duration is read back through ffmpeg's null muxer when needed.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess


def ffmpeg_exe() -> str:
    env = os.environ.get("FFMPEG_BINARY")
    if env and os.path.exists(env):
        return env
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise RuntimeError(
        "No ffmpeg found. Install with `pip install imageio-ffmpeg` "
        "or put ffmpeg on PATH.")


def _run(args: list[str]) -> subprocess.CompletedProcess:
    proc = subprocess.run([ffmpeg_exe(), "-hide_banner", "-y", *args],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        tail = proc.stderr[-1800:]
        raise RuntimeError(f"ffmpeg failed (exit {proc.returncode}):\n{tail}")
    return proc


def silent_audio(out_path: str, seconds: float, sample_rate: int = 48000) -> None:
    """A duration-matched silent track — the offline TTS stand-in."""
    _run(["-f", "lavfi", "-i", f"anullsrc=r={sample_rate}:cl=stereo",
          "-t", f"{seconds:.3f}", "-c:a", "pcm_s16le", out_path])


def probe_duration(path: str) -> float:
    """Read a media file's duration by decoding to the null muxer."""
    proc = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", path, "-f", "null", "-"],
                          capture_output=True, text=True)
    times = re.findall(r"time=(\d+):(\d+):(\d+\.\d+)", proc.stderr)
    if not times:
        return 0.0
    h, m, s = times[-1]
    return int(h) * 3600 + int(m) * 60 + float(s)


def scene_clip(base_path: str, overlay_path: str, audio_path: str, out_path: str, *,
               seconds: float, width: int, height: int, fps: int, motion: bool) -> None:
    """Encode one scene: base image (optionally Ken Burns) + fixed overlay + audio.

    The overlay (text, citation, AI bug) is composited AFTER any zoom so it stays
    pixel-fixed and fully on-screen. Uniform encode params let concat stream-copy.
    """
    frames = max(1, int(round(fps * seconds)))
    if motion:
        # Ken Burns the base underneath; oversample first to reduce shimmer.
        base = (f"[0:v]scale={width*2}:{height*2},"
                f"zoompan=z='min(zoom+0.0008,1.12)':d={frames}:"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"s={width}x{height}:fps={fps},setsar=1[bg]")
    else:
        base = f"[0:v]scale={width}:{height},setsar=1,fps={fps}[bg]"
    fc = f"{base};[bg][1:v]overlay=0:0,format=yuv420p[v]"
    _run([
        "-loop", "1", "-t", f"{seconds:.3f}", "-i", base_path,
        "-loop", "1", "-t", f"{seconds:.3f}", "-i", overlay_path,
        "-i", audio_path,
        "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-r", str(fps), "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        "-t", f"{seconds:.3f}", "-movflags", "+faststart", out_path,
    ])


def concat(clip_paths: list[str], out_path: str) -> None:
    """Concatenate uniformly-encoded clips without re-encoding."""
    list_file = out_path + ".concat.txt"
    with open(list_file, "w", encoding="utf-8") as fh:
        for clip in clip_paths:
            fh.write(f"file '{os.path.abspath(clip)}'\n")
    try:
        _run(["-f", "concat", "-safe", "0", "-i", list_file, "-c", "copy",
              "-movflags", "+faststart", out_path])
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)
