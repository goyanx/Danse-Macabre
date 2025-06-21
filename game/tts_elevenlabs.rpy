init python:
    import requests
    import os
    
    # Set your API key and desired voice ID here
    ELEVEN_API_KEY = "ea80ff9c0313ec59031f04c7f5bf7969"  # <-- Replace with your real key
    ELEVEN_VOICE_ID = "wyWA56cQNU2KqUW4eCsI"  # <-- Replace with your voice id

    # Path to save temporary TTS audio
    AUDIO_PATH = "game/audio/tts_tmp.mp3"

    # Default to enabled, can be changed via GUI
    if not hasattr(store, 'tts_enabled'):
        tts_enabled = True

    # Helper: Get the length of mp3 for sync
    def get_mp3_length(path):
        try:
            from mutagen.mp3 import MP3
            audio = MP3(path)
            return audio.info.length
        except Exception:
            return 0.5  # fallback to a short wait

    def speak(text):
        if not tts_enabled:
            return

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVEN_VOICE_ID}"
        headers = {"xi-api-key": ELEVEN_API_KEY, "Content-Type": "application/json"}
        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                with open(AUDIO_PATH, "wb") as f:
                    f.write(response.content)
                renpy.music.play(AUDIO_PATH, channel="voice", loop=False)
                
                # Optionally wait for the audio duration
                duration = get_mp3_length(AUDIO_PATH)
                renpy.pause(duration, hard=False)
            else:
                renpy.log(f"ElevenLabs TTS Error: {response.status_code} {response.text}")
        except Exception as e:
            renpy.log(f"ElevenLabs TTS Exception: {e}")


    # Integrate TTS callback with Ren'Py say events

define config.say_menu_text_callback = speak
