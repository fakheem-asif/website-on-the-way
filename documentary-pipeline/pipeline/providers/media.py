"""Visual base-image providers.

Each returns the underlying frame only; captions, citation strip and the
AI-ASSISTED bug are layered on afterwards by util.cards.compose_frame. Title,
disclosure and credits scenes always use a styled background (they are
text-heavy); only body scenes pull B-roll in real mode.
"""
from __future__ import annotations

import io
import os

from PIL import Image

from ..config import Config
from ..models import Scene
from ..util import cards
from .base import MediaProvider

_TEXTY = {"title", "disclosure", "credits"}


class StubMedia(MediaProvider):
    """Offline: every frame is a styled background."""

    def base_image(self, scene: Scene, cfg: Config):
        return cards.background(cfg.style), {
            "provider": "stub", "ai_generated": True,
            "attribution": "Generated background graphic", "license": "n/a"}


class PexelsMedia(MediaProvider):
    """Stock B-roll via the Pexels API (untested offline; verify before production)."""

    def __init__(self) -> None:
        try:
            import requests  # noqa: F401
        except Exception as exc:
            raise RuntimeError("Pexels provider needs `pip install requests`.") from exc
        self._key = os.environ.get("PEXELS_API_KEY")
        if not self._key:
            raise RuntimeError("Set PEXELS_API_KEY to use the pexels provider.")

    def base_image(self, scene: Scene, cfg: Config):
        if scene.kind in _TEXTY or not scene.visual_query:
            return cards.background(cfg.style), {
                "provider": "stub", "ai_generated": True,
                "attribution": "Generated background graphic", "license": "n/a"}
        import requests
        r = requests.get("https://api.pexels.com/v1/search",
                         headers={"Authorization": self._key},
                         params={"query": scene.visual_query, "per_page": 1, "orientation": "landscape"},
                         timeout=60)
        r.raise_for_status()
        photos = r.json().get("photos", [])
        if not photos:
            return cards.background(cfg.style), {
                "provider": "pexels", "ai_generated": False,
                "attribution": f"No Pexels result for '{scene.visual_query}'", "license": "Pexels"}
        photo = photos[0]
        img_bytes = requests.get(photo["src"]["large2x"], timeout=60).content
        return Image.open(io.BytesIO(img_bytes)), {
            "provider": "pexels", "ai_generated": False,
            "attribution": f"Photo by {photo.get('photographer', 'unknown')} (Pexels)",
            "license": "Pexels License"}


class WikimediaMedia(MediaProvider):
    """Public-domain / CC imagery via Wikimedia Commons (untested offline)."""

    def __init__(self) -> None:
        try:
            import requests  # noqa: F401
        except Exception as exc:
            raise RuntimeError("Wikimedia provider needs `pip install requests`.") from exc

    def base_image(self, scene: Scene, cfg: Config):
        if scene.kind in _TEXTY or not scene.visual_query:
            return cards.background(cfg.style), {
                "provider": "stub", "ai_generated": True,
                "attribution": "Generated background graphic", "license": "n/a"}
        import requests
        api = "https://commons.wikimedia.org/w/api.php"
        s = requests.get(api, params={
            "action": "query", "format": "json", "generator": "search",
            "gsrnamespace": 6, "gsrsearch": scene.visual_query, "gsrlimit": 1,
            "prop": "imageinfo", "iiprop": "url|extmetadata", "iiurlwidth": cfg.style.width,
        }, headers={"User-Agent": "documentary-pipeline/1.0"}, timeout=60).json()
        pages = (s.get("query", {}) or {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            url = info.get("thumburl") or info.get("url")
            if not url:
                continue
            meta = info.get("extmetadata", {})
            artist = (meta.get("Artist", {}) or {}).get("value", "Wikimedia Commons")
            lic = (meta.get("LicenseShortName", {}) or {}).get("value", "see Commons")
            img_bytes = requests.get(url, headers={"User-Agent": "documentary-pipeline/1.0"}, timeout=60).content
            return Image.open(io.BytesIO(img_bytes)), {
                "provider": "wikimedia", "ai_generated": False,
                "attribution": f"{artist} via Wikimedia Commons", "license": lic}
        return cards.background(cfg.style), {
            "provider": "wikimedia", "ai_generated": False,
            "attribution": f"No Commons result for '{scene.visual_query}'", "license": "n/a"}
