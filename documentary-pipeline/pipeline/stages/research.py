"""Stage 1 — research. Produces an UNVERIFIED dossier of cited claims."""
from __future__ import annotations

from ..config import Config
from ..models import Dossier
from ..providers import get_provider


def run(subject: str, cfg: Config) -> Dossier:
    provider = get_provider("research", cfg.providers.get("research", "stub"))
    dossier = provider.research(subject, cfg)
    return dossier
