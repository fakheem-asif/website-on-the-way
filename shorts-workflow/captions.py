def _fmt_ts(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


def srt_from_boundaries(boundaries: list[dict], words_per_caption: int = 3) -> str:
    if not boundaries:
        return ""
    cues = []
    for i in range(0, len(boundaries), words_per_caption):
        group = boundaries[i : i + words_per_caption]
        start = group[0]["start"]
        end = group[-1]["start"] + group[-1]["duration"]
        text = " ".join(w["text"] for w in group).upper()
        cues.append((start, end, text))

    out = []
    for idx, (start, end, text) in enumerate(cues, 1):
        out.append(f"{idx}\n{_fmt_ts(start)} --> {_fmt_ts(end)}\n{text}\n")
    return "\n".join(out)
