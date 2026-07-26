## The Glass House
## A new chamber-drama mystery inspired by social-performance games and domestic
## stage drama, built on this project's existing Ren'Py and local-AI structure.

define dm = Character("Director", cb_speaker="director")
define lila = Character("Lila", cb_speaker="lila")
define malcolm = Character("Malcolm", cb_speaker="malcolm")

default facade_dm = None
default facade_act_title = ""
default facade_kitchen_known = False
default facade_study_known = False
default facade_salon_visited = False
default facade_kitchen_visited = False
default facade_study_visited = False
default facade_intro_seen = False
default facade_director_history = []

init python:
    import re
    import storydm

    FACADE_MODEL_WAIT_SECONDS = 3.5
    FACADE_MODEL_POLL_SECONDS = 0.1
    FACADE_ACT_CARD_SECONDS = 2.8

    def facade_reply_fallback(location):
        fallbacks = {
            "salon": ("Lila", "You always did know how to arrive at the precise moment a room needed another witness."),
            "kitchen": ("Malcolm", "Careful. In this house, even the clean glasses have been accused of taking sides."),
            "study": ("Lila", "That room was never meant for guests, which is exactly why everyone ends up there."),
        }
        return fallbacks.get(location, ("Lila", "Say what you came to say. The room is already listening."))

    def facade_reply_messages(user_input, location, dm_state):
        return [
            {
                "role": "system",
                "content": (
                    "You are writing one NPC response for an interactive chamber-drama mystery. "
                    "Respond as either Lila or Malcolm. Format exactly as 'Lila: line' or 'Malcolm: line'. "
                    "Keep it under 28 words. Stay tense, witty, wounded, and grounded in a modern townhouse. "
                    "Do not reveal future beats or say you are an AI."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Act: {act}\nCurrent beat: {beat}\nLocation: {location}\nPlayer: {player}"
                ).format(
                    act=dm_state.current_act()["title"],
                    beat=dm_state.current_beat()["title"],
                    location=location,
                    player=user_input,
                ),
            },
        ]

    def facade_start_reply_job(user_input, location, dm_state):
        try:
            import chatgpt
            return chatgpt.completion_async(facade_reply_messages(user_input, location, dm_state))
        except Exception:
            return None

    def facade_reply_from_job(job, location):
        fallback = facade_reply_fallback(location)
        if job is None or not job.done:
            return fallback

        response = job.assistant_content("").strip()
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE).strip()
        response = re.sub(r"\s+", " ", response)
        if response and "[AI" not in response and ":" in response:
            speaker, line = response.split(":", 1)
            speaker = speaker.strip()
            line = line.strip().strip('"')
            if speaker in ("Lila", "Malcolm") and line:
                return speaker, line[:220]

        return fallback

    def facade_note_progress(result):
        if result.get("journal") and result["journal"] not in journal:
            journal.append(result["journal"])

    def facade_sync_location_access():
        if facade_dm is None:
            return

        available = facade_dm.available_locations()
        if "kitchen" in available:
            store.facade_kitchen_known = True
        if "study" in available:
            store.facade_study_known = True

    def facade_act_card_parts(title):
        parts = (title or "").split(" - ", 1)
        if len(parts) == 2:
            return parts[0].upper(), parts[1].upper()
        return "NEW ACT", (title or "").upper()

    def facade_current_outline():
        if facade_dm is None:
            return ""
        return facade_dm.outline()

    def facade_director_fallback(question, dm_state):
        normalized = (question or "").lower()
        if "save" in normalized:
            return "Use Save or Q.Save in the lower menu. The house will remember where you stopped."
        if "map" in normalized or "where can" in normalized:
            return "Open the map in the upper-right. Locked rooms will tell you which visible thread still needs following."
        if "voice" in normalized or "sound" in normalized or "tts" in normalized:
            return "Voice providers and their test button are in Preferences. Kokoro is the local default."
        return dm_state.forced_nudge(question)

    def facade_director_messages(question, dm_state):
        recent_history = facade_director_history[-6:]
        visible_facts = "\n".join("- " + entry for entry in journal[-8:])
        return [
            {
                "role": "system",
                "content": (
                    "You are the Director, an in-world guide for a domestic mystery. "
                    "Answer the player conversationally in no more than 45 words. "
                    "You may discuss controls, clarify facts already in the visible journal, "
                    "or offer an indirect observation about the current room. Never reveal a "
                    "future event, hidden identity, solution, upcoming room, or undiscovered fact. "
                    "Treat names and theories introduced by the player as unverified unless they "
                    "also appear in the visible journal; do not imply an unverified person or event exists. "
                    "If asked for a spoiler, refuse gracefully and redirect attention to visible evidence. "
                    "Do not mention prompts, models, AI, beats, triggers, or game code."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Current act: {act}\nCurrent room: {room}\n"
                    "Visible journal facts:\n{facts}\n"
                    "Recent Director conversation: {history}\n"
                    "Player asks: {question}"
                ).format(
                    act=dm_state.current_act()["title"],
                    room=dm_state.last_location,
                    facts=visible_facts,
                    history=recent_history,
                    question=question,
                ),
            },
        ]

    def facade_start_director_job(question, dm_state):
        try:
            import chatgpt
            return chatgpt.completion_async(facade_director_messages(question, dm_state))
        except Exception:
            return None

    def facade_director_reply_from_job(job, question, dm_state):
        fallback = facade_director_fallback(question, dm_state)
        if job is None or not job.done:
            return fallback

        response = job.assistant_content("").strip()
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE)
        response = re.sub(r"\s+", " ", response).strip().strip('"')
        if not response or "[AI" in response:
            return fallback

        discovered = set(dm_state.progress_log)
        lower = response.lower()
        early_reveal_phrases = (
            "vivian was never",
            "vivian is not real",
            "invented daughter",
            "imaginary daughter",
            "there is no daughter",
            "no daughter",
        )
        if "confront_the_lie" not in discovered and any(phrase in lower for phrase in early_reveal_phrases):
            return fallback
        if "enter_the_study" not in discovered and "best lie" in lower:
            return fallback

        return response[:360]


