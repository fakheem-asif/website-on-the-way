import html
import re
import urllib.request
import xml.etree.ElementTree as ET

GOOGLE_NEWS_RSS = "https://news.google.com/rss/headlines/section/topic/{category}?hl=en-US&gl=US&ceid=US:en"


def _strip_html(s: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", s or "")).strip()


def fetch_trending(category: str = "TECHNOLOGY", limit: int = 20):
    url = GOOGLE_NEWS_RSS.format(category=category)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    items = []
    for item in root.findall(".//item")[:limit]:
        items.append({
            "title": _strip_html(item.findtext("title", "")),
            "summary": _strip_html(item.findtext("description", "")),
            "link": (item.findtext("link") or "").strip(),
            "published": (item.findtext("pubDate") or "").strip(),
        })
    return items
