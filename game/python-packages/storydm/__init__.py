__version__ = "0.1.0"

import re


LOCATION_UNLOCK_BEATS = {
    "kitchen": "find_the_third_glass",
    "study": "press_the_absent_guest",
}


ACTS = [
    {
        "id": "act1_arrival",
        "title": "Act I - Arrival at the Glass House",
        "summary": (
            "The player arrives after a party at Lila and Malcolm Vale's townhouse. "
            "Everything is polished, but the room keeps betraying the marriage."
        ),
        "beats": [
            {
                "id": "greet_the_hosts",
                "title": "The practiced welcome",
                "location": "salon",
                "triggers": ["hello", "hi", "greet", "arrive", "thank", "party", "evening"],
                "callback": "facade_beat_greeted",
                "journal": "Lila and Malcolm perform hospitality like a rehearsed scene.",
                "nudge": "The room is waiting for you to break the politeness. Say hello, accept the drink, or ask why the invitation came so late.",
            },
            {
                "id": "notice_the_crack",
                "title": "The flaw in the display",
                "location": "salon",
                "triggers": ["portrait", "photo", "wedding picture", "crack", "mantel", "mantle", "damaged frame"],
                "callback": "facade_beat_crack",
                "journal": "The wedding portrait has a hairline crack through Lila's smile.",
                "nudge": "Something visible in the salon does not fit the polished welcome. Look at the portrait, glasses, or mantel.",
            },
            {
                "id": "question_the_toast",
                "title": "The toast that names the ghost",
                "location": "salon",
                "triggers": ["toast", "celebrating", "celebration", "anniversary", "vivian", "missing guest", "why tonight"],
                "callback": "facade_to_act2",
                "journal": "Malcolm nearly toasted Vivian, then pretended he had not said the name.",
                "nudge": "The toast is the first loose thread. Ask what they are celebrating, or what name Malcolm nearly said.",
            },
        ],
    },
    {
        "id": "act2_polite_war",
        "title": "Act II - The Polite War",
        "summary": (
            "The hosts recruit the player as audience, judge, and shield. The player must make the fighting specific enough to reveal a third place setting."
        ),
        "beats": [
            {
                "id": "name_the_performance",
                "title": "The marriage as theatre",
                "location": "salon",
                "triggers": ["acting", "performance", "script", "play", "theatre", "theater", "pretend", "show"],
                "callback": "facade_beat_performance",
                "journal": "Their arguments sound rehearsed, as if tonight has been staged before.",
                "nudge": "Listen to how polished the insults are. Ask whether this fight is new or rehearsed.",
            },
            {
                "id": "find_the_third_glass",
                "title": "A place set for absence",
                "location": "salon",
                "triggers": ["third glass", "extra glass", "bar", "counter", "kitchen", "place setting", "three glasses"],
                "callback": "facade_unlock_kitchen",
                "journal": "There is a third glass, clean and waiting, though only two hosts are present.",
                "nudge": "The bar is set for someone who is not in the room. Inspect the glasses or move toward the kitchen.",
            },
            {
                "id": "press_the_absent_guest",
                "title": "Vivian becomes unavoidable",
                "location": "kitchen",
                "triggers": ["vivian", "daughter", "child", "guest", "invited", "absent", "empty chair", "where is she", "prepared for", "untouched glass", "third glass"],
                "callback": "facade_to_act3",
                "journal": "Vivian is spoken of as a person, a memory, and a weapon.",
                "nudge": "The kitchen has the evidence of preparation. Ask who the third glass was meant for.",
            },
        ],
    },
    {
        "id": "act3_missing_guest",
        "title": "Act III - The Missing Guest",
        "summary": (
            "The player finds the private script behind the public fight. The DM watches for confusion and points the player toward the study."
        ),
        "beats": [
            {
                "id": "enter_the_study",
                "title": "The locked room opens",
                "location": "study",
                "triggers": ["study", "desk", "letter", "drawer", "cream paper", "manuscript"],
                "callback": "facade_beat_letter",
                "journal": "A letter in the study describes Vivian as 'our best lie'.",
                "nudge": "The argument keeps circling a private room. Go to the study and look for paper, letters, or a drawer.",
            },
            {
                "id": "confront_the_lie",
                "title": "The invented daughter",
                "location": "study",
                "triggers": ["lie", "fiction", "invented", "imaginary", "not real", "best lie", "no daughter", "truth"],
                "callback": "facade_beat_confrontation",
                "journal": "Vivian may be the fiction that has held the marriage together.",
                "nudge": "The letter does not ask you to solve a disappearance. It asks you to name a lie.",
            },
            {
                "id": "choose_the_break",
                "title": "Break the game or preserve it",
                "location": "study",
                "triggers": ["apologize", "truth", "leave", "stop", "enough", "separate", "stay", "forgive"],
                "callback": "facade_to_act4",
                "journal": "The couple cannot continue the performance unless the player chooses how to answer it.",
                "nudge": "They are waiting for a human response now: tell them to stop, tell the truth, leave, or ask them what they still want.",
            },
        ],
    },
    {
        "id": "act4_after_midnight",
        "title": "Act IV - After Midnight",
        "summary": (
            "The confrontation resolves into quiet. The player can leave the house changed, or sit with what the couple cannot yet say."
        ),
        "beats": [
            {
                "id": "name_the_room",
                "title": "The room with no child",
                "location": "study",
                "triggers": ["nursery", "room", "vivian", "child", "empty", "door", "bedroom"],
                "callback": "facade_beat_empty_room",
                "journal": "The untouched room is not a crime scene. It is a shrine to an invented witness.",
                "nudge": "One last place has been protected by euphemism. Ask about Vivian's room, or the door they never open.",
            },
            {
                "id": "quiet_exit",
                "title": "The final silence",
                "location": "study",
                "triggers": ["leave", "goodbye", "sit", "silence", "wait", "door", "home", "end"],
                "callback": "facade_ending",
                "journal": "The performance ends because nobody has the strength to restart it.",
                "nudge": "There is nothing left to interrogate. Leave, sit quietly, or say goodbye.",
            },
        ],
    },
]


