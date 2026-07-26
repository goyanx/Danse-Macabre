# The Glass House Enhancement Roadmap

These are high-value follow-ups for improving the game beyond the current playable version.

## Narrative Depth

- Add relationship state tracking for Lila, Malcolm, and the player: trust, resentment, alliance, and discomfort.
- Let the final scene branch based on whether the player comforts, accuses, withdraws, or enables the couple's performance.
- Add optional memory fragments that reframe Vivian as a shared ritual rather than a single twist.
- Give Lila and Malcolm private contradictions so repeated playthroughs expose different emotional angles.

## DM and Progression

- Add beat confidence scoring instead of simple trigger matching, so partial player intent can advance or receive tailored clarification.
- Store recent locations, failed actions, and repeated questions in the journal for richer Director nudges.
- Add a "soft lock rescue" mode where the Director can unlock one contextual action after extended confusion.
- Log anonymized local playtest traces to tune trigger phrases and nudge timing.

## Speech and Performance

- Add character-specific in-app speech settings for pace, pitch, and voice where the Ren'Py runtime supports it.
- Add a spoken Director accessibility mode that summarizes the current room, available actions, and last discovered clue.
- Add optional text effects for interruptions, overlapping argument rhythms, and silence after key revelations.
- Upgrade from Ren'Py self-voicing to optional generated voice clips for major authored lines; the current self-voicing path depends on system voices and can sound robotic.
- Prefer pre-generated or cached voiceover over live blocking TTS calls in normal dialogue flow.
- Best current ElevenLabs fit: `eleven_v3` for expressive pre-rendered Lila/Malcolm/Director lines, `eleven_flash_v2_5` for low-latency interactive generation, and `eleven_turbo_v2_5` as a balanced fallback.
- Candidate ElevenLabs voices from the connected account for this chamber mystery: `Sarah - Mature, Reassuring, Confident` for Lila, `Roger - Laid-Back, Casual, Resonant` for Malcolm, and `British Archeologist` or `Lisa Kim - calm and smart` for Director narration.
- OpenAI TTS is another strong route for a simpler stack; current OpenAI docs recommend `marin` or `cedar` for best quality.
- Add a build-time voice generation tool that reads curated dialogue lines, writes stable files under `game/audio/voice/`, and emits a manifest so Ren'Py can play local audio without waiting on network calls.
- For dynamic AI replies, generate audio asynchronously only after text fallback is already on screen, then cache by speaker/text hash for future playthroughs.

## Art and Presentation

- Extend the GPT-generated high-fidelity room backgrounds to the street, map, menu, and closeup images.
- Add character poses for Lila and Malcolm: composed, amused, wounded, angry, and exhausted.
- Add room detail closeups for the cracked portrait, third glass, study letter, and closed door.
- Add subtle animated overlays: city light flicker, glass reflection, study lamp hum, and late-night window rain.

## Audio

- Generate additional ElevenLabs sound effects for glass handling, floorboards, drawer locks, distant traffic, and room tone loops.
- Add adaptive ambience that shifts as the marriage performance deteriorates.
- Add silence as a deliberate audio event after the invented-daughter reveal.

## TTS References

- ElevenLabs model guidance: https://elevenlabs.io/docs/overview/models
- ElevenLabs v3: https://elevenlabs.io/v3
- OpenAI text-to-speech guide: https://developers.openai.com/api/docs/guides/text-to-speech

## Interface

- Replace the text-based Director button with a small icon that matches the map and journal UI.
- Add a compact current-objective panel that can be toggled without spoiling the next beat.
- Add journal filtering by people, rooms, and discovered lies.
- Add a first-run accessibility prompt for self-voicing and text speed.

## Testing and Tooling

- Add automated tests for every beat trigger, callback label, and room unlock.
- Add a Ren'Py lint wrapper script that fails on new warnings while allowing explicitly documented legacy warnings.
- Add an asset manifest that verifies every referenced background, sprite, sound, and GUI image exists.
- Add a local Ollama health check screen with selected model, endpoint status, and fallback state.
