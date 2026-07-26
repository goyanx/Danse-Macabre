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

- `OLLAMA_TIMEOUT_SECONDS`, default `30`, limits each Ollama HTTP request.
- `OPENAI_CHAT_TIMEOUT_SECONDS`, default `30`, limits an OpenAI chat request.
- `GLASSHOUSE_LLM_WAIT_SECONDS`, default `30`, controls how long all story
  modules wait for a dynamic reply before using authored fallback dialogue.
- `GLASSHOUSE_LLM_POLL_SECONDS`, default `0.1`, controls the non-blocking UI
  polling cadence during asynchronous model work.
- `OLLAMA_NUM_PREDICT`, default `96`, and `OPENAI_CHAT_MAX_TOKENS`, default
  `96`, cap short dialogue generation.
- `OLLAMA_THINK`, default `false`, prevents reasoning traces from consuming the
  response budget during normal character dialogue.
- `OLLAMA_KEEP_ALIVE`, default `10m`, avoids repeatedly loading the local model.

`facade_story.rpy` and `extra_act_story.rpy` read the shared UI values from the
`chatgpt` adapter. Do not introduce a separate hard-coded story timeout.

## Anti-Patterns To Avoid

- Do not call `chatgpt.completion(...)` directly from a Ren'Py label that is part of normal player flow.
- Do not mutate Ren'Py store objects from worker threads.
- Do not let model output decide whether a beat progresses. Use local beat rules first, then model text for atmosphere.
- Do not wait indefinitely for Ollama. Always provide a deterministic fallback.
- Do not enable reasoning for short NPC lines unless a specific feature truly
  requires it.
- Do not use a vague "be concise" instruction without a one-line format,
  sentence count, word limit, and explicit ban on preambles and postscripts.
- Do not call cloud TTS synchronously during dialogue display. Pre-generate authored lines, cache dynamic lines by speaker/text hash, and keep Ren'Py playback local.
