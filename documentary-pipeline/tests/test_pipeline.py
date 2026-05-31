"""Fast guarantees — no ffmpeg/encode. Run: python -m unittest -v (from project root)."""
import unittest

from pipeline.config import Config
from pipeline.models import Claim, Dossier, Source
from pipeline.providers import get_provider
from pipeline.stages import script as script_stage
from pipeline.stages.review import ReviewGateError, assert_ready


def _real_claim(cid, text, category="record"):
    return Claim(id=cid, text=text, category=category, verified=True,
                 sources=[Source(title="Example Report", publisher="Example News",
                                 url="https://example.org/x", published="2020-01-01")])


def _approved_dossier():
    d = Dossier(subject="Test Subject",
                claims=[_real_claim("c01", "Subject did the first thing", "biography"),
                        _real_claim("c02", "Subject did the second thing", "record")])
    d.approved = True
    return d


class IntegrityTests(unittest.TestCase):
    def test_placeholder_claims_are_not_citable(self):
        dossier = get_provider("research", "stub").research("Some Person", Config())
        self.assertTrue(dossier.claims)
        self.assertFalse(any(c.is_citable() for c in dossier.claims))

    def test_gate_blocks_unapproved(self):
        d = _approved_dossier()
        d.approved = False
        with self.assertRaises(ReviewGateError):
            assert_ready(d)

    def test_gate_blocks_placeholder_only_even_if_approved(self):
        d = get_provider("research", "stub").research("Some Person", Config())
        d.approved = True  # approved, but every claim is a placeholder
        with self.assertRaises(ReviewGateError):
            assert_ready(d)

    def test_gate_passes_with_verified_cited_claims(self):
        excluded = assert_ready(_approved_dossier())
        self.assertEqual(excluded, [])


class ScriptTests(unittest.TestCase):
    def setUp(self):
        self.script = script_stage.build(_approved_dossier(), Config())

    def test_has_title_disclosure_and_credits(self):
        kinds = [s.kind for s in self.script.scenes]
        self.assertEqual(kinds[0], "title")
        self.assertEqual(kinds[1], "disclosure")
        self.assertIn("credits", kinds)

    def test_every_body_scene_is_cited_and_traceable(self):
        body = [s for s in self.script.scenes if s.kind == "body"]
        self.assertEqual(len(body), 2)
        for scene in body:
            self.assertTrue(scene.claim_ids, "body scene must trace back to a claim")
            self.assertTrue(scene.citation_label.startswith("Source:"))

    def test_unverified_claims_are_excluded(self):
        d = _approved_dossier()
        d.claims.append(Claim(id="c99", text="unverified rumour", verified=False,
                              sources=[Source(title="x")]))
        script = script_stage.build(d, Config())
        used = {cid for s in script.scenes for cid in s.claim_ids}
        self.assertNotIn("c99", used)


if __name__ == "__main__":
    unittest.main()
