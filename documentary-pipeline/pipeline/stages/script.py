"""Stage 3 — scriptwriting.

Turns the *verified* claims into an ordered set of narrated scenes. Each body
scene maps to exactly one claim (clear provenance), gets narration written from
that claim alone, and carries an on-screen source citation. The title,
AI-disclosure and closing citations scenes are always added.
"""
from __future__ import annotations

import re

from ..config import Config
from ..models import Dossier, Scene, Script, Source
from ..providers import get_provider

# category -> (chapter title, order)
_CHAPTERS = {
    "biography": ("Background", 0),
    "timeline": ("The Rise", 1),
    "record": ("The Record", 2),
    "quote": ("In Their Own Words", 3),
    "context": ("Controversy & Legacy", 4),
    "general": ("Findings", 5),
}
_STOP = set("the a an of to in on and or for with by from at as is was were that this their his her "
            "its into over under after before during about not but also has had have".split())


def _chapter(cat: str) -> tuple[str, int]:
    return _CHAPTERS.get(cat, _CHAPTERS["general"])


def _visual_query(subject: str, text: str) -> str:
    words = [w for w in re.findall(r"[A-Za-z]{4,}", text.lower()) if w not in _STOP]
    return " ".join([subject] + words[:3])


def _citation_label(sources: list[Source]) -> str:
    cites = [s.short_cite() for s in sources if s.source_type != "placeholder"]
    return "Source: " + " · ".join(cites) if cites else ""


def _dedupe_sources(dossier: Dossier) -> list[Source]:
    seen, out = set(), []
    for claim in dossier.verified_claims():
        for s in claim.sources:
            key = (s.title, s.publisher, s.url)
            if key not in seen:
                seen.add(key)
                out.append(s)
    return out


def build(dossier: Dossier, cfg: Config) -> Script:
    llm = get_provider("llm", cfg.providers.get("llm", "stub"))
    verified = dossier.verified_claims()

    title = cfg.title_template.format(subject=dossier.subject)
    scenes: list[Scene] = [
        Scene(id="s_title", chapter="", heading=title, kind="title",
              on_screen_text=(cfg.subtitle + (f"  ·  {dossier.subject_role}" if dossier.subject_role else "")),
              narration=f"{title}. {cfg.subtitle}."),
        Scene(id="s_disclosure", chapter="", heading="AI-Assisted Production", kind="disclosure",
              narration=cfg.disclosure_statement),
    ]

    # Body scenes grouped by chapter order, one claim each.
    ordered = sorted(verified, key=lambda c: (_chapter(c.category)[1], c.id))
    for i, claim in enumerate(ordered, start=1):
        chapter, _ = _chapter(claim.category)
        prompt = (
            f"CHAPTER: {chapter}\nHEADING: \n"
            "CLAIMS (use ONLY these; invent nothing):\n"
            f"- [{claim.id}] {claim.text} (Sources: {_citation_label(claim.sources)})\n"
            "Write 2-3 sentences of documentary narration conveying ONLY this claim."
        )
        narration = llm.write_narration("", prompt).strip() or claim.text
        scenes.append(Scene(
            id=f"s_body_{i:02d}", chapter=chapter, heading="", kind="body",
            narration=narration, claim_ids=[claim.id],
            citation_label=_citation_label(claim.sources),
            visual_query=_visual_query(dossier.subject, claim.text)))

    # Closing citations, paginated into one or more credits scenes.
    lines = [f"{i}. {s.short_cite()}" + (f" — {s.url}" if s.url else "")
             for i, s in enumerate(_dedupe_sources(dossier), start=1)]
    per_page = 8
    pages = [lines[i:i + per_page] for i in range(0, len(lines), per_page)] or [["(no sources listed)"]]
    for idx, page in enumerate(pages, start=1):
        suffix = f" ({idx}/{len(pages)})" if len(pages) > 1 else ""
        scenes.append(Scene(
            id=f"s_credits_{idx}", chapter="", heading=f"Sources & Citations{suffix}",
            kind="credits", on_screen_text="\n".join(page),
            narration="Every factual claim in this film is drawn from the public sources listed here."))

    return Script(subject=dossier.subject, title=title, scenes=scenes,
                  is_fictional=dossier.is_fictional)
