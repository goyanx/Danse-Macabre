import pickle
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON_PACKAGES = ROOT / "game" / "python-packages"
if str(PYTHON_PACKAGES) not in sys.path:
    sys.path.insert(0, str(PYTHON_PACKAGES))

import extraact


class ExtraActStateTests(unittest.TestCase):
    def make_date_state(self):
        state = extraact.ExtraActState()
        result = state.register_turn(
            "I came back because I wanted to see you. Would you have a drink with me? "
            "No pressure; it is your choice."
        )
        self.assertEqual(result["event"], "date_accepted")
        self.assertTrue(state.choose_date("jazz_lounge"))
        return state

    def test_respectful_invitation_unlocks_date_selection(self):
        state = extraact.ExtraActState()

        result = state.register_turn(
            "You look beautiful. Would you go out for a drink with me? No pressure."
        )

        self.assertEqual(result["event"], "date_accepted")
        self.assertEqual(state.stage, "choose_date")
        self.assertGreaterEqual(state.respect, 2)
        self.assertGreaterEqual(state.attraction, 1)

    def test_pressure_blocks_the_date(self):
        state = extraact.ExtraActState()

        result = state.register_turn("You owe me a date and you have to come with me.")

        self.assertEqual(result["event"], "date_declined")
        self.assertEqual(state.stage, "invitation")
        self.assertEqual(state.boundary_violations, 1)

    def test_home_invitation_requires_connection(self):
        state = self.make_date_state()

        early = state.register_turn("Come home to my place now.")

        self.assertEqual(early["event"], "home_declined")
        self.assertEqual(state.stage, "date")

        state.register_turn("I want to be honest about why I came back.")
        state.register_turn("What do you want from tonight? I want to listen.")
        accepted = state.register_turn(
            "You are beautiful, and I enjoy your company. "
            "Would you continue the evening at my place? Your choice."
        )

        self.assertEqual(accepted["event"], "home_accepted")
        self.assertEqual(state.stage, "home")

    def test_bedroom_requires_trust_respect_and_time_at_home(self):
        state = self.make_date_state()
        state.register_turn("I want to be honest about how I feel.")
        state.register_turn("What would you like? I want to listen and understand.")
        state.register_turn(
            "You are stunning. Would you continue the evening at my place? No pressure."
        )
        self.assertEqual(state.stage, "home")

        state.register_turn("I am glad you came. Take your time and be comfortable.")
        state.register_turn("I care about you and want to understand what you want.")
        result = state.register_turn(
            "Would you like to be closer in the bedroom? Only if that is your choice."
        )

        self.assertEqual(result["event"], "bedroom_accepted")
        self.assertEqual(state.stage, "bedroom")

    def test_open_state_never_forces_an_ending(self):
        state = self.make_date_state()
        state.enter_open_state("apartment")

        for _ in range(20):
            result = state.register_turn("Tell me what you are thinking.")

        self.assertEqual(result["event"], "open_conversation")
        self.assertEqual(state.stage, "open")
        self.assertEqual(len(state.history), 12)

    def test_state_is_save_compatible(self):
        state = self.make_date_state()
        restored = pickle.loads(pickle.dumps(state))

        self.assertEqual(restored.stage, state.stage)
        self.assertEqual(restored.history, state.history)
        self.assertEqual(restored.mood_name(), state.mood_name())

    def test_moment_context_is_compact_and_serializable(self):
        state = self.make_date_state()
        state.register_turn("I want to listen and understand what you want tonight.")

        context = state.moment_context()
        restored = pickle.loads(pickle.dumps(context))

        self.assertEqual(restored["stage"], "date")
        self.assertEqual(restored["mood"], state.mood_name())
        self.assertIn("objective", restored)
        self.assertIn("readiness", restored)
        self.assertLessEqual(len(restored["recent_events"].split(", ")), 4)


if __name__ == "__main__":
    unittest.main()
