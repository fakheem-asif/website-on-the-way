"""Stage 4 — voiceover. One audio file per scene; sets each scene's duration."""
from __future__ import annotations

import os

from ..config import Config
from ..models import Asset, Script
from ..providers import get_provider
from ..providers.tts import planned_seconds
from ..util import ffmpeg


def run(script: Script, out_dir: str, cfg: Config) -> list[Asset]:
    provider = get_provider("tts", cfg.providers.get("tts", "stub"))
    ext = getattr(provider, "ext", ".wav")
    audio_dir = os.path.join(out_dir, "audio")
    os.makedirs(audio_dir, exist_ok=True)

    assets: list[Asset] = []
    for scene in script.scenes:
        path = os.path.join(audio_dir, f"{scene.id}{ext}")
        asset = provider.synthesize(scene, path, cfg)
        # Lock the scene's video duration to the actual audio length.
        dur = ffmpeg.probe_duration(asset.path) or planned_seconds(scene, cfg)
        scene.seconds = round(dur, 2)
        assets.append(asset)
    return assets
