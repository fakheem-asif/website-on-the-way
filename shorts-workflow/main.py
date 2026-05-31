import argparse
import asyncio
import datetime
import json
import os
import re
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv
from openai import OpenAI

import assemble
import captions
import footage
import script
import trends
import tts


def slugify(s: str, max_len: int = 50) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s[:max_len] or "short"


async def run(cfg: dict, topic_index: int = 0):
    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("error: OPENAI_API_KEY not set (copy .env.example to .env)")
    if not os.environ.get("PEXELS_API_KEY"):
        sys.exit("error: PEXELS_API_KEY not set (copy .env.example to .env)")

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    pexels_key = os.environ["PEXELS_API_KEY"]
    model = cfg["model"]

    print(f"[1/7] Fetching trending {cfg['news_category']} stories...")
    items = trends.fetch_trending(category=cfg["news_category"], limit=20)
    if not items:
        sys.exit("error: no trending items returned")
    item = items[topic_index]
    print(f"      Topic: {item['title']}")

    print(f"[2/7] Writing {cfg['script_words']}-word script...")
    script_text = script.write_script(client, model, item["title"], item["summary"], cfg["script_words"])
    print(f"      {len(script_text.split())} words generated.")

    print(f"[3/7] Picking visual keywords...")
    keywords = script.script_to_keywords(client, model, script_text, n=cfg["clip_count"])
    print(f"      {keywords}")

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    workdir = Path("tmp") / stamp
    workdir.mkdir(parents=True, exist_ok=True)
    outdir = Path("output")
    outdir.mkdir(exist_ok=True)

    print(f"[4/7] Downloading Pexels footage...")
    footage_paths = []
    for i, kw in enumerate(keywords):
        path = workdir / f"clip_{i}.mp4"
        try:
            footage.fetch_video(kw, str(path), pexels_key)
            footage_paths.append(str(path))
            print(f"      [{i+1}/{len(keywords)}] {kw} -> ok")
        except Exception as e:
            print(f"      [{i+1}/{len(keywords)}] {kw} -> skip ({e})")
    if not footage_paths:
        sys.exit("error: no footage downloaded")

    print(f"[5/7] Generating TTS narration ({cfg['voice']})...")
    audio_path = workdir / "narration.mp3"
    boundaries = await tts.synthesize(script_text, str(audio_path), voice=cfg["voice"])
    print(f"      {len(boundaries)} word boundaries captured.")

    print(f"[6/7] Building burned captions...")
    srt_path = workdir / "captions.srt"
    srt_path.write_text(captions.srt_from_boundaries(boundaries, cfg["words_per_caption"]))

    print(f"[7/7] Assembling video with ffmpeg...")
    slug = slugify(item["title"])
    out_path = outdir / f"{stamp}_{slug}.mp4"
    assemble.assemble(footage_paths, str(audio_path), str(srt_path),
                      str(out_path), str(workdir))

    print(f"\nGenerating upload metadata...")
    meta = script.youtube_metadata(client, model, item["title"], script_text, item["link"])
    meta_path = outdir / f"{stamp}_{slug}.json"
    meta_path.write_text(json.dumps(meta, indent=2))

    print(f"\nVideo:    {out_path}")
    print(f"Metadata: {meta_path}")
    print(f"\nSuggested title: {meta.get('title','')}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--topic", type=int, default=0,
                   help="Index into trending list (0 = top story)")
    args = p.parse_args()
    cfg = yaml.safe_load(open(args.config))
    asyncio.run(run(cfg, args.topic))


if __name__ == "__main__":
    main()
