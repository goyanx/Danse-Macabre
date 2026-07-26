import argparse
import json
from pathlib import Path
import sys


def generate_audio(pipeline, sf, text, out_path, voice, speed):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    generator = pipeline(text, voice=voice, speed=speed)

    with sf.SoundFile(str(out), mode="w", samplerate=24000, channels=1) as audio_file:
        for _, _, audio in generator:
            audio_file.write(audio)

    return out


def run_server(KPipeline, sf, lang_code):
    pipeline = KPipeline(lang_code=lang_code)
    for raw_line in sys.stdin:
        try:
            request = json.loads(raw_line)
            out = generate_audio(
                pipeline,
                sf,
                request["text"],
                request["out"],
                request.get("voice", "af_heart"),
                float(request.get("speed", 1.0)),
            )
            response = {"ok": True, "out": str(out)}
        except Exception as exc:
            response = {"ok": False, "error": str(exc)}
        print("__KOKORO_RESULT__" + json.dumps(response), flush=True)


def main():
    parser = argparse.ArgumentParser(description="Generate Kokoro TTS WAV files.")
    parser.add_argument("--text")
    parser.add_argument("--out")
    parser.add_argument("--voice", default="af_heart")
    parser.add_argument("--lang-code", default="a")
    parser.add_argument("--speed", type=float, default=1.0)
    parser.add_argument("--server", action="store_true")
    args = parser.parse_args()

    try:
        from kokoro import KPipeline
        import soundfile as sf
    except Exception as exc:
        raise SystemExit(
            "Kokoro is not installed in this Python environment. Install it with: "
            "python -m pip install kokoro soundfile. Original error: {}".format(exc)
        )

    if args.server:
        run_server(KPipeline, sf, args.lang_code)
        return

    if not args.text or not args.out:
        parser.error("--text and --out are required unless --server is used")

    pipeline = KPipeline(lang_code=args.lang_code)
    out = generate_audio(pipeline, sf, args.text, args.out, args.voice, args.speed)
    print(out)


if __name__ == "__main__":
    main()