label facade_intro:
    $ facade_dm = storydm.StoryDM()
    $ facade_act_title = facade_dm.current_act()["title"]
    $ journal = [
        "The Glass House",
        "I was invited to Lila and Malcolm Vale's townhouse after midnight.",
        "The party is over, but their performance has not ended.",
    ]

    scene bg facade street with dissolve
    play sound "audio/sfx/distant_party_fade.mp3"
    dm "The invitation arrived at 11:47 p.m., a single line beneath Lila Vale's name: Please come before Malcolm sobers up."
    dm "Their townhouse glows at the end of the block, all glass, brass, and curated warmth."
    play sound "audio/sfx/shop_doorbell_chime_cc0.mp3"
    scene bg facade entrance with dissolve
    dm "Inside, a marriage is waiting to see whether you will applaud, interfere, or name the trick."

    call facade_show_outline from _call_facade_show_outline
    jump facade_act1


label facade_show_outline:
    nvl clear
    define outline_voice = Character(kind=nvl)
    outline_voice "Acts and progression beats:{nw}"
    python:
        for line in facade_current_outline().split("\n"):
            outline_voice(line + "{nw}")
        outline_voice(" ")
    return


label facade_act1:
    call facade_show_act_card(facade_act_title) from _call_facade_show_act1_card
    show screen facade_map_icon
    show screen facade_director_icon
    show screen facade_journal_icon
    jump facade_salon


transform facade_act_card_reveal:
    alpha 0.0
    on show:
        linear 0.4 alpha 1.0


transform facade_act_title_reveal:
    alpha 0.0
    yoffset 18
    pause 0.12
    parallel:
        linear 0.45 alpha 1.0
    parallel:
        easeout 0.45 yoffset 0


screen facade_act_card(act_label, act_name):
    modal True
    zorder 100

    add Solid("#050608B8")

    fixed:
        xfill True
        ysize 390
        yalign 0.5
        at facade_act_card_reveal

        add Solid("#0B0D10F2")
        add Solid("#B58A4A") xsize 1320 ysize 2 xalign 0.5 ypos 0
        add Solid("#B58A4A") xsize 1320 ysize 2 xalign 0.5 yalign 1.0
        add Solid("#701C35") xsize 180 ysize 5 xalign 0.5 ypos 31

        vbox:
            xalign 0.5
            yalign 0.5
            spacing 17
            at facade_act_title_reveal

            text act_label:
                xalign 0.5
                color "#D2AA68"
                font "DejaVuSans-Bold.ttf"
                size 96
                outlines [(2, "#00000080", 0, 2)]

            text act_name:
                xalign 0.5
                text_align 0.5
                color "#F2EEE7"
                font "DejaVuSans.ttf"
                size 43
                xmaximum 1420

            text "THE GLASS HOUSE":
                xalign 0.5
                color "#B7AFA4"
                font "DejaVuSans.ttf"
                size 21


