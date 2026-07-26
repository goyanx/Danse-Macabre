#The rollback creates some bugs, so I disable it
define config.rollback_enabled = False

define playlist = [ "audio/music/glass_house_dark_ambience_loop.ogg" ]

init python:
    import storydm

##BASIC GAME STRUCTURE##
label start:
    #Change the music
    stop music fadeout 1.0
    $ renpy.random.shuffle(playlist)         # Should shuffle in place
    play music playlist fadeout 1.0 fadein 1.0 volume 0.32

    # Start the new chamber-drama mystery.
    call facade_intro from _call_facade_intro

    return
