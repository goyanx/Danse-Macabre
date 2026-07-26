init python:
    def _voice_initialization_smoke_start():
        fixture = os.path.join(
            renpy.config.basedir,
            "tests",
            "fixtures",
            "director_voice_smoke.wav",
        )
        key = "voice-initialization-smoke"
        _tts_runtime.current_key = key
        _tts_play_if_current(key, fixture)

    class _UnpickleableVoiceRuntimeFixture(object):
        def __init__(self):
            self.lock = threading.Lock()

    def _voice_save_smoke():
        slot = "_voice_runtime_smoke"
        previous_process = _tts_runtime.kokoro_process
        try:
            _tts_runtime.kokoro_process = _UnpickleableVoiceRuntimeFixture()
            renpy.save(slot, extra_info="Voice runtime smoke test")
        finally:
            _tts_runtime.kokoro_process = previous_process
            if renpy.can_load(slot):
                renpy.unlink_save(slot)


testcase voice_initialization:
    $ _preferences.set_volume("voice", 1.0)
    $ _preferences.mute["voice"] = False
    $ _voice_initialization_smoke_start()
    pause 0.5
    assert tts_status == "Voice is playing."
    assert renpy.music.is_playing(channel="generated_voice")
    $ _voice_save_smoke()
    run Quit(confirm=False)