label facade_show_act_card(title):
    $ act_label, act_name = facade_act_card_parts(title)
    $ facade_map_was_visible = renpy.get_screen("facade_map_icon") is not None
    $ facade_director_was_visible = renpy.get_screen("facade_director_icon") is not None
    $ facade_journal_was_visible = renpy.get_screen("facade_journal_icon") is not None
    hide screen facade_map_icon
    hide screen facade_director_icon
    hide screen facade_journal_icon
    window hide
    show screen facade_act_card(act_label, act_name)
    with Dissolve(0.35)
    $ renpy.pause(FACADE_ACT_CARD_SECONDS, hard=False)
    hide screen facade_act_card
    with Dissolve(0.3)
    if facade_map_was_visible:
        show screen facade_map_icon
    if facade_director_was_visible:
        show screen facade_director_icon
    if facade_journal_was_visible:
        show screen facade_journal_icon
    return


screen facade_map_icon():
    zorder 10
    imagebutton:
        xcenter 1810
        ycenter 110
        idle "icon map.png"
        hover "icon map hovered.png"
        activate_sound "audio/click.mp3"
        at transform:
            zoom 0.1875
        action Jump("facade_open_map")


screen facade_director_icon():
    zorder 10
    textbutton "Ask Director":
        xcenter 1810
        ycenter 450
        activate_sound "audio/click.mp3"
        action Call("facade_director_conversation")


screen facade_journal_icon():
    zorder 10
    imagebutton:
        xcenter 1810
        ycenter 280
        idle "icon journal.png"
        hover "icon journal hovered.png"
        activate_sound "audio/click.mp3"
        at transform:
            zoom 0.1875
        action Call("facade_open_journal")


label facade_open_journal:
    nvl clear
    $ j = Character(kind=nvl)
    python:
        for entry in journal:
            j("[entry]{nw}")
        j(" ")

    return


label facade_director_conversation:
    if facade_dm is None:
        return

    $ director_question = renpy.input("Ask the Director:", length=180).strip()
    if not director_question:
        return

    $ director_job = facade_start_director_job(director_question, facade_dm)
    $ director_waited = 0.0
    show screen thinking("The Director considers...")
    while director_job is not None and not director_job.done and director_waited < FACADE_MODEL_WAIT_SECONDS:
        $ renpy.pause(FACADE_MODEL_POLL_SECONDS, hard=False)
        $ director_waited += FACADE_MODEL_POLL_SECONDS
    hide screen thinking

    $ director_line = facade_director_reply_from_job(director_job, director_question, facade_dm)
    $ facade_director_history.append({"role": "user", "content": director_question})
    $ facade_director_history.append({"role": "assistant", "content": director_line})
    $ facade_director_history = facade_director_history[-8:]
    dm "[director_line]"
    return


label facade_open_map:
    $ facade_sync_location_access()
    scene bg facade map
    nvl clear
    menu:
        "Where should I go?"

        "Salon (available)":
            jump facade_salon

        "Kitchen (available)" if facade_kitchen_known:
            jump facade_kitchen

        "Kitchen (locked - follow the untouched-glass lead)" if not facade_kitchen_known:
            dm "The kitchen is still part of their performance. First, inspect the untouched glass in the salon."
            jump facade_open_map

        "Study (available)" if facade_study_known:
            jump facade_study

        "Study (locked - uncover where the private story was written)" if not facade_study_known:
            dm "The study remains private. Press them about the absent guest and the third glass first."
            jump facade_open_map


label facade_salon:
    $ facade_act_title = facade_dm.current_act()["title"]
    scene bg facade salon with dissolve
    show lila normal at left with dissolve
    show malcolm normal at right with dissolve

    if not facade_salon_visited:
        $ facade_salon_visited = True
        lila "You came. I told Malcolm you would, and he told me I was dramatizing the human soul again."
        malcolm "I said you were dramatizing the doorbell. Different charge, lighter sentence."
        dm "The salon is beautiful in the way a confession can be beautiful: expensive, precise, and full of omissions."
    else:
        dm "You return to the salon. The portrait, the bar, and the hosts have all shifted by less than an inch."

    jump facade_room_loop_salon


