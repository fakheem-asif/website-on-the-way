"""Wire the stages together, enforcing the review gate before production."""
from __future__ import annotations

import os

from .config import Config
from .models import Dossier
from .stages import assemble, review
from .stages import script as script_stage
from .stages import visuals, voiceover


def produce(dossier: Dossier, cfg: Config, out_dir: str) -> dict:
    """script -> voiceover -> visuals -> assemble. Refuses unreviewed dossiers."""
    excluded = review.assert_ready(dossier)  # raises ReviewGateError if not ready
    os.makedirs(out_dir, exist_ok=True)

    script = script_stage.build(dossier, cfg)
    script_path = os.path.join(out_dir, "script.json")
    script.save(script_path)

    audio = voiceover.run(script, out_dir, cfg)
    vis = visuals.run(script, out_dir, cfg)
    result = assemble.run(script, audio, vis, out_dir, cfg)

    result["script"] = script_path
    result["excluded_claims"] = excluded
    result["used_claims"] = [c.id for c in dossier.verified_claims()]
    return result
