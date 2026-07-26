import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def run(command):
    print("+", " ".join(str(part) for part in command), flush=True)
    return subprocess.run(command, cwd=ROOT, check=False).returncode


def find_renpy(explicit_path):
    candidates = [
        explicit_path,
        os.environ.get("RENPY_EXE"),
        r"D:\renpy_installer\renpy-8.3.7-sdk\renpy.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return Path(candidate)
    return None


def main():
    parser = argparse.ArgumentParser(description="Run The Glass House regression suite.")
    parser.add_argument(
        "--skip-unit",
        action="store_true",
        help="Skip the offline Python tests.",
    )
    parser.add_argument(
        "--voice-init",
        action="store_true",
        help="Boot Ren'Py and verify initialized generated-voice playback.",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run Ren'Py lint after the offline Python tests.",
    )
    parser.add_argument(
        "--renpy-exe",
        help="Path to renpy.exe. RENPY_EXE is used when omitted.",
    )
    args = parser.parse_args()

    if not args.skip_unit:
        status = run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                "tests",
                "-v",
            ]
        )
        if status:
            return status

    if args.voice_init or args.lint:
        renpy_exe = find_renpy(args.renpy_exe)
        if renpy_exe is None:
            print("A Ren'Py check was requested, but renpy.exe was not found.", file=sys.stderr)
            return 2

        if args.voice_init:
            status = run(
                [str(renpy_exe), str(ROOT), "test", "voice_initialization"]
            )
            if status:
                return status

        if args.lint:
            return run([str(renpy_exe), str(ROOT), "lint"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
