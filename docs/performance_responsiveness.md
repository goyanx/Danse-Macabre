# Performance and Responsiveness Notes

This project avoids running local model calls on the Ren'Py UI thread.

## Current Rules

- Player progression is deterministic and synchronous. Beat matching must stay fast and local.
- Ollama calls are optional flavor, not required for progression.
- Dynamic NPC replies in `game/facade_story.rpy` use `chatgpt.completion_async`.
- The UI polls async jobs with short `renpy.pause(..., hard=False)` intervals while showing the `thinking` overlay.
- If the model is slow or unavailable, the story uses deterministic fallback lines.
- Director nudges are computed locally by default so help never freezes the interface.
- Voiceover should be loaded from local files when possible. Any cloud TTS should run as a build-time generation step or an async cache fill after text is already visible.

## Tunables

- `OLLAMA_TIMEOUT_SECONDS`, default `8`, limits network calls in `game/python-packages/chatgpt/__init__.py`.
- `FACADE_MODEL_WAIT_SECONDS`, default `3.5`, limits how long the script waits for a dynamic reply before falling back.
- `FACADE_MODEL_POLL_SECONDS`, default `0.1`, controls UI polling cadence during async model work.

## Anti-Patterns To Avoid

- Do not call `chatgpt.completion(...)` directly from a Ren'Py label that is part of normal player flow.
- Do not mutate Ren'Py store objects from worker threads.
- Do not let model output decide whether a beat progresses. Use local beat rules first, then model text for atmosphere.
- Do not wait indefinitely for Ollama. Always provide a deterministic fallback.
- Do not call cloud TTS synchronously during dialogue display. Pre-generate authored lines, cache dynamic lines by speaker/text hash, and keep Ren'Py playback local.
