"""Research providers — they produce an *unverified* dossier of claims.

Critical design point: no research provider invents citations. The offline
stub emits clearly-labelled placeholder slots; the LLM provider drafts
candidate claim statements with empty sources. In both cases every claim is
`verified=False`, so the review gate forces a human to attach real sources and
confirm each fact before anything reaches the script. This is what keeps the
"strictly fact-based + cited" guarantee honest even when a model is involved.
"""
from __future__ import annotations

import os

from ..config import Config
from ..models import Claim, Dossier, Source
from .base import LLMProvider, ResearchProvider

_CATEGORIES = [
    ("biography", "early life and background"),
    ("biography", "education and pre-political career"),
    ("timeline", "entry into politics"),
    ("record", "major policy positions and votes"),
    ("record", "signature achievement or legislation"),
    ("context", "notable controversy or criticism"),
    ("quote", "a representative, sourced public statement"),
    ("context", "legacy and current assessment"),
]


def _placeholder(idx: int, subject: str, category: str, topic: str) -> Claim:
    return Claim(
        id=f"c{idx:02d}",
        text=(f"[PLACEHOLDER] Replace with a verified fact about {subject}: {topic}. "
              f"Do not publish until this is rewritten from a real source."),
        category=category,
        sources=[Source(title="ATTACH A REAL SOURCE HERE", source_type="placeholder",
                        note="Placeholder — the review gate will reject this until replaced.")],
        verified=False,
        reviewer_note="Auto-generated slot. Research, rewrite, cite, then mark verified.",
    )


class StubResearch(ResearchProvider):
    """Offline scaffold: structured placeholder claims, nothing fabricated."""

    def research(self, subject: str, cfg: Config) -> Dossier:
        claims = [_placeholder(i + 1, subject, cat, topic)
                  for i, (cat, topic) in enumerate(_CATEGORIES)]
        return Dossier(
            subject=subject,
            subject_role="(fill in role/office)",
            summary=(f"Research scaffold for a documentary on {subject}. Every claim below "
                     "is an empty placeholder — fill each with a fact from a verifiable "
                     "public source, then run the review gate."),
            claims=claims,
            generator="stub",
        )


class LLMResearch(ResearchProvider):
    """Uses an LLM to draft candidate claim statements (still unsourced/unverified)."""

    def __init__(self) -> None:
        # Reuse whichever LLM the operator configured for narration.
        from .base import get_provider
        self._llm: LLMProvider = get_provider("llm", os.environ.get("LLM_PROVIDER", "anthropic"))

    def research(self, subject: str, cfg: Config) -> Dossier:
        system = (
            "You are a documentary researcher. Propose factual claim STATEMENTS to "
            "investigate about the subject. Output one claim per line. Do NOT invent "
            "sources, dates, or quotes. Keep each claim checkable against public record.")
        prompt = (f"Subject: {subject}\nList 8-12 candidate factual claims to verify, "
                  "covering background, career, record, controversies, and legacy.")
        text = self._llm.write_narration(system, prompt)
        claims = []
        for i, line in enumerate(l.strip("-• \t") for l in text.splitlines() if l.strip()):
            claims.append(Claim(
                id=f"c{i + 1:02d}", text=line, category="general", sources=[],
                verified=False,
                reviewer_note="Drafted by LLM. Find and attach real sources, then verify."))
        return Dossier(
            subject=subject,
            summary=f"LLM-drafted research leads for {subject}. Unsourced and unverified by design.",
            claims=claims,
            generator="llm",
        )