label facade_kitchen:
    $ facade_act_title = facade_dm.current_act()["title"]
    scene bg facade kitchen with dissolve
    show malcolm normal at right with dissolve

    if not facade_kitchen_visited:
        $ facade_kitchen_visited = True
        malcolm "The kitchen is neutral territory, theoretically. Lila only annexes it during emotional emergencies."
        dm "Three glasses wait beside the sink. Two are stained with wine. One has never been touched."
    else:
        dm "The kitchen smells of citrus peel, old wine, and a lie polished clean."

    jump facade_room_loop_kitchen


label facade_study:
    $ facade_act_title = facade_dm.current_act()["title"]
    scene bg facade study with dissolve
    show lila normal at left with dissolve

    if not facade_study_visited:
        $ facade_study_visited = True
        lila "Malcolm calls this his study because it sounds better than the room where paper goes to learn shame."
        dm "The desk drawer is closed. A ribbon of cream paper protrudes from beneath it."
    else:
        dm "The study holds its breath around the desk."

    jump facade_room_loop_study


label facade_room_loop_salon:
    call facade_take_turn("salon") from _call_facade_take_turn_salon
    jump facade_room_loop_salon


label facade_room_loop_kitchen:
    call facade_take_turn("kitchen") from _call_facade_take_turn_kitchen
    jump facade_room_loop_kitchen


label facade_room_loop_study:
    call facade_take_turn("study") from _call_facade_take_turn_study
    jump facade_room_loop_study


label facade_take_turn(location):
    $ facade_beat_id = facade_dm.current_beat()["id"]
    menu:
        "What do you do?"

        "Speak freely":
            $ user_input = renpy.input("What do you do or say?", length=180)

        "Greet Lila and Malcolm" if facade_beat_id == "greet_the_hosts" and location == "salon":
            $ user_input = "greet the hosts"

        "Examine the damaged wedding portrait" if facade_beat_id == "notice_the_crack" and location == "salon":
            $ user_input = "inspect the cracked wedding portrait"

        "Ask what Malcolm nearly toasted" if facade_beat_id == "question_the_toast" and location == "salon":
            $ user_input = "ask what Malcolm was about to toast"

        "Question how rehearsed the argument feels" if facade_beat_id == "name_the_performance" and location == "salon":
            $ user_input = "this feels like a rehearsed performance"

        "Inspect the untouched glass at the bar" if facade_beat_id == "find_the_third_glass" and location == "salon":
            $ user_input = "inspect the bar and the untouched third glass"

        "Ask who the untouched glass was prepared for" if facade_beat_id == "press_the_absent_guest" and location == "kitchen":
            $ user_input = "ask who the untouched third glass was prepared for"

        "Read the paper caught in the desk drawer" if facade_beat_id == "enter_the_study" and location == "study":
            $ user_input = "open the study desk drawer and read the letter"

        "Ask what \"our best lie\" means" if facade_beat_id == "confront_the_lie" and location == "study":
            $ user_input = "ask whether Vivian was invented and what our best lie means"

        "Tell them the performance has to stop" if facade_beat_id == "choose_the_break" and location == "study":
            $ user_input = "stop this game and tell the truth"

        "Ask what they want without the performance" if facade_beat_id == "choose_the_break" and location == "study":
            $ user_input = "ask what they want now and whether they can forgive each other"

        "Ask what is behind the closed door" if facade_beat_id == "name_the_room" and location == "study":
            $ user_input = "ask about the closed door and the empty bedroom"

        "Say goodbye and leave quietly" if facade_beat_id == "quiet_exit" and location == "study":
            $ user_input = "say goodbye and leave"

        "Stay with them in the silence" if facade_beat_id == "quiet_exit" and location == "study":
            $ user_input = "sit and wait together in silence"

    $ facade_result = facade_dm.register_player_input(user_input, location)
    $ facade_note_progress(facade_result)

    if facade_result.get("callback"):
        $ renpy.call(facade_result["callback"])
    else:
        call facade_dynamic_reply(location) from _call_facade_dynamic_reply_shared
        call facade_maybe_nudge from _call_facade_maybe_nudge_shared

    $ _history_list = []
    return


