"""Text-to-speech providers.

Offline stub produces a duration-matched silent track (the burned-in captions
carry the words). Real adapters use a generic synthetic narrator voice. Policy:
never clone the subject's voice — narration is an out-of-character narrator, and
the disclosure card + bug make the synthetic nature explicit.
"""
from __future__ import annotations

import os

from ..config import Config
from ..models import Asset, Scene
from ..util import ffmpeg
from ..util.text import estimate_seconds
from .base import TTSProvider

_FLOORS = {"title": 4.0, "disclosure": 7.0, "credits": 6.0, "body": 0.0}


def planned_seconds(scene: Scene, cfg: Config) -> float:
    est = estimate_seconds(scene.narration or scene.heading, cfg.words_per_second, cfg.min_scene_seconds)
    return round(max(est, _FLOORS.get(scene.kind, 0.0)), 2)


class StubTTS(TTSProvider):
    """Silent, duration-matched placeholder audio."""

    ext = ".wav"

    def synthesize(self, scene: Scene, out_path: str, cfg: Config) -> Asset:
        seconds = planned_seconds(scene, cfg)
        ffmpeg.silent_audio(out_path, seconds)
        return Asset(scene_id=scene.id, kind="audio", path=out_path, provider="stub-silent",
                     ai_generated=False, attribution="Silent placeholder (captions carry narration)")


class ElevenLabsTTS(TTSProvider):
    ext = ".mp3"

    def __init__(self) -> None:
        try:
            import requests  # noqa: F401
        except Exception as exc:
            raise RuntimeError("ElevenLabs provider needs `pip install requests`.") from exc
        self._key = os.environ.get("ELEVENLABS_API_KEY")
        if not self._key:
            raise RuntimeError("Set ELEVENLABS_API_KEY to use the elevenlabs provider.")
        # A generic narrator voice. Do NOT point this at a clone of the subject.
        self._voice = os.environ.get("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

    def synthesize(self, scene: Scene, out_path: str, cfg: Config) -> Asset:
        import requests
        resp = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{self._voice}",
            headers={"xi-api-key": self._key, "accept": "audio/mpeg"},
            json={"text": scene.narration, "model_id": "eleven_multilingual_v2"}, timeout=120)
        resp.raise_for_status()
        with open(out_path, "wb") as fh:
            fh.write(resp.content)
        return Asset(scene_id=scene.id, kind="audio", path=out_path, provider="elevenlabs",
                     ai_generated=True, attribution="Synthetic narrator voice (not the subject's voice)")


class OpenAITTS(TTSProvider):
    ext = ".mp3"

    def __init__(self) -> None:
        try:
            import openai  # noqa: F401
        except Exception as exc:
            raise RuntimeError("OpenAI TTS needs `pip install openai`.") from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("Set OPENAI_API_KEY to use the openai tts provider.")
        import openai
        self._client = openai.OpenAI()
        self._voice = os.environ.get("OPENAI_TTS_VOICE", "onyx")

    def synthesize(self, scene: Scene, out_path: str, cfg: Config) -> Asset:
        with self._client.audio.speech.with_streaming_response.create(
                model=os.environ.get("OPENAI_TTS_MODEL", "tts-1"),
                voice=self._voice, input=scene.narration) as resp:
            resp.stream_to_file(out_path)
        return Asset(scene_id=scene.id, kind="audio", path=out_path, provider="openai",
                     ai_generated=True, attribution="Synthetic narrator voice (not the subject's voice)")
