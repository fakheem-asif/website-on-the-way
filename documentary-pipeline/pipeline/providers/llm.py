"""LLM providers for narration writing.

The stub composes narration straight from the verified claim text passed in the
prompt — it adds connective grammar but never new facts. Real adapters send the
same strict system prompt ("use only the supplied claims, invent nothing") to a
hosted model. Either way the script stage post-checks that narration introduces
no un-cited material.
"""
from __future__ import annotations

import os
import re

from .base import LLMProvider

_CLAIM_LINE = re.compile(r"^-\s*\[(?P<id>[^\]]+)\]\s*(?P<text>.*?)\s*(?:\(Sources:.*\))?\s*$")

SYSTEM_PROMPT = (
    "You are writing narration for a fact-based documentary. You will be given a "
    "scene heading and a set of VERIFIED, CITED claims. Write engaging documentary "
    "narration that conveys ONLY the information in those claims. Do not add facts, "
    "dates, names, quotes, motivations, or speculation that is not present in the "
    "claims. Do not editorialise. Output only the narration prose."
)


def _claims_from_prompt(prompt: str) -> list[str]:
    out = []
    for line in prompt.splitlines():
        m = _CLAIM_LINE.match(line.strip())
        if m and m.group("text"):
            out.append(m.group("text").strip())
    return out


class StubLLM(LLMProvider):
    """Deterministic, offline. Stitches verified claim sentences into narration."""

    def write_narration(self, system: str, prompt: str) -> str:
        claims = _claims_from_prompt(prompt)
        if not claims:
            # Fall back to the heading line for non-claim scenes.
            for line in prompt.splitlines():
                if line.upper().startswith("HEADING:"):
                    return line.split(":", 1)[1].strip()
            return ""
        sentences = []
        for text in claims:
            text = text.strip()
            if not text.endswith((".", "!", "?")):
                text += "."
            sentences.append(text[0].upper() + text[1:])
        return " ".join(sentences)


class AnthropicLLM(LLMProvider):
    def __init__(self) -> None:
        try:
            import anthropic  # noqa: F401
        except Exception as exc:
            raise RuntimeError("Anthropic provider needs `pip install anthropic`.") from exc
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("Set ANTHROPIC_API_KEY to use the anthropic provider.")
        import anthropic
        self._client = anthropic.Anthropic()
        self._model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")

    def write_narration(self, system: str, prompt: str) -> str:
        msg = self._client.messages.create(
            model=self._model, max_tokens=1024, system=system or SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}])
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text").strip()


class OpenAILLM(LLMProvider):
    def __init__(self) -> None:
        try:
            import openai  # noqa: F401
        except Exception as exc:
            raise RuntimeError("OpenAI provider needs `pip install openai`.") from exc
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("Set OPENAI_API_KEY to use the openai provider.")
        import openai
        self._client = openai.OpenAI()
        self._model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def write_narration(self, system: str, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model, max_tokens=1024,
            messages=[{"role": "system", "content": system or SYSTEM_PROMPT},
                      {"role": "user", "content": prompt}])
        return (resp.choices[0].message.content or "").strip()
