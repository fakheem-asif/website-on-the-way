# shorts-workflow

Automated YouTube Shorts generator — news/trends recap format.

Pulls a trending headline from Google News, writes a ~45-second narration with GPT,
generates a Microsoft Neural TTS voiceover with word-level timing, downloads matching
vertical stock clips from Pexels, and assembles a 1080×1920 MP4 with burned TikTok-style
captions. Outputs the video plus an upload-metadata JSON (title, description, tags).

You upload manually.

## Honest expectations

This tool generates videos. It does not generate money.

Reality check on the "$1000/week" goal:
- YouTube Partner Program requires 1000 subs + 10M Shorts views in 90 days (or
  4000 watch hours on long-form). Shorts RPM is typically **$0.02–$0.10 per 1000 views**.
- $1000/week from Shorts alone realistically needs ~10–50M views/week, sustained.
- Faceless news-recap channels are an extremely crowded niche. Many AI-generated
  channels get demonetized or hit with "reused content" / "spam, deceptive practices"
  strikes. Read [YouTube's spam policy](https://support.google.com/youtube/answer/2801973).
- The path to real revenue is sponsorships, affiliate links in descriptions, or
  driving traffic to your own product — not ad revenue. This tool gives you the
  asset pipeline; monetization is on you.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install ffmpeg (must include `ffprobe`):

```bash
# macOS
brew install ffmpeg
# Ubuntu/Debian
sudo apt install ffmpeg
```

Create `.env` from `.env.example`:

```bash
cp .env.example .env
# Get keys:
#   OPENAI_API_KEY: https://platform.openai.com/api-keys
#   PEXELS_API_KEY: https://www.pexels.com/api/new/
```

## Run

```bash
python main.py                  # top trending story
python main.py --topic 3        # 4th story in the list
```

Output lands in `output/`:
- `YYYYMMDD_HHMMSS_<slug>.mp4` — vertical 1080×1920 video
- `YYYYMMDD_HHMMSS_<slug>.json` — suggested title, description, tags

## Configuration

Edit `config.yaml`:

| Key                  | Default              | Notes                                                      |
| -------------------- | -------------------- | ---------------------------------------------------------- |
| `news_category`      | `TECHNOLOGY`         | `WORLD`, `BUSINESS`, `SCIENCE`, `SPORTS`, `HEALTH`, etc.   |
| `script_words`       | `110`                | ≈45s at 150wpm. Shorts cap at 60s.                         |
| `clip_count`         | `5`                  | Number of stock clips to fetch                             |
| `voice`              | `en-US-GuyNeural`    | Any [edge-tts voice](https://github.com/rany2/edge-tts)    |
| `words_per_caption`  | `3`                  | Lower = more TikTok-style                                  |
| `model`              | `gpt-4o-mini`        | OpenAI model for script + metadata                         |

## Per-video cost

- OpenAI (gpt-4o-mini, script + keywords + metadata): ~$0.001
- edge-tts: free
- Pexels: free
- **Total: ≈$0.001 per video**

## Daily batch

To generate the top 5 stories at once:

```bash
for i in 0 1 2 3 4; do python main.py --topic $i; done
```

## Project layout

```
shorts-workflow/
├── main.py          # orchestrator
├── trends.py        # Google News RSS
├── script.py        # GPT script + keywords + YT metadata
├── tts.py           # edge-tts narration + word timings
├── footage.py       # Pexels vertical stock video
├── captions.py      # SRT from word timings
├── assemble.py      # ffmpeg: normalize → concat → burn subs → mux
├── config.yaml
├── .env             # (gitignored) API keys
└── output/          # generated MP4s + metadata JSONs
```

## Known limits

- Pexels won't have footage for every niche topic — fallback keywords kick in
  when the LLM returns junk, but very obscure stories will give generic clips.
- edge-tts is reverse-engineered Microsoft Edge — Microsoft can throttle or
  break it any time. If TTS fails, swap to OpenAI's `tts-1` (~$0.015/1k chars).
- News-headline scripts can be repetitive across days. Vary `news_category`
  or write a custom prompt in `script.py` for a more distinctive voice.
- No background music. Add `-stream_loop -1 -i music.mp3` and an `amix` filter
  in `assemble.py` if you want it (mind copyright).
