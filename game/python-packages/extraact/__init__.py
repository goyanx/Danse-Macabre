import re


RESPECT_PHRASES = (
    "your choice",
    "no pressure",
    "comfortable",
    "take your time",
    "what do you want",
    "what would you like",
    "listen",
    "understand",
    "respect",
)

HONESTY_PHRASES = (
    "honest",
    "truth",
    "came back",
    "wanted to see you",
    "care about you",
    "missed you",
    "feel",
)

WARMTH_PHRASES = (
    "kind",
    "laugh",
    "smile",
    "glad",
    "enjoy",
    "beautiful evening",
    "good company",
    "stay with you",
)

FLIRT_PHRASES = (
    "beautiful",
    "gorgeous",
    "stunning",
    "attractive",
    "kiss",
    "closer",
    "dance",
    "flirt",
)

INVITATION_PHRASES = (
    "date",
    "drink with me",
    "go out",
    "dinner",
    "jazz",
    "rooftop",
    "come with me",
)

HOME_PHRASES = (
    "my place",
    "my apartment",
    "come home",
    "continue the evening",
    "one more drink",
)

BEDROOM_PHRASES = (
    "bedroom",
    "come to bed",
    "stay the night",
    "more intimate",
    "be close",
)

PRESSURE_PHRASES = (
    "you owe me",
    "must come",
    "have to come",
    "do what i say",
    "get you drunk",
    "won't take no",
    "cannot say no",
    "can't say no",
)


class ExtraActState:
    def __init__(self):
        self.stage = "invitation"
        self.location = "townhouse"
        self.trust = 1
        self.respect = 1
        self.warmth = 0
        self.attraction = 0
        self.boundary_violations = 0
        self.date_turns = 0
        self.home_turns = 0
        self.total_turns = 0
        self.history = []

    def mood_name(self):
        score = (
            self.trust
            + self.respect
            + self.warmth
            + self.attraction
            - (self.boundary_violations * 3)
        )
        if score >= 12:
            return "close"
        if score >= 8:
            return "warm"
        if score >= 4:
            return "curious"
        return "guarded"

    def current_objective(self):
        if self.stage == "invitation":
            return "Invite Lila out without treating her answer as an obligation."
        if self.stage == "choose_date":
            return "Choose somewhere that gives both of you room to talk."
        if self.stage == "date":
            return "Build trust through honesty, attention, humor, and respect."
        if self.stage == "home":
            return "Let the quieter setting deepen the conversation without rushing her."
        if self.stage == "bedroom":
            return "Keep the intimacy mutual, private, and emotionally attentive."
        return "Stay present and let the relationship remain open-ended."

    def persona_summary(self):
        mood = self.mood_name()
        summaries = {
            "guarded": "Lila is elegant and alert, using wit to protect her independence.",
            "curious": "Lila is intrigued but watches whether the player listens as well as flirts.",
            "warm": "Lila is candid, playful, and willing to risk tenderness.",
            "close": "Lila is trusting, intimate, and direct while keeping clear boundaries.",
        }
        return summaries[mood]

    def moment_context(self):
        recent_events = [
            "{}:{}".format(entry.get("location", self.location), entry.get("event", "conversation"))
            for entry in self.history[-4:]
        ]
        readiness = "open"
        if self.stage == "date":
            readiness = "can_go_home" if self.can_go_home() else "needs_more_connection"
        elif self.stage == "home":
            readiness = "can_enter_bedroom" if self.can_enter_bedroom() else "needs_more_trust"

        return {
            "stage": self.stage,
            "location": self.location,
            "mood": self.mood_name(),
            "objective": self.current_objective(),
            "persona": self.persona_summary(),
            "recent_events": ", ".join(recent_events) or "none",
            "boundary_pressure": "yes" if self.boundary_violations else "no",
            "readiness": readiness,
        }

    def choose_date(self, location):
        if self.stage != "choose_date":
            return False
        if location not in ("jazz_lounge", "rooftop"):
            return False
        self.stage = "date"
        self.location = location
        return True

    def can_go_home(self):
        return (
            self.stage == "date"
            and self.date_turns >= 3
            and self.trust >= 3
            and self.respect >= 3
            and self.attraction >= 1
            and self.boundary_violations == 0
        )

    def can_enter_bedroom(self):
        return (
            self.stage == "home"
            and self.home_turns >= 2
            and self.trust >= 5
            and self.respect >= 4
            and self.attraction >= 2
            and self.boundary_violations == 0
        )

    def enter_open_state(self, location=None):
        self.stage = "open"
        if location:
            self.location = location

    def register_turn(self, text, location=None):
        normalized = self._normalize(text)
        if location:
            self.location = location

        before = {
            "trust": self.trust,
            "respect": self.respect,
            "warmth": self.warmth,
            "attraction": self.attraction,
        }
        event = "conversation"

        if self._contains(normalized, PRESSURE_PHRASES):
            self.boundary_violations += 1
            self.respect = max(-3, self.respect - 2)
            self.trust = max(-3, self.trust - 2)
            event = "boundary"
        else:
            if self._contains(normalized, RESPECT_PHRASES):
                self.respect = min(8, self.respect + 1)
                self.trust = min(8, self.trust + 1)
            if self._contains(normalized, HONESTY_PHRASES):
                self.trust = min(8, self.trust + 1)
            if self._contains(normalized, WARMTH_PHRASES):
                self.warmth = min(8, self.warmth + 1)
            if self._contains(normalized, FLIRT_PHRASES):
                self.attraction = min(8, self.attraction + 1)

        if self.stage == "invitation" and self._contains(normalized, INVITATION_PHRASES):
            if self.boundary_violations:
                event = "date_declined"
            else:
                self.stage = "choose_date"
                event = "date_accepted"

        elif self.stage == "date":
            self.date_turns += 1
            if self._contains(normalized, HOME_PHRASES):
                if self.can_go_home():
                    self.stage = "home"
                    self.location = "apartment"
                    event = "home_accepted"
                else:
                    event = "home_declined"

        elif self.stage == "home":
            self.home_turns += 1
            if self._contains(normalized, BEDROOM_PHRASES):
                if self.can_enter_bedroom():
                    self.stage = "bedroom"
                    self.location = "bedroom"
                    event = "bedroom_accepted"
                else:
                    event = "bedroom_declined"

        elif self.stage in ("bedroom", "open"):
            event = "open_conversation"

        self.total_turns += 1
        changes = {
            key: getattr(self, key) - value
            for key, value in before.items()
        }
        entry = {
            "text": normalized,
            "location": self.location,
            "event": event,
            "mood": self.mood_name(),
        }
        self.history.append(entry)
        self.history = self.history[-12:]

        return {
            "event": event,
            "mood": self.mood_name(),
            "objective": self.current_objective(),
            "changes": changes,
            "stage": self.stage,
        }

    @staticmethod
    def _contains(text, phrases):
        return any(phrase in text for phrase in phrases)

    @staticmethod
    def _normalize(text):
        return re.sub(r"\s+", " ", (text or "").lower()).strip()