class StoryDM:
    def __init__(self, acts=None):
        self.acts = acts or ACTS
        self.act_index = 0
        self.beat_index = 0
        self.turns_since_progress = 0
        self.progress_log = []
        self.recent_inputs = []
        self.last_location = "salon"

    def current_act(self):
        return self.acts[self.act_index]

    def current_beat(self):
        return self.current_act()["beats"][self.beat_index]

    def available_locations(self):
        completed = set(self.progress_log)
        locations = {"salon"}
        for location, beat_id in LOCATION_UNLOCK_BEATS.items():
            if beat_id in completed:
                locations.add(location)
        return locations

    def outline(self):
        return "\n".join([
            self.current_act()["title"],
            "Observe the room, listen closely, and decide when politeness stops being useful.",
            "Future acts remain hidden until you reach them.",
        ])

    def register_player_input(self, text, location):
        self.last_location = location
        normalized = self._normalize(text)
        beat = self.current_beat()
        self.turns_since_progress += 1
        if normalized:
            self.recent_inputs.append({"text": normalized, "location": location, "beat": beat["id"]})
            self.recent_inputs = self.recent_inputs[-6:]

        if self._matches(beat, normalized, location):
            return self._progress(beat)

        return {
            "progressed": False,
            "callback": None,
            "beat": beat,
            "problem": self.problem_state(),
            "nudge": self.nudge(text),
        }

    def nudge(self, player_text=""):
        beat = self.current_beat()
        if self.turns_since_progress < 3:
            return ""

        return self.forced_nudge(player_text)

    def forced_nudge(self, player_text="", use_ollama=False):
        beat = self.current_beat()
        expected_location = beat.get("location")
        if expected_location and self.last_location != expected_location:
            return "The thread is tugging away from this room. Use the map and return to the {}.".format(expected_location)

        ollama_line = self._ollama_nudge(beat, player_text) if use_ollama else ""
        return ollama_line or beat["nudge"]

    def nudge_messages(self, player_text=""):
        beat = self.current_beat()
        return [
            {
                "role": "system",
                "content": (
                    "You are the invisible director of an interactive domestic mystery. "
                    "Give one subtle in-world nudge, under 22 words. Do not reveal the solution."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Current act: {act}\nCurrent beat: {beat}\nNeeded action: {nudge}\n"
                    "Recent player attempts: {recent}\nPlayer just typed: {player_text}"
                ).format(
                    act=self.current_act()["title"],
                    beat=beat["title"],
                    nudge=beat["nudge"],
                    recent=self.recent_inputs,
                    player_text=player_text,
                ),
            },
        ]

    def problem_state(self):
        return self.turns_since_progress >= 3

    def _progress(self, beat):
        self.turns_since_progress = 0
        self.recent_inputs = []
        self.progress_log.append(beat["id"])
        result = {
            "progressed": True,
            "callback": beat["callback"],
            "beat": beat,
            "problem": False,
            "journal": beat.get("journal", ""),
            "nudge": "",
        }

        self.beat_index += 1
        if self.beat_index >= len(self.current_act()["beats"]):
            self.beat_index = 0
            if self.act_index < len(self.acts) - 1:
                self.act_index += 1

        return result

    def _matches(self, beat, normalized_text, location):
        if beat.get("location") and beat["location"] != location:
            location_words = [beat["location"]]
            if not any(word in normalized_text for word in location_words):
                return False

        return any(trigger in normalized_text for trigger in beat.get("triggers", []))

    def _ollama_nudge(self, beat, player_text):
        try:
            import chatgpt

            response = chatgpt.completion(self.nudge_messages(player_text))[-1].get("content", "")
            response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE).strip()
            response = re.sub(r"\s+", " ", response)
            if response and "[AI" not in response:
                return response[:180]
        except Exception:
            pass
        return ""

    @staticmethod
    def _normalize(text):
        return re.sub(r"\s+", " ", (text or "").lower()).strip()
