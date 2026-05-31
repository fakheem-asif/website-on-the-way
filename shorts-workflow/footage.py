import requests

PEXELS_SEARCH = "https://api.pexels.com/videos/search"


def fetch_video(query: str, out_path: str, api_key: str, min_duration: float = 4.0) -> str:
    r = requests.get(
        PEXELS_SEARCH,
        headers={"Authorization": api_key},
        params={"query": query, "orientation": "portrait", "per_page": 15, "size": "medium"},
        timeout=30,
    )
    r.raise_for_status()
    videos = r.json().get("videos", [])
    if not videos:
        raise RuntimeError(f"no Pexels results for '{query}'")

    for v in videos:
        if v.get("duration", 0) < min_duration:
            continue
        files = sorted(
            [f for f in v.get("video_files", []) if f.get("height", 0) >= f.get("width", 0)],
            key=lambda f: f.get("height", 0),
            reverse=True,
        )
        for vf in files:
            if vf.get("height", 0) >= 1280:
                vr = requests.get(vf["link"], stream=True, timeout=60)
                vr.raise_for_status()
                with open(out_path, "wb") as out:
                    for chunk in vr.iter_content(8192):
                        out.write(chunk)
                return out_path
    raise RuntimeError(f"no vertical HD file for '{query}'")
