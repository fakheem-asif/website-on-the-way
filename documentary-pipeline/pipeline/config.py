"""Configuration: visual style, pacing, providers, and disclosure wording.

Loaded from a JSON file (see config.example.json) merged over defaults. Note
that disclosure is *wording only* — the assemble stage always renders the
disclosure card, citations, and the on-screen bug regardless of config.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

_FONT_DIR = "/usr/share/fonts/truetype/dejavu"


@dataclass
class Style:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    motion: bool = True
    bg: str = "#0e1116"
    fg: str = "#f2f4f8"
    muted: str = "#aeb6c2"
    line: str = "#6b7480"
    accent: str = "#e0b34a"
    font_regular: str = f"{_FONT_DIR}/DejaVuSans.ttf"
    font_bold: str = f"{_FONT_DIR}/DejaVuSans-Bold.ttf"
    font_serif: str = f"{_FONT_DIR}/DejaVuSerif.ttf"
    bug_label: str = "AI-ASSISTED"


_DEFAULT_DISCLOSURE = (
    "This documentary was produced with AI assistance. The narration voice and "
    "some visuals are AI-generated. Every factual claim is drawn from cited "
    "public sources, listed in full in the closing credits."
)


@dataclass
class Config:
    style: Style = field(default_factory=Style)
    words_per_second: float = 2.6
    min_scene_seconds: float = 3.5
    output_dir: str = "build"
    title_template: str = "{subject}"
    subtitle: str = "An AI-assisted documentary"
    disclosure_statement: str = _DEFAULT_DISCLOSURE
    providers: dict[str, str] = field(default_factory=lambda: {
        "research": "stub", "llm": "stub", "tts": "stub", "media": "stub",
    })

    @classmethod
    def load(cls, path: str | None) -> "Config":
        cfg = cls()
        if not path:
            return cfg
        with open(path, "r", encoding="utf-8") as fh:
            data: dict[str, Any] = json.load(fh)
        if "style" in data:
            for k, v in data["style"].items():
                if hasattr(cfg.style, k):
                    setattr(cfg.style, k, v)
        for k in ("words_per_second", "min_scene_seconds", "output_dir",
                  "title_template", "subtitle", "disclosure_statement"):
            if k in data:
                setattr(cfg, k, data[k])
        if "providers" in data:
            cfg.providers.update(data["providers"])
        if "disclosure" in data:  # convenience block
            disc = data["disclosure"]
            if "label" in disc:
                cfg.style.bug_label = disc["label"]
            if "statement" in disc:
                cfg.disclosure_statement = disc["statement"]
        return cfg
