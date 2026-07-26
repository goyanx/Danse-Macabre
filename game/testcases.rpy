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


testcase act_card_initialization:
    run Show("facade_act_card", act_label="ACT II", act_name="THE POLITE WAR")
    pause 0.2
    assert renpy.get_screen("facade_act_card") is not None
    run Quit(confirm=False)


testcase extra_act_initialization:
    $ extra_state = extraact.ExtraActState()
    $ extra_result = extra_state.register_turn("Would you have a drink with me? No pressure; it is your choice.")
    assert extra_result["event"] == "date_accepted"
    assert extra_state.choose_date("jazz_lounge")
    assert extra_state.current_objective()
    $ extra_slot = "_extra_act_runtime_smoke"
    $ renpy.save(extra_slot, extra_info="Extra act runtime smoke test")
    assert renpy.can_load(extra_slot)
    $ renpy.unlink_save(extra_slot)
    run Quit(confirm=False)


testcase voice_initialization:
    $ _preferences.set_volume("voice", 1.0)
    $ _preferences.mute["voice"] = False
    $ _voice_initialization_smoke_start()
    pause 0.5
    assert tts_status == "Voice is playing."
    assert renpy.music.is_playing(channel="generated_voice")
    $ _voice_save_smoke()
    run Quit(confirm=False)
