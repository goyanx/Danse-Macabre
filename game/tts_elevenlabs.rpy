## Voice playback for dialogue.
##
## Kokoro is the default local provider. OpenAI and ElevenLabs remain optional
## cloud alternatives, while system self-voicing is an accessibility fallback.

init python:
    import hashlib
    import json
    import os
    import re
    import subprocess
    import threading

    try:
        import requests
    except Exception:
        requests = None

    if not hasattr(store, "tts_enabled"):
        store.tts_enabled = True

    if not hasattr(store, "tts_provider"):
        store.tts_provider = "kokoro"

    if not hasattr(store, "tts_status"):
        store.tts_status = "Choose Test Voice to verify the selected provider."

    TTS_OPENAI_MODEL = os.environ.get("GLASSHOUSE_OPENAI_TTS_MODEL", "gpt-4o-mini-tts")
    TTS_OPENAI_URL = "https://api.openai.com/v1/audio/speech"
    TTS_ELEVENLABS_MODEL = os.environ.get("GLASSHOUSE_ELEVENLABS_MODEL", "eleven_flash_v2_5")
    TTS_ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    TTS_TEXT_LIMIT = int(os.environ.get("GLASSHOUSE_TTS_TEXT_LIMIT", "420"))
    TTS_KOKORO_PYTHON = os.environ.get("KOKORO_PYTHON", r"C:\Python312\python.exe")

    TTS_VOICES = {
        "lila": {
            "openai": os.environ.get("GLASSHOUSE_VOICE_LILA_OPENAI", "marin"),
            "elevenlabs": os.environ.get("GLASSHOUSE_VOICE_LILA_ELEVENLABS", "EXAVITQu4vr4xnSDxMaL"),
            "kokoro": os.environ.get("GLASSHOUSE_VOICE_LILA_KOKORO", "af_heart"),
        },
        "malcolm": {
            "openai": os.environ.get("GLASSHOUSE_VOICE_MALCOLM_OPENAI", "cedar"),
            "elevenlabs": os.environ.get("GLASSHOUSE_VOICE_MALCOLM_ELEVENLABS", "CwhRBWXzGAHq8TQ4Fs17"),
            "kokoro": os.environ.get("GLASSHOUSE_VOICE_MALCOLM_KOKORO", "am_michael"),
        },
        "director": {
            "openai": os.environ.get("GLASSHOUSE_VOICE_DIRECTOR_OPENAI", "ballad"),
            "elevenlabs": os.environ.get("GLASSHOUSE_VOICE_DIRECTOR_ELEVENLABS", "JBFqnCBsd6RMkjVDRZzb"),
            "kokoro": os.environ.get("GLASSHOUSE_VOICE_DIRECTOR_KOKORO", "bm_george"),
        },
    }

    _tts_jobs = set()
    _tts_current_key = None
    _tts_lock = threading.Lock()
    _kokoro_process = None
    _kokoro_process_lock = threading.Lock()

    def _tts_cache_dir():
        root = getattr(renpy.config, "savedir", None) or getattr(renpy.config, "gamedir", ".")
        path = os.path.join(root, "tts_cache")
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def _tts_clean_text(text):
        clean = renpy.substitute(str(text))
        clean = re.sub(r"\{[^}]+\}", "", clean)
        clean = re.sub(r"\[[^\]]+\]", "", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean[:TTS_TEXT_LIMIT]

    def _tts_voice_for(provider, speaker):
        return TTS_VOICES.get(speaker, TTS_VOICES["director"]).get(provider)

    def _tts_cache_path(provider, speaker, text, extension):
        voice = _tts_voice_for(provider, speaker) or ""
        raw = "|".join([provider, speaker, voice, TTS_OPENAI_MODEL, TTS_ELEVENLABS_MODEL, text])
        key = hashlib.sha1(raw.encode("utf-8")).hexdigest()
        return key, os.path.join(_tts_cache_dir(), "{}.{}".format(key, extension))

    def _tts_openai_instructions(speaker):
        if speaker == "lila":
            return "Speak with restrained elegance, emotional intelligence, and controlled tension. Natural human pacing, not announcer-like."
        if speaker == "malcolm":
            return "Speak with dry wit, warmth under pressure, and a tired late-night intimacy. Natural human pacing, not announcer-like."
        return "Speak as a calm, cinematic mystery narrator with subtle tension and clear pacing. Natural and intimate, not robotic."

    def _tts_play_if_current(key, path):
        global _tts_current_key
        if key != _tts_current_key:
            return
        if not os.path.exists(path):
            return
        try:
            renpy.music.play(path.replace("\\", "/"), channel="voice", loop=False)
            store.tts_status = "Voice is playing."
        except Exception as e:
            store.tts_status = "Voice playback failed. Check log.txt."
            renpy.log("TTS playback failed: {}".format(e))

    def _tts_set_status(message):
        store.tts_status = message

    def _tts_generate_elevenlabs(speaker, text, out_path):
        if requests is None:
            raise RuntimeError("The requests package is not available.")

        api_key = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("XI_API_KEY")
        if not api_key:
            raise RuntimeError("Set ELEVENLABS_API_KEY or XI_API_KEY to use ElevenLabs TTS.")

        voice_id = _tts_voice_for("elevenlabs", speaker)
        url = TTS_ELEVENLABS_URL.format(voice_id=voice_id)
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "text": text,
            "model_id": TTS_ELEVENLABS_MODEL,
            "voice_settings": {
                "stability": 0.48,
                "similarity_boost": 0.8,
                "style": 0.18,
                "use_speaker_boost": True,
            },
        }
        response = requests.post(
            url,
            params={"output_format": "mp3_44100_128"},
            headers=headers,
            data=json.dumps(payload),
            timeout=30,
        )
        response.raise_for_status()
        tmp_path = out_path + ".tmp"
        with open(tmp_path, "wb") as f:
            f.write(response.content)
        os.replace(tmp_path, out_path)

    def _tts_generate_openai(speaker, text, out_path):
        if requests is None:
            raise RuntimeError("The requests package is not available.")

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Set OPENAI_API_KEY to use OpenAI TTS.")

        headers = {
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }
        payload = {
            "model": TTS_OPENAI_MODEL,
            "voice": _tts_voice_for("openai", speaker),
            "input": text,
            "instructions": _tts_openai_instructions(speaker),
            "response_format": "mp3",
        }
        response = requests.post(TTS_OPENAI_URL, headers=headers, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        tmp_path = out_path + ".tmp"
        with open(tmp_path, "wb") as f:
            f.write(response.content)
        os.replace(tmp_path, out_path)

    def _tts_generate_kokoro(speaker, text, out_path):
        script = os.path.join(renpy.config.basedir, "tools", "kokoro_tts.py")
        if not os.path.exists(script):
            raise RuntimeError("Missing tools/kokoro_tts.py")

        voice = _tts_voice_for("kokoro", speaker)
        request = json.dumps({
            "text": text,
            "out": out_path,
            "voice": voice,
            "speed": 1.0,
        })

        with _kokoro_process_lock:
            _tts_start_kokoro_server_unlocked(script)

            try:
                _kokoro_process.stdin.write(request + "\n")
                _kokoro_process.stdin.flush()
                while True:
                    line = _kokoro_process.stdout.readline()
                    if not line:
                        raise RuntimeError("Kokoro worker stopped unexpectedly.")
                    if line.startswith("__KOKORO_RESULT__"):
                        result = json.loads(line[len("__KOKORO_RESULT__"):])
                        break
            except Exception:
                _tts_stop_kokoro_server()
                raise

        if not result.get("ok"):
            raise RuntimeError(result.get("error", "Kokoro TTS failed."))

    def _tts_start_kokoro_server_unlocked(script=None):
        global _kokoro_process
        if _kokoro_process is not None and _kokoro_process.poll() is None:
            return

        if script is None:
            script = os.path.join(renpy.config.basedir, "tools", "kokoro_tts.py")
        if not os.path.exists(script):
            return

        python_exe = TTS_KOKORO_PYTHON if os.path.isfile(TTS_KOKORO_PYTHON) else "python"
        _kokoro_process = subprocess.Popen(
            [python_exe, script, "--server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )

    def _tts_preload_kokoro():
        if not getattr(store, "tts_enabled", False):
            return
        if getattr(store, "tts_provider", "kokoro") != "kokoro":
            return
        if not _kokoro_process_lock.acquire(False):
            return
        try:
            _tts_start_kokoro_server_unlocked()
        finally:
            _kokoro_process_lock.release()

    def _tts_stop_kokoro_server():
        global _kokoro_process
        process = _kokoro_process
        _kokoro_process = None
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except Exception:
                pass

    def _tts_generate_worker(provider, speaker, text, key, path):
        try:
            if provider == "openai":
                _tts_generate_openai(speaker, text, path)
            elif provider == "elevenlabs":
                _tts_generate_elevenlabs(speaker, text, path)
            elif provider == "kokoro":
                _tts_generate_kokoro(speaker, text, path)
            else:
                return
            renpy.invoke_in_main_thread(_tts_play_if_current, key, path)
        except Exception as e:
            renpy.invoke_in_main_thread(
                _tts_set_status,
                "{} voice failed: {}".format(provider.title(), str(e)[:110]),
            )
            renpy.log("{} TTS generation failed: {}".format(provider, e))
        finally:
            with _tts_lock:
                _tts_jobs.discard(key)

    def _tts_start_cached(provider, speaker, text):
        global _tts_current_key
        extension = "wav" if provider == "kokoro" else "mp3"
        key, path = _tts_cache_path(provider, speaker, text, extension)
        _tts_current_key = key

        if os.path.exists(path):
            store.tts_status = "Using cached voice."
            _tts_play_if_current(key, path)
            return

        with _tts_lock:
            if key in _tts_jobs:
                return
            _tts_jobs.add(key)

        worker = threading.Thread(target=_tts_generate_worker, args=(provider, speaker, text, key, path))
        worker.daemon = True
        worker.start()
        store.tts_status = "Generating voice in the background..."

    def tts_play_sample():
        provider = getattr(store, "tts_provider", "kokoro")
        if provider == "off":
            store.tts_status = "Select a voice provider before testing."
            return
        if provider == "system":
            try:
                renpy.display.tts.speak("This is a voice sample from The Glass House.", force=True)
                store.tts_status = "System voice is playing."
            except Exception as e:
                store.tts_status = "System voice failed: {}".format(str(e)[:110])
            return
        _tts_start_cached(provider, "director", "This is a voice sample from The Glass House.")

    def tts_character_callback(event, interact=True, what=None, cb_speaker=None, **kwargs):
        if event != "begin":
            return
        if not interact or not what:
            return
        if not getattr(store, "tts_enabled", False):
            return

        if not cb_speaker:
            return

        provider = getattr(store, "tts_provider", "kokoro")
        speaker = cb_speaker
        text = _tts_clean_text(what)
        if not text:
            return

        try:
            renpy.music.stop(channel="voice")
        except Exception:
            pass

        if provider == "off":
            return
        if provider == "system":
            try:
                renpy.display.tts.speak(text, force=True)
            except Exception as e:
                renpy.log("System TTS failed: {}".format(e))
            return
        if provider in ("openai", "elevenlabs", "kokoro"):
            _tts_start_cached(provider, speaker, text)

    def configure_voice_startup():
        try:
            _preferences.self_voicing = False
        except Exception:
            pass

    config.all_character_callbacks.append(tts_character_callback)
    config.start_callbacks.append(configure_voice_startup)
    config.start_interact_callbacks.append(_tts_preload_kokoro)
    config.quit_callbacks.append(_tts_stop_kokoro_server)