label facade_dynamic_reply(location):
    $ reply_job = facade_start_reply_job(user_input, location, facade_dm)
    $ reply_waited = 0.0
    show screen thinking("Listening...")
    while reply_job is not None and not reply_job.done and reply_waited < FACADE_MODEL_WAIT_SECONDS:
        $ renpy.pause(FACADE_MODEL_POLL_SECONDS, hard=False)
        $ reply_waited += FACADE_MODEL_POLL_SECONDS
    hide screen thinking
    $ reply_speaker, reply_line = facade_reply_from_job(reply_job, location)
    if reply_speaker == "Malcolm":
        malcolm "[reply_line]"
    else:
        lila "[reply_line]"
    return


label facade_maybe_nudge:
    $ dm_nudge = facade_result.get("nudge", "")
    if dm_nudge:
        dm "[dm_nudge]"
    return


label facade_beat_greeted:
    show malcolm amused at right with dissolve
    lila "There. A civilized greeting. We remember civilization, don't we, Malcolm?"
    malcolm "I keep a little in the decanter for emergencies."
    return


label facade_beat_crack:
    play sound "audio/sfx/crystal_glass_tension.mp3"
    show lila wounded at left with dissolve
    dm "You look closer at the wedding portrait. The crack in the glass runs directly through Lila's mouth."
    lila "It happened years ago. Malcolm says replacing it would be sentimental."
    malcolm "I said replacing only the glass would be cowardice."
    return


label facade_to_act2:
    $ facade_act_title = facade_dm.current_act()["title"]
    show lila angry at left with dissolve
    show malcolm wounded at right with dissolve
    malcolm "To absent friends."
    lila "Do not."
    dm "The name Vivian hangs above the toast, unspoken and unmistakable."
    call facade_show_act_card(facade_act_title) from _call_facade_show_act2_card
    return


label facade_beat_performance:
    show lila angry at left with dissolve
    show malcolm amused at right with dissolve
    lila "A performance? No, dear. Performances end when the audience leaves."
    malcolm "Ours has admirable stamina."
    return


label facade_unlock_kitchen:
    if not facade_kitchen_known:
        $ facade_kitchen_known = True
        "(New room unlocked: Kitchen)"
    show malcolm wounded at right with dissolve
    malcolm "Fine. Look in the kitchen. Perhaps the glasses will give you the testimony we keep bungling."
    return


label facade_to_act3:
    $ facade_study_known = True
    $ facade_act_title = facade_dm.current_act()["title"]
    show lila wounded at left with dissolve
    lila "Vivian was invited every year."
    malcolm "Lila."
    lila "No, let our guest find the study. Let the house tell the story for once."
    "(New room unlocked: Study)"
    call facade_show_act_card(facade_act_title) from _call_facade_show_act3_card
    jump facade_study


label facade_beat_letter:
    play sound "audio/sfx/study_drawer_click.mp3"
    show lila wounded at left with dissolve
    dm "The drawer gives with a wooden click. The letter inside is addressed to nobody."
    dm "One sentence has been underlined until the paper nearly tears: Vivian is our best lie."
    return


label facade_beat_confrontation:
    show lila angry at left with dissolve
    show malcolm wounded at right with dissolve
    lila "Say it plainly. I want to hear whether it sounds monstrous in someone else's mouth."
    malcolm "Vivian was never born. There. The house is still standing."
    dm "The invented daughter has been audience, hostage, and altar."
    return


label facade_to_act4:
    $ facade_act_title = facade_dm.current_act()["title"]
    show lila wounded at left with dissolve
    show malcolm wounded at right with dissolve
    lila "If the game is over, what are we supposed to do with the rest of the night?"
    malcolm "Perhaps live through it without keeping score."
    call facade_show_act_card(facade_act_title) from _call_facade_show_act4_card
    return


label facade_beat_empty_room:
    show lila wounded at left with dissolve
    dm "They do not show you a nursery. They show you a closed door and the dust-free rectangle where a nameplate used to be."
    lila "It was easier to love her than to forgive each other."
    return


label facade_ending:
    hide screen facade_map_icon
    hide screen facade_director_icon
    hide screen facade_journal_icon
    scene bg facade street with dissolve
    dm "You leave after midnight. Behind you, no glass breaks."
    dm "For the first time all evening, the silence belongs to no one."
    "END OF THE GLASS HOUSE"
    $ persistent.facade_extra_act_unlocked = True
    $ renpy.save_persistent()
    "EXTRA ACT -1 UNLOCKED"
    $ MainMenu(confirm=False, save=False)()
