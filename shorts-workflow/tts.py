import edge_tts


async def synthesize(text: str, audio_path: str, voice: str = "en-US-GuyNeural"):
    """Generate MP3 narration and return word-level timing boundaries."""
    communicate = edge_tts.Communicate(text, voice)
    boundaries = []
    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                boundaries.append({
                    "start": chunk["offset"] / 10_000_000,
                    "duration": chunk["duration"] / 10_000_000,
                    "text": chunk["text"],
                })
    return boundaries
