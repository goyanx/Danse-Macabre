# The Glass House Story Outline

The game is structured as a chamber-drama mystery about two hosts, Lila and Malcolm Vale, whose marriage has become a performance staged for guests. The player advances by saying or doing things that trigger specific beats. If the player stalls, the DM detects repeated non-progress turns and gives a subtle nudge toward the current beat.

Implementation notes:

- Each beat is represented in `game/python-packages/storydm/__init__.py` with a location, trigger phrases, journal text, callback label, and fallback nudge.
- Player progression can happen through free typed dialogue or through explicit room actions in `game/facade_story.rpy`.
- The Director watches turns since last progress. After three non-progress turns, or when the player presses the Director button, it provides a subtle nudge.
- The Director and dynamic NPC replies use a nonblocking LLM worker. OpenAI is used when configured, with Ollama as an optional local alternative and deterministic fallback lines when neither service is available.
- Director conversations receive only the current room, current act, recent Director exchanges, and journal facts the player has already earned. Generated replies are filtered again for premature solution language.
- Character/NPC speech can use cached OpenAI TTS, ElevenLabs, local Kokoro, system voice fallback, or be disabled from Preferences.

## Act I - Arrival at the Glass House

The player arrives at the Vales' townhouse after a party. The room is polished, expensive, and wrong in small ways.

- The practiced welcome: greet the hosts, accept the social frame, or ask why the invitation came so late.
- The flaw in the display: inspect the portrait, mantel, glasses, or visible crack in the room's presentation.
- The toast that names the ghost: question the toast, anniversary, missing guest, or the name Vivian.

## Act II - The Polite War

Lila and Malcolm recruit the player as audience, judge, and shield while the fight becomes more specific.

- The marriage as theatre: call out the rehearsed quality of their arguments or ask whether the conflict is a performance.
- A place set for absence: inspect the bar, kitchen, third glass, or extra place setting.
- Vivian becomes unavoidable: press the hosts about Vivian, the absent guest, the empty chair, or who the third glass was meant for.

## Act III - The Missing Guest

The private room opens. The player discovers the document that changes the mystery from disappearance to confession.

- The locked room opens: go to the study and inspect the desk, drawer, letter, or manuscript.
- The invented daughter: confront the letter's phrase, "our best lie," and name Vivian as fiction.
- Break the game or preserve it: choose a human response by telling them to stop, speak truth, apologize, leave, stay, or forgive.

## Act IV - After Midnight

The performance collapses into quiet. The last beats resolve through restraint rather than accusation.

- The room with no child: ask about Vivian's room, the nursery, the closed door, or the empty bedroom.
- The final silence: leave, sit quietly, say goodbye, wait, or end the evening.
