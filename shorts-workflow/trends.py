import feedparser

GOOGLE_NEWS_RSS = "https://news.google.com/rss/headlines/section/topic/{category}?hl=en-US&gl=US&ceid=US:en"


def fetch_trending(category: str = "TECHNOLOGY", limit: int = 20):
    feed = feedparser.parse(GOOGLE_NEWS_RSS.format(category=category))
    out = []
    for e in feed.entries[:limit]:
        out.append({
            "title": e.title,
            "summary": getattr(e, "summary", ""),
            "link": e.link,
            "published": getattr(e, "published", ""),
        })
    return out
