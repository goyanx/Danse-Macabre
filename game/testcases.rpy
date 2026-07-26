init python:
    def _voice_initialization_smoke_start():
        global _tts_current_key

        fixture = os.path.join(
            renpy.config.basedir,
            "tests",
            "fixtures",
            "director_voice_smoke.wav",
        )
        key = "voice-initialization-smoke"
        _tts_current_key = key
        _tts_play_if_current(key, fixture)


testcase voice_initialization:
    $ _preferences.set_volume("voice", 1.0)
    $ _preferences.mute["voice"] = False
    $ _voice_initialization_smoke_start()
    pause 0.5
    assert tts_status == "Voice is playing."
    assert renpy.music.is_playing(channel="generated_voice")
    run Quit(confirm=False)
