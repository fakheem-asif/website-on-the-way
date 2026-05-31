"""Provider interfaces and a tiny registry/factory.

Each capability (research, llm, tts, media) has an abstract base and one or
more concrete providers. The config picks providers by name; `get_provider`
resolves them. Real adapters live in sibling modules and are imported lazily
so the stub path never requires optional dependencies or API keys.
"""
from __future__ import annotations

import abc

from ..config import Config
from ..models import Asset, Dossier, Scene


class ResearchProvider(abc.ABC):
    name = "research"

    @abc.abstractmethod
    def research(self, subject: str, cfg: Config) -> Dossier:
        ...


class LLMProvider(abc.ABC):
    name = "llm"

    @abc.abstractmethod
    def write_narration(self, system: str, prompt: str) -> str:
        ...


class TTSProvider(abc.ABC):
    name = "tts"

    @abc.abstractmethod
    def synthesize(self, scene: Scene, out_path: str, cfg: Config) -> Asset:
        ...


class MediaProvider(abc.ABC):
    name = "media"

    @abc.abstractmethod
    def base_image(self, scene: Scene, cfg: Config):
        """Return (PIL.Image base frame, provenance dict).

        provenance keys: provider, ai_generated, attribution, license.
        Text/citation/bug overlays are applied later by util.cards.compose_frame,
        so this returns only the underlying visual (a styled background offline,
        or fetched B-roll in real mode).
        """
        ...


def get_provider(kind: str, name: str):
    """Resolve a provider instance by capability + name."""
    name = (name or "stub").lower()
    if kind == "research":
        from . import research as m
        return {"stub": m.StubResearch, "llm": m.LLMResearch}.get(name, m.StubResearch)()
    if kind == "llm":
        from . import llm as m
        return {"stub": m.StubLLM, "anthropic": m.AnthropicLLM, "openai": m.OpenAILLM}.get(name, m.StubLLM)()
    if kind == "tts":
        from . import tts as m
        return {"stub": m.StubTTS, "elevenlabs": m.ElevenLabsTTS, "openai": m.OpenAITTS}.get(name, m.StubTTS)()
    if kind == "media":
        from . import media as m
        return {"stub": m.StubMedia, "pexels": m.PexelsMedia, "wikimedia": m.WikimediaMedia}.get(name, m.StubMedia)()
    raise ValueError(f"unknown provider kind: {kind}")
