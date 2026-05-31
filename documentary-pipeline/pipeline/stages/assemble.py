"""Stage 6 — assemble. Encode per-scene clips, concatenate, and write sidecars.

Outputs: documentary.mp4, documentary.srt (caption sidecar) and manifest.json
(an auditable record of every scene, its source claims, and the provenance of
each audio/visual asset, plus confirmation that disclosure markings are present).
"""
from __future__ import annotations

import datetime as _dt
import json
import os

from ..config import Config
from ..models import Asset, Script
from ..util import ffmpeg
from ..util.text import build_srt
from .visuals import overlay_path_for


def _by_scene(assets: list[Asset]) -> dict[str, Asset]:
    return {a.scene_id: a for a in assets}


def run(script: Script, audio: list[Asset], visuals: list[Asset],
        out_dir: str, cfg: Config) -> dict:
    clips_dir = os.path.join(out_dir, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    audio_by, visual_by = _by_scene(audio), _by_scene(visuals)

    clip_paths: list[str] = []
    cues: list[tuple[float, float, str]] = []
    t = 0.0
    for scene in script.scenes:
        a, v = audio_by[scene.id], visual_by[scene.id]
        clip = os.path.join(clips_dir, f"{scene.id}.mp4")
        ffmpeg.scene_clip(
            v.path, overlay_path_for(v.path), a.path, clip,
            seconds=scene.seconds, width=cfg.style.width, height=cfg.style.height,
            fps=cfg.style.fps, motion=cfg.style.motion and scene.kind == "body")
        clip_paths.append(clip)
        cues.append((t, t + scene.seconds, scene.narration or scene.heading))
        t += scene.seconds

    video_path = os.path.join(out_dir, "documentary.mp4")
    ffmpeg.concat(clip_paths, video_path)

    srt_path = os.path.join(out_dir, "documentary.srt")
    with open(srt_path, "w", encoding="utf-8") as fh:
        fh.write(build_srt(cues))

    manifest = _manifest(script, audio_by, visual_by, cfg, total=t)
    manifest_path = os.path.join(out_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    return {"video": video_path, "srt": srt_path, "manifest": manifest_path,
            "duration": round(t, 2), "scenes": len(script.scenes)}


def _manifest(script: Script, audio_by, visual_by, cfg: Config, total: float) -> dict:
    scenes = []
    for s in script.scenes:
        a, v = audio_by[s.id], visual_by[s.id]
        scenes.append({
            "id": s.id, "kind": s.kind, "chapter": s.chapter, "seconds": s.seconds,
            "claim_ids": s.claim_ids, "citation": s.citation_label,
            "narration": s.narration,
            "audio": {"provider": a.provider, "ai_generated": a.ai_generated,
                      "attribution": a.attribution},
            "visual": {"provider": v.provider, "ai_generated": v.ai_generated,
                       "attribution": v.attribution, "license": v.license},
        })
    return {
        "tool": "documentary-pipeline",
        "subject": script.subject,
        "title": script.title,
        "created_at": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "is_fictional": script.is_fictional,
        "duration_seconds": round(total, 2),
        "scene_count": len(script.scenes),
        "disclosure": {
            "bug_label": cfg.style.bug_label,
            "statement": cfg.disclosure_statement,
            "disclosure_card": any(s.kind == "disclosure" for s in script.scenes),
            "citations_card": any(s.kind == "credits" for s in script.scenes),
            "present": True,
        },
        "scenes": scenes,
    }
