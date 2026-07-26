# TTS Providers

The game no longer enables Ren'Py self-voicing automatically. That system path depends on OS voices and can sound robotic.

The Preferences screen now exposes five voice choices:

- `Kokoro Local`: offline/local TTS through `tools/kokoro_tts.py`. This is the default provider.
- `OpenAI`: cloud TTS with local cache.
- `ElevenLabs`: cloud TTS with local cache. The configured key and all three character voices have been verified with `eleven_flash_v2_5`.
- `System Voice`: Ren'Py/system TTS for accessibility fallback.
- `Off`: no generated dialogue voice.

## OpenAI

Set `OPENAI_API_KEY` in the environment. Generated lines are cached in the Ren'Py save directory under `tts_cache`, so repeated lines do not call the API again.

Default model:

- `gpt-4o-mini-tts`

Default voices:

- Lila: `marin`
- Malcolm: `cedar`
- Director: `ballad`

Optional overrides:

- `GLASSHOUSE_VOICE_LILA_OPENAI`
- `GLASSHOUSE_VOICE_MALCOLM_OPENAI`
- `GLASSHOUSE_VOICE_DIRECTOR_OPENAI`
- `GLASSHOUSE_OPENAI_TTS_MODEL`, default `gpt-4o-mini-tts`

## ElevenLabs

Set `ELEVENLABS_API_KEY` or `XI_API_KEY` in the environment. Generated lines are cached in the Ren'Py save directory under `tts_cache`, so repeated lines do not call the API again.

Default voices:

- Lila: `Sarah - Mature, Reassuring, Confident`
- Malcolm: `Roger - Laid-Back, Casual, Resonant`
- Director: `George - Warm, Captivating Storyteller`

Optional overrides:

- `GLASSHOUSE_VOICE_LILA_ELEVENLABS`
- `GLASSHOUSE_VOICE_MALCOLM_ELEVENLABS`
- `GLASSHOUSE_VOICE_DIRECTOR_ELEVENLABS`
- `GLASSHOUSE_ELEVENLABS_MODEL`, default `eleven_flash_v2_5`

## Kokoro (default)

Kokoro is installed in `C:\Python312\python.exe` on this machine and the game uses it automatically. To use another Python runtime, install Kokoro into it:

```powershell
python -m pip install kokoro soundfile
```

Then set the executable path:

```powershell
$env:KOKORO_PYTHON="C:\Path\To\python.exe"
```

Default Kokoro voices:

- Lila: `af_heart`
- Malcolm: `am_michael`
- Director: `bm_george`

Optional overrides:

- `GLASSHOUSE_VOICE_LILA_KOKORO`
- `GLASSHOUSE_VOICE_MALCOLM_KOKORO`
- `GLASSHOUSE_VOICE_DIRECTOR_KOKORO`

Kokoro starts one persistent local worker from the title screen, keeping the model loaded between lines. Generated WAV files are cached in the Ren'Py save directory under `tts_cache`.
