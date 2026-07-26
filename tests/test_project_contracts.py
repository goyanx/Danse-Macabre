import re
import struct
import sys
import unittest
import wave
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "game"
PYTHON_PACKAGES = GAME / "python-packages"
if str(PYTHON_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGES))

import storydm


def png_dimensions(path):
    with path.open("rb") as image:
        header = image.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("{} is not a valid PNG header.".format(path))
    return struct.unpack(">II", header[16:24])


def png_color_type(path):
    with path.open("rb") as image:
        header = image.read(26)
    if len(header) < 26 or header[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("{} is not a valid PNG header.".format(path))
    return header[25]


def relative_luminance(hex_color):
    channels = [int(hex_color[index:index + 2], 16) / 255.0 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first, second):
    lighter, darker = sorted(
        (relative_luminance(first), relative_luminance(second)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


class StoryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.story_source = (GAME / "facade_story.rpy").read_text(encoding="utf-8")
        cls.labels = set(
            re.findall(r"^label\s+([A-Za-z0-9_]+)", cls.story_source, re.MULTILINE)
        )

    def test_every_beat_callback_label_exists(self):
        callbacks = {
            beat["callback"]
            for act in storydm.ACTS
            for beat in act["beats"]
            if beat.get("callback")
        }
        self.assertEqual(callbacks - self.labels, set())

    def test_every_beat_location_has_room_and_loop_labels(self):
        locations = {beat["location"] for act in storydm.ACTS for beat in act["beats"]}

        for location in locations:
            with self.subTest(location=location):
                self.assertIn("facade_" + location, self.labels)
                self.assertIn("facade_room_loop_" + location, self.labels)

    def test_audio_references_exist(self):
        rpy_source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in GAME.glob("*.rpy")
        )
        references = set(
            re.findall(r'"(audio/[^"]+\.(?:mp3|ogg|wav))"', rpy_source, re.IGNORECASE)
        )

        self.assertTrue(references)
        for reference in references:
            with self.subTest(reference=reference):
                path = GAME / Path(reference)
                self.assertTrue(path.is_file(), "Missing audio asset: {}".format(reference))
                self.assertGreater(path.stat().st_size, 1024)

    def test_active_backgrounds_are_native_resolution(self):
        locations = {"street", "entrance", "map"}
        locations.update(beat["location"] for act in storydm.ACTS for beat in act["beats"])

        for location in locations:
            path = GAME / "images" / "bg facade {}.png".format(location)
            with self.subTest(location=location):
                self.assertTrue(path.is_file())
                self.assertEqual(png_dimensions(path), (1920, 1080))

    def test_character_expression_assets_exist(self):
        required = {
            "lila normal.png",
            "lila angry.png",
            "lila wounded.png",
            "malcolm normal.png",
            "malcolm amused.png",
            "malcolm wounded.png",
        }

        for filename in required:
            path = GAME / "images" / filename
            with self.subTest(filename=filename):
                self.assertTrue(path.is_file())
                self.assertEqual(png_dimensions(path), (620, 1080))

    def test_map_and_journal_icons_are_transparent_native_assets(self):
        required = {
            "icon journal.png",
            "icon journal hovered.png",
            "icon map.png",
            "icon map hovered.png",
        }

        for filename in required:
            path = GAME / "images" / filename
            with self.subTest(filename=filename):
                self.assertTrue(path.is_file())
                self.assertEqual(png_dimensions(path), (800, 800))
                self.assertEqual(png_color_type(path), 6)

    def test_ai_authoring_guide_is_discoverable(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        guide = ROOT / "docs" / "ai_story_authoring_guide.md"

        self.assertTrue(guide.is_file())
        self.assertIn("docs/ai_story_authoring_guide.md", readme)

    def test_choice_text_is_readable_without_hover(self):
        gui_source = (GAME / "gui.rpy").read_text(encoding="utf-8")
        screen_source = (GAME / "screens.rpy").read_text(encoding="utf-8")
        idle_text = re.search(
            r'gui\.choice_button_text_idle_color\s*=\s*"(#[0-9a-fA-F]{6})"',
            gui_source,
        )
        idle_background = re.search(
            r'background Solid\("(#[0-9a-fA-F]{6})[0-9a-fA-F]{0,2}"\)',
            screen_source,
        )

        self.assertIsNotNone(idle_text)
        self.assertIsNotNone(idle_background)
        self.assertGreaterEqual(
            contrast_ratio(idle_text.group(1), idle_background.group(1)),
            4.5,
        )

    def test_map_always_lists_every_playable_room(self):
        for room in ("Salon", "Kitchen", "Study"):
            with self.subTest(room=room):
                self.assertIn('"{} (available)"'.format(room), self.story_source)

        self.assertIn('"Kitchen (locked -', self.story_source)
        self.assertIn('"Study (locked -', self.story_source)
        self.assertIn("$ facade_sync_location_access()", self.story_source)

    def test_ending_returns_directly_to_main_menu(self):
        ending = re.search(
            r"^label facade_ending:\s*(.*?)(?=^label |\Z)",
            self.story_source,
            re.MULTILINE | re.DOTALL,
        )

        self.assertIsNotNone(ending)
        self.assertIn('\"END OF THE GLASS HOUSE\"', ending.group(1))
        self.assertIn("MainMenu(confirm=False, save=False)()", ending.group(1))
        self.assertNotRegex(ending.group(1), r"(?m)^\s+return\s*$")


class TTSContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tts_source = (GAME / "tts_elevenlabs.rpy").read_text(encoding="utf-8")
        cls.story_source = (GAME / "facade_story.rpy").read_text(encoding="utf-8")

    def test_characters_declare_tts_speakers(self):
        for speaker in ("director", "lila", "malcolm"):
            self.assertIn('cb_speaker="{}"'.format(speaker), self.story_source)

    def test_callback_uses_prefix_stripped_speaker_argument(self):
        self.assertRegex(
            self.tts_source,
            r"def tts_character_callback\([^)]*\bspeaker=None",
        )
        self.assertNotIn("cb_speaker=None", self.tts_source)

    def test_generated_voice_has_dedicated_voice_mixer_channel(self):
        self.assertRegex(
            self.tts_source,
            r'register_channel\(\s*"generated_voice",\s*mixer="voice"',
        )
        self.assertIn('channel="generated_voice"', self.tts_source)
        self.assertNotRegex(
            self.tts_source,
            r"renpy\.music\.(?:play|stop)\([^)]*channel=\"voice\"",
        )

    def test_external_cache_uses_audio_data(self):
        self.assertIn("renpy.audio.audio.AudioData", self.tts_source)

    def test_transient_tts_state_is_excluded_from_saves(self):
        self.assertIn("class _TTSRuntime(NoRollback):", self.tts_source)
        for field in (
            "jobs_lock",
            "kokoro_process",
            "kokoro_process_lock",
        ):
            self.assertIn("_tts_runtime.{}".format(field), self.tts_source)

    def test_voice_initialization_fixture_is_valid_spoken_audio(self):
        fixture = ROOT / "tests" / "fixtures" / "director_voice_smoke.wav"

        self.assertTrue(fixture.is_file())
        with wave.open(str(fixture), "rb") as audio:
            self.assertEqual(audio.getnchannels(), 1)
            self.assertEqual(audio.getsampwidth(), 2)
            self.assertEqual(audio.getframerate(), 24000)
            self.assertGreater(audio.getnframes(), 24000)

    def test_voice_initialization_test_uses_production_playback_path(self):
        testcase_source = (GAME / "testcases.rpy").read_text(encoding="utf-8")

        self.assertIn("testcase voice_initialization:", testcase_source)
        self.assertIn("_tts_play_if_current(key, fixture)", testcase_source)
        self.assertIn(
            'renpy.music.is_playing(channel="generated_voice")',
            testcase_source,
        )
        self.assertIn("_tts_runtime.kokoro_process =", testcase_source)
        self.assertIn("renpy.save(slot", testcase_source)


class RepositoryHygieneTests(unittest.TestCase):
    def test_no_credential_like_values_in_project_text(self):
        key_pattern = re.compile(r"sk_[A-Za-z0-9_-]{20,}")
        extensions = {".md", ".py", ".rpy", ".json", ".yml", ".yaml", ".txt"}
        violations = []

        for path in ROOT.rglob("*"):
            if ".git" in path.parts or path.suffix.lower() not in extensions:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if key_pattern.search(text):
                violations.append(str(path.relative_to(ROOT)))

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
