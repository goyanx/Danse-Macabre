# Extra Act -1: Romance Epilogue Design

This document describes the unlockable romance sandbox that follows completion
of **The Glass House**. It is intended for authors and coding agents extending
the epilogue without breaking saves, consent rules, asynchronous dialogue, or
its open-ended structure.

## Player Contract

`Extra Act -1` appears on the main menu after `facade_ending` has been seen.
The ending also writes `persistent.facade_extra_act_unlocked` and immediately
saves persistent data. Checking `renpy.seen_label("facade_ending")` preserves
the unlock for players who completed the story before this feature existed.

The epilogue is an adult, consensual romance. Lila retains independent goals,
may decline any escalation, and never rewards pressure. Intimate scenes are
cinematic and non-graphic: the bedroom background remains visible while
dialogue and narration carry the emotional scene.

## File Ownership

| Path | Responsibility |
| --- | --- |
| `game/extra_act_story.rpy` | Menu unlock helper, authored choices, scenes, async Lila replies, fallback dialogue, and open loops |
| `game/python-packages/extraact/__init__.py` | Serializable mood, relationship, objective, boundary, stage, and progression rules |
| `tests/test_extraact.py` | Deterministic progression and pickle/save compatibility |
| `tests/test_project_contracts.py` | Unlock, asset, async, open-loop, and Ren'Py initialization contracts |
| `game/images/bg extra *.png` | Date, apartment, and bedroom backgrounds |
| `game/images/lila club *.png` | Neutral, warm, and guarded club-dress expressions |

The Python engine decides whether a date, apartment invitation, or bedroom
invitation is accepted. Ren'Py presents the outcome. An LLM may only word
Lila's response and must never determine progression.

## State Machine

```text
invitation
    -> choose_date
    -> date (jazz lounge or rooftop)
    -> home (player apartment)
    -> bedroom
    -> open (bedroom or living room)
```

The player can end the extra act from any major location. Once the open state
is reached, no story counter forces an ending; the player may keep using
authored prompts or `Speak freely` until choosing to return to the main menu.

`ExtraActState` stores only serializable values:

```text
stage, location
trust, respect, warmth, attraction
boundary_violations
date_turns, home_turns, total_turns
history (latest 12 normalized turns)
```

Do not add threads, subprocesses, locks, audio objects, or completion jobs to
this class. Ren'Py must be able to pickle it during any menu or dialogue line.

## Mood, Objectives, and Consent

`mood_name()` derives `guarded`, `curious`, `warm`, or `close` from the
relationship values. `current_objective()` exposes a stage-appropriate writing
goal. These values guide expression selection and the optional LLM prompt; they
are not hidden random rolls.

Escalation requirements are intentionally explicit:

- A date requires an invitation with no boundary violation.
- Going home requires at least three date turns, trust, respect, attraction,
  and zero boundary violations.
- Entering the bedroom requires at least two home turns, stronger trust and
  respect, attraction, and zero boundary violations.
- Pressure lowers trust and respect and produces a firm boundary response.

When adding phrases, prefer specific natural language over broad tokens. Add
unit tests for every new accepted and declined pathway.

## Dialogue Architecture

Every turn follows this order:

1. Display the player input.
2. Call `ExtraActState.register_turn`.
3. Start `chatgpt.completion_async` for optional wording.
4. Poll in configurable `GLASSHOUSE_LLM_POLL_SECONDS` slices, default `0.1`,
   for at most `GLASSHOUSE_LLM_WAIT_SECONDS`, default `30`, using non-hard
   pauses.
5. Validate the result and use a deterministic fallback if unavailable.
6. Select Lila's expression and display her voiced Character line.

This order is important. Progress succeeds even when Ollama is offline, and
the interface continues processing events while the completion runs. Keep job
variables local and underscore-prefixed; never store an active job in `default`
or persistent state.

`Read the moment` uses the same async pattern with `extra_moment_messages`.
It sends a compact `ExtraActState.moment_context()` snapshot, asks for one
`Director:` line of no more than 42 words, and falls back to the deterministic
mood/objective text if the model is unavailable or malformed. The insight may
explain Lila's visible mood, present need, and a useful next approach, but it
must not expose numeric scores, hidden mechanics, spoilers, or reasoning.

The model prompt must preserve all of these constraints:

- Both characters are adults.
- Lila is independent and may refuse.
- Mood and current objective guide, but do not mechanically dictate, wording.
- Responses remain in character, concise, plain spoken, emotional, and
  spoiler-free.
- Lila may use brief hesitations, soft laughs, sighs, gasps, `mm`, or restrained
  moans when the relationship state and scene stage support them.
- Avoid polished aphorisms, theatrical prose, glib banter, and overly clever
  lines.
- Responses contain exactly one `Lila:` line, one or two complete sentences,
  and no more than 36 words.
- Responses contain no preamble, postscript, reasoning, heading, stage
  direction, quotation wrapper, alternative answer, or follow-up offer.
- Intimacy may be suggestive but not graphically sexual.
- No mention of prompts, models, scores, or game internals.

## Art and Presentation

The extra act reuses the cinematic act-card screen with:

```renpy
call facade_show_act_card("Extra Act -1 - One More Night")
```

Date and apartment scenes show a full-body Lila sprite. The bedroom scene hides
the sprite and stays on `bg extra bedroom`, allowing narration and dialogue to
carry private moments without explicit character art.

Background contract: `1920x1080` RGB PNG. Sprite contract: `620x1080` RGBA PNG
with transparent corners. New expressions must preserve Lila's identity,
wardrobe, proportions, lighting direction, and visual realism.

## Extension Checklist

1. Add a deterministic engine event or stage rule first.
2. Add focused unit tests for acceptance, refusal, and pickle compatibility.
3. Add authored choices whose internal text contains the intended semantic cues.
4. Add a deterministic fallback response for every new event.
5. Keep LLM work optional, bounded, and presentation-only.
6. Add backgrounds and expressions at native dimensions.
7. Keep intimate content consensual, adult, non-graphic, and interruptible.
8. Preserve an explicit route back to the main menu.
9. Run `python tools/run_tests.py --voice-init --lint`.
