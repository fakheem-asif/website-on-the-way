"""Core data structures shared across pipeline stages.

The whole pipeline is organised around one rule: a factual claim may only
appear in the documentary if it carries at least one verifiable source AND a
human has marked it verified. These dataclasses encode that contract and know
how to (de)serialise themselves to plain JSON so every stage hands off an
auditable artifact on disk.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import json
from dataclasses import dataclass, field
from typing import Any


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


@dataclass
class Source:
    """A citation backing a claim."""

    title: str
    publisher: str = ""
    url: str = ""
    published: str = ""           # ISO date the source was published
    accessed: str = field(default_factory=lambda: _dt.date.today().isoformat())
    source_type: str = "news"     # news | official | transcript | academic | book | placeholder
    note: str = ""

    def short_cite(self) -> str:
        bits = [b for b in (self.publisher or self.title, self.published) if b]
        return " — ".join(bits) if bits else self.title

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Source":
        return cls(**{k: d.get(k, getattr(cls, k, "")) for k in (
            "title", "publisher", "url", "published", "accessed", "source_type", "note")})


@dataclass
class Claim:
    """A single factual statement plus its evidence and review status."""

    id: str
    text: str
    category: str = "general"     # biography | record | timeline | quote | context | general
    sources: list[Source] = field(default_factory=list)
    verified: bool = False        # flipped to True only by a human in the review gate
    reviewer_note: str = ""

    def is_citable(self) -> bool:
        return bool(self.sources) and all(s.source_type != "placeholder" for s in self.sources)

    def to_dict(self) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        d["sources"] = [s.to_dict() for s in self.sources]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Claim":
        return cls(
            id=d["id"],
            text=d["text"],
            category=d.get("category", "general"),
            sources=[Source.from_dict(s) for s in d.get("sources", [])],
            verified=bool(d.get("verified", False)),
            reviewer_note=d.get("reviewer_note", ""),
        )


@dataclass
class Dossier:
    """Output of the research stage; input to the review gate."""

    subject: str
    subject_role: str = ""
    summary: str = ""
    claims: list[Claim] = field(default_factory=list)
    generated_at: str = field(default_factory=_now)
    generator: str = "stub"
    is_fictional: bool = False    # True for the bundled demo subject
    approved: bool = False        # set by the human review gate
    approved_by: str = ""
    approved_at: str = ""

    def verified_claims(self) -> list[Claim]:
        return [c for c in self.claims if c.verified and c.is_citable()]

    def to_dict(self) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        d["claims"] = [c.to_dict() for c in self.claims]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Dossier":
        obj = cls(
            subject=d["subject"],
            subject_role=d.get("subject_role", ""),
            summary=d.get("summary", ""),
            claims=[Claim.from_dict(c) for c in d.get("claims", [])],
            generated_at=d.get("generated_at", _now()),
            generator=d.get("generator", "stub"),
            is_fictional=bool(d.get("is_fictional", False)),
            approved=bool(d.get("approved", False)),
            approved_by=d.get("approved_by", ""),
            approved_at=d.get("approved_at", ""),
        )
        return obj

    def save(self, path: str) -> None:
        _write_json(path, self.to_dict())

    @classmethod
    def load(cls, path: str) -> "Dossier":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))


@dataclass
class Scene:
    """One narrated beat of the documentary."""

    id: str
    chapter: str
    heading: str
    narration: str
    on_screen_text: str = ""
    claim_ids: list[str] = field(default_factory=list)   # provenance back to the dossier
    citation_label: str = ""                             # e.g. "Sources: Reuters, AP"
    visual_query: str = ""                               # search hint for B-roll providers
    kind: str = "body"            # title | disclosure | body | credits
    seconds: float = 0.0          # filled once audio duration is known

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Scene":
        return cls(**{k: d.get(k, getattr(cls, k, None)) for k in (
            "id", "chapter", "heading", "narration", "on_screen_text",
            "claim_ids", "citation_label", "visual_query", "kind", "seconds")})


@dataclass
class Script:
    subject: str
    title: str
    scenes: list[Scene] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    is_fictional: bool = False

    def to_dict(self) -> dict[str, Any]:
        d = dataclasses.asdict(self)
        d["scenes"] = [s.to_dict() for s in self.scenes]
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Script":
        return cls(
            subject=d["subject"],
            title=d["title"],
            scenes=[Scene.from_dict(s) for s in d.get("scenes", [])],
            created_at=d.get("created_at", _now()),
            is_fictional=bool(d.get("is_fictional", False)),
        )

    def save(self, path: str) -> None:
        _write_json(path, self.to_dict())

    @classmethod
    def load(cls, path: str) -> "Script":
        with open(path, "r", encoding="utf-8") as fh:
            return cls.from_dict(json.load(fh))


@dataclass
class Asset:
    """A produced media file plus its provenance (who/what made it)."""

    scene_id: str
    kind: str                     # audio | visual
    path: str
    provider: str = "stub"
    ai_generated: bool = False
    attribution: str = ""
    license: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def _write_json(path: str, data: dict[str, Any]) -> None:
    import os
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
