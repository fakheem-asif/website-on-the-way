import json
import re


SCRIPT_PROMPT = """You are writing narration for a YouTube Short (vertical, ~45s).

Topic: {title}
Context: {summary}

Rules:
- Target {words} words. Speak in plain spoken English.
- Open with a 5-word hook that creates curiosity or stakes.
- One idea per sentence. Short, punchy sentences.
- Conversational, urgent. No "hey guys" or "in this video".
- No stage directions, no markdown, no emojis, no hashtags.
- End with a one-line question that pushes a comment.
- Output ONLY the narration text. Nothing else."""


KEYWORDS_PROMPT = """You pick stock-footage search terms for a YouTube Short.

Script:
{script}

Return {n} short visual search queries (1-3 words each) that together illustrate the script.
Prefer concrete, filmable nouns over abstract concepts. Avoid brand names.

Output ONLY a JSON array of strings. Example: ["server room","laptop typing","data center"]"""


def write_script(client, model: str, title: str, summary: str, words: int = 110) -> str:
    summary_clean = re.sub(r"<[^>]+>", " ", summary or "").strip()[:600]
    r = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": SCRIPT_PROMPT.format(title=title, summary=summary_clean, words=words),
        }],
        temperature=0.8,
    )
    return r.choices[0].message.content.strip()


def script_to_keywords(client, model: str, script_text: str, n: int = 5) -> list[str]:
    r = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": KEYWORDS_PROMPT.format(script=script_text, n=n),
        }],
        temperature=0.5,
    )
    raw = r.choices[0].message.content.strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        return ["abstract background", "city skyline", "technology", "people working", "nature"][:n]
    try:
        kws = json.loads(match.group(0))
        return [str(k).strip() for k in kws if k][:n]
    except json.JSONDecodeError:
        return ["abstract background", "city skyline", "technology", "people working", "nature"][:n]


def youtube_metadata(client, model: str, title: str, script_text: str, link: str) -> dict:
    prompt = f"""Generate YouTube Shorts metadata for this narration.

Original headline: {title}
Narration: {script_text}

Return JSON with keys:
- "title": <70 chars, curiosity hook, NO clickbait emojis>
- "description": 2-3 sentences, then a blank line, then 5 relevant hashtags including #shorts
- "tags": array of 10 lowercase tags, no #

Output ONLY the JSON."""
    r = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        response_format={"type": "json_object"},
    )
    try:
        meta = json.loads(r.choices[0].message.content)
    except json.JSONDecodeError:
        meta = {"title": title[:70], "description": script_text[:200], "tags": []}
    meta["source"] = link
    return meta
