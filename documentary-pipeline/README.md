# Documentary Pipeline

A workflow that turns a politician (or any public figure) into a **long-form,
fact-based documentary video** — research → human review → script → voiceover →
visuals → a rendered `.mp4` — with sourcing and AI-disclosure built into the
machinery rather than bolted on.

It runs **end-to-end offline** out of the box: a static `ffmpeg` (via
`imageio-ffmpeg`) and Pillow are the only requirements, and the "stub" providers
render a real MP4 with no API keys. Swap in real providers (LLM, TTS, stock
B-roll) when you want voice and footage.

```
 research ──▶  REVIEW GATE  ──▶ script ──▶ voiceover ──▶ visuals ──▶ assemble ──▶ .mp4
 (cited        (human verifies   (every     (synthetic    (B-roll /   (concat +
  claims)       + approves)       line       narrator)     cards)      disclosure
                                  cited)                                + citations)
```

## Why it's built this way (the integrity model)

A documentary about a real person carries factual authority, and an automated
one is easy to misuse. Three controls are wired into the code — not optional
config:

1. **Claims must be cited.** A factual claim is only usable if it has ≥1
   real (non-placeholder) source. See `models.Claim.is_citable`.
2. **A human must verify and approve.** Nothing past research runs until a
   person marks each claim `verified` and approves the dossier. The gate
   (`stages/review.py`) refuses unapproved *and* placeholder-only dossiers — you
   cannot bypass it with `--approve-all` if the sources aren't real.
3. **AI use is always disclosed.** Assembly always burns in an `AI-ASSISTED`
   bug on every frame, a disclosure card, and a closing **Sources & Citations**
   crawl. A `manifest.json` records the provenance of every asset.

The research providers **never invent citations** — offline they emit labelled
placeholders; with an LLM they draft unsourced leads. Either way, a human has to
attach real sources. That's what keeps "strictly fact-based + cited" honest.

## Install

```bash
cd documentary-pipeline
pip install -r requirements.txt   # imageio-ffmpeg + pillow
```

## Quickstart — render the demo (fictional subject)

The demo uses a **wholly fictional** politician ("Jordan Rivera, former mayor of
Lakeview") so you can see the full pipeline without making claims about anyone
real.

```bash
python -m pipeline demo --config config.example.json
# -> build/demo/documentary.mp4   (1080p, ~78s, 11 scenes)
#    build/demo/documentary.srt   (captions)
#    build/demo/manifest.json     (auditable provenance record)
#    build/demo/script.json       (the generated script)
```

## Real workflow — three steps, with the gate in the middle

### 1. Research → an *unverified* dossier
```bash
python -m pipeline research --subject "Jane Q. Public" --out build
# writes build/jane-q-public.dossier.json full of placeholder claims to fill in
```

### 2. Review gate — verify every claim, then approve
Edit the dossier so each claim is a real fact with a real source, then:
```bash
python -m pipeline review --dossier build/jane-q-public.dossier.json
#   interactive: for each claim, confirm it against its source (y/N), then approve
# writes build/jane-q-public.reviewed.json
```
(`--approve-all` exists for testing only and is refused when sources are
placeholders.)

### 3. Produce the video
```bash
python -m pipeline produce --dossier build/jane-q-public.reviewed.json --out build
```

`python -m pipeline run --subject "..."` chains these: it produces only if an
approved `*.reviewed.json` already exists, otherwise it stops at the gate.

## Providers (swap stub → real)

Select providers in the config `"providers"` block; supply keys via env vars.

| Capability | `stub` (default) | Real options | Env |
|-----------|------------------|--------------|-----|
| `research` | placeholder dossier | `llm` (drafts unsourced leads) | uses the `llm` provider |
| `llm` | narration from claim text | `anthropic`, `openai` | `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` |
| `tts` | silent, duration-matched | `elevenlabs`, `openai` | `ELEVENLABS_API_KEY` / `OPENAI_API_KEY` |
| `media` | styled cards | `pexels`, `wikimedia` | `PEXELS_API_KEY` (Wikimedia: none) |

```jsonc
// config.json
{ "providers": { "research": "stub", "llm": "anthropic", "tts": "elevenlabs", "media": "wikimedia" } }
```

Real TTS uses a **generic synthetic narrator** — the adapters deliberately do
**not** clone the subject's voice, and real `media` providers pull licensed /
public-domain footage with attribution recorded in the manifest. The real
adapters (`anthropic`/`openai`/`elevenlabs`/`pexels`/`wikimedia`) are wired but
untested offline; verify keys and quotas before a production run.

## Outputs

- `documentary.mp4` — H.264/AAC, 1920×1080 (configurable).
- `documentary.srt` — caption sidecar.
- `script.json` — scenes, narration, and `claim_ids` linking each line to its source.
- `manifest.json` — per-scene + per-asset provenance, AI flags, and a
  `disclosure` block confirming the bug, disclosure card, and citations are present.

## Configuration

See `config.example.json`. Highlights: `style` (resolution/fps/colours/`motion`
for Ken Burns), `words_per_second` + `min_scene_seconds` (pacing),
`title_template`/`subtitle`, and `disclosure` (wording only — the disclosure
itself is always rendered).

## Responsible use

This tool is for **honest, sourced** documentary work. Don't use it to fabricate
statements or events, impersonate a real person's voice or likeness, or pass AI
output off as authentic footage. Documentaries about real people can implicate
defamation and election laws — fact-check, keep the citations accurate, and
leave the disclosure intact. For non-factual treatments, set the framing to
satire/fiction and keep it clearly labelled.

## GitHub Actions

`.github/workflows/documentary.yml` is a manual-dispatch template (`demo` /
`research` / `produce`). GitHub only runs workflows from the repo root, so copy
it to the repository's root `.github/workflows/` to activate. There is no
automatic "video about a real person" path — `produce` runs only from a dossier
you've reviewed and committed.

## Extending

Add a provider by subclassing the relevant base in `pipeline/providers/base.py`
and registering it in `get_provider`. Each stage is a small module under
`pipeline/stages/` and hands off a plain-JSON artifact, so stages can be run and
inspected independently.
```
pipeline/
  cli.py · orchestrator.py · config.py · models.py
  stages/   research · review · script · voiceover · visuals · assemble
  providers/ research · llm · tts · media  (stub + real adapters)
  util/     ffmpeg · cards · text
```
