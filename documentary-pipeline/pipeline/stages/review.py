"""Stage 2 — the human review gate.

Nothing downstream runs until a person has (a) confirmed each claim against its
source and marked it verified, and (b) approved the dossier as a whole. This is
the single most important integrity control in the pipeline, so the check is
strict and cannot be satisfied by placeholder or unsourced claims.
"""
from __future__ import annotations

import datetime as _dt

from ..models import Dossier


class ReviewGateError(RuntimeError):
    """Raised when production is attempted on an unreviewed/unapproved dossier."""


def assert_ready(dossier: Dossier) -> list[str]:
    """Raise unless the dossier is approved with >=1 verified, citable claim.

    Returns the ids of claims that will be EXCLUDED (unverified or uncited) so
    the caller can report them.
    """
    if not dossier.approved:
        raise ReviewGateError(
            "Dossier is not approved. Review it and run `review`, or hand-edit the "
            "reviewed JSON to set \"approved\": true after verifying every claim.")
    verified = dossier.verified_claims()
    if not verified:
        raise ReviewGateError(
            "No verified, citable claims. Each used claim needs >=1 real (non-placeholder) "
            "source and \"verified\": true. Nothing can be produced from unverified material.")
    excluded = [c.id for c in dossier.claims if c not in verified]
    return excluded


def interactive(dossier: Dossier, reviewer: str = "", approve_all: bool = False) -> Dossier:
    """Walk a human through verifying each claim, then approve. Mutates + returns."""
    if approve_all:
        print("\n  WARNING: --approve-all marks every citable claim verified WITHOUT human\n"
              "  fact-checking. Use only for testing/demos, never for publication.\n")
        for claim in dossier.claims:
            if claim.is_citable():
                claim.verified = True
        return _stamp(dossier, reviewer or "approve-all")

    print(f"\nReview gate for: {dossier.subject}\n" + "=" * 60)
    for claim in dossier.claims:
        print(f"\n[{claim.id}] ({claim.category}) {claim.text}")
        if claim.sources:
            for s in claim.sources:
                tag = " (PLACEHOLDER)" if s.source_type == "placeholder" else ""
                print(f"    src: {s.short_cite()} {s.url}{tag}")
        else:
            print("    src: (none)")
        if not claim.is_citable():
            print("    -> not citable yet (needs a real source); leaving unverified.")
            continue
        ans = input("    Verified against its source? [y/N] ").strip().lower()
        claim.verified = ans in ("y", "yes")
        if claim.verified:
            note = input("    Reviewer note (optional): ").strip()
            if note:
                claim.reviewer_note = note

    n = len(dossier.verified_claims())
    print(f"\n{n} claim(s) verified.")
    if n and input("Approve this dossier for production? [y/N] ").strip().lower() in ("y", "yes"):
        return _stamp(dossier, reviewer or input("Approver name: ").strip() or "anonymous")
    dossier.approved = False
    print("Not approved.")
    return dossier


def _stamp(dossier: Dossier, reviewer: str) -> Dossier:
    dossier.approved = True
    dossier.approved_by = reviewer
    dossier.approved_at = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    return dossier
