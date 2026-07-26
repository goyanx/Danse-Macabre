import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
if str(PYTHON_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGES))

import storydm


def iter_beats():
    for act_index, act in enumerate(storydm.ACTS):
        for beat_index, beat in enumerate(act["beats"]):
            yield act_index, beat_index, act, beat


class StorySchemaTests(unittest.TestCase):
    def test_act_and_beat_ids_are_unique(self):
        act_ids = [act["id"] for act in storydm.ACTS]
        beat_ids = [beat["id"] for _, _, _, beat in iter_beats()]

        self.assertEqual(len(act_ids), len(set(act_ids)))
        self.assertEqual(len(beat_ids), len(set(beat_ids)))

    def test_every_beat_has_required_fields(self):
        required = {"id", "title", "location", "triggers", "callback", "journal", "nudge"}

        for _, _, act, beat in iter_beats():
            with self.subTest(act=act["id"], beat=beat["id"]):
                self.assertTrue(required.issubset(beat))
                self.assertRegex(beat["id"], r"^[a-z][a-z0-9_]*$")
                self.assertTrue(beat["triggers"])
                self.assertTrue(all(trigger == trigger.lower() for trigger in beat["triggers"]))
                self.assertTrue(all(trigger.strip() for trigger in beat["triggers"]))
                self.assertTrue(beat["callback"].startswith("facade_"))
                self.assertTrue(beat["journal"].strip())
                self.assertTrue(beat["nudge"].strip())

    def test_outline_does_not_reveal_future_story(self):
        outline = storydm.StoryDM().outline().lower()

        self.assertIn("act i", outline)
        self.assertNotIn("act ii", outline)
        self.assertNotIn("vivian", outline)
        self.assertNotIn("daughter", outline)
        self.assertNotIn("best lie", outline)


class StoryProgressionTests(unittest.TestCase):
    def test_primary_trigger_completes_every_beat_in_order(self):
        dm = storydm.StoryDM()
        expected_callbacks = []

        for _, _, _, beat in iter_beats():
            expected_callbacks.append(beat["callback"])
            result = dm.register_player_input(beat["triggers"][0], beat["location"])

            with self.subTest(beat=beat["id"]):
                self.assertTrue(result["progressed"])
                self.assertEqual(result["callback"], beat["callback"])
                self.assertEqual(result["journal"], beat["journal"])

        self.assertEqual(dm.progress_log, [beat["id"] for _, _, _, beat in iter_beats()])
        self.assertEqual(len(expected_callbacks), 11)

    def test_wrong_room_does_not_advance_current_beat(self):
        dm = storydm.StoryDM()
        result = dm.register_player_input("hello", "kitchen")

        self.assertFalse(result["progressed"])
        self.assertEqual(dm.current_beat()["id"], "greet_the_hosts")

    def test_nudge_appears_after_three_failed_turns(self):
        dm = storydm.StoryDM()

        first = dm.register_player_input("look around", "salon")
        second = dm.register_player_input("listen", "salon")
        third = dm.register_player_input("wait", "salon")

        self.assertEqual(first["nudge"], "")
        self.assertEqual(second["nudge"], "")
        self.assertEqual(third["nudge"], dm.current_beat()["nudge"])
        self.assertTrue(third["problem"])

    def test_progress_resets_stall_tracking(self):
        dm = storydm.StoryDM()
        dm.register_player_input("look around", "salon")
        dm.register_player_input("listen", "salon")

        result = dm.register_player_input("hello", "salon")

        self.assertTrue(result["progressed"])
        self.assertEqual(dm.turns_since_progress, 0)
        self.assertEqual(dm.recent_inputs, [])

    def test_every_beat_has_an_authored_choice_that_advances_it(self):
        story_source = (ROOT / "game" / "facade_story.rpy").read_text(encoding="utf-8")
        choice_pattern = re.compile(
            r'if facade_beat_id == "([^"]+)" and location == "([^"]+)":\s*'
            r'\$ user_input = "([^"]+)"'
        )
        choices = {}
        for beat_id, location, player_input in choice_pattern.findall(story_source):
            choices.setdefault(beat_id, []).append((location, player_input))

        for act_index, beat_index, _, beat in iter_beats():
            with self.subTest(beat=beat["id"]):
                self.assertIn(beat["id"], choices)
                matched = False
                for location, player_input in choices[beat["id"]]:
                    dm = storydm.StoryDM()
                    dm.act_index = act_index
                    dm.beat_index = beat_index
                    result = dm.register_player_input(player_input, location)
                    matched = matched or result["progressed"]
                self.assertTrue(matched, "No authored choice advances this beat.")


if __name__ == "__main__":
    unittest.main()
