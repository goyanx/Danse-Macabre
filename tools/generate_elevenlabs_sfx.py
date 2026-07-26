import os
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
SFX_DIR = ROOT / "game" / "audio" / "sfx"
ENDPOINT = "https://api.elevenlabs.io/v1/sound-generation"


SFX = [
    {
        "file": "townhouse_door_chime.mp3",
        "text": "A refined modern townhouse door chime at night, soft brass tone, subtle room reverb, no voices.",
        "duration_seconds": 2,
    },
    {
        "file": "crystal_glass_tension.mp3",
        "text": "A delicate crystal glass set down too firmly, a tiny resonant crack, tense silence after, no voices.",
        "duration_seconds": 3,
    },
    {
        "file": "distant_party_fade.mp3",
        "text": "A distant upscale apartment party fading behind a closing door, muffled footsteps and glasses, no speech or identifiable voices.",
        "duration_seconds": 6,
    },
    {
        "file": "study_drawer_click.mp3",
        "text": "An old wooden desk drawer opening with a careful click, paper sliding against wood, intimate suspense, no voices.",
        "duration_seconds": 3,
    },
]


def generate(effect):
    api_key = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("XI_API_KEY")
    if not api_key:
        raise RuntimeError("Set ELEVENLABS_API_KEY or XI_API_KEY to generate sound effects.")

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }
    payload = {
        "text": effect["text"],
        "duration_seconds": effect["duration_seconds"],
        "prompt_influence": 0.45,
    }

    response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=90)
    response.raise_for_status()

    out = SFX_DIR / effect["file"]
    out.write_bytes(response.content)
    print(out)


def main():
    SFX_DIR.mkdir(parents=True, exist_ok=True)
    for effect in SFX:
        generate(effect)


if __name__ == "__main__":
    main()
