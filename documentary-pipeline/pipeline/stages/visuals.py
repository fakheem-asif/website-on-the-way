"""Stage 5 — visuals. Base image per scene + the always-on text/citation/bug overlay."""
from __future__ import annotations

import os

from ..config import Config
from ..models import Asset, Script
from ..providers import get_provider
from ..util import cards


def run(script: Script, out_dir: str, cfg: Config) -> list[Asset]:
    provider = get_provider("media", cfg.providers.get("media", "stub"))
    frame_dir = os.path.join(out_dir, "frames")
    os.makedirs(frame_dir, exist_ok=True)

    assets: list[Asset] = []
    for scene in script.scenes:
        base, prov = provider.base_image(scene, cfg)
        base_path = os.path.join(frame_dir, f"{scene.id}.base.png")
        ovl_path = os.path.join(frame_dir, f"{scene.id}.ovl.png")
        cards.base_frame(cfg.style, base).save(base_path)
        cards.overlay_layer(cfg.style, scene, fictional=script.is_fictional).save(ovl_path)
        assets.append(Asset(
            scene_id=scene.id, kind="visual", path=base_path,
            provider=prov.get("provider", "stub"),
            ai_generated=bool(prov.get("ai_generated", True)),
            attribution=prov.get("attribution", ""),
            license=prov.get("license", "")))
    return assets


def overlay_path_for(base_path: str) -> str:
    """Map a base-frame path to its sibling overlay path."""
    return base_path[:-len(".base.png")] + ".ovl.png" if base_path.endswith(".base.png") else base_path
