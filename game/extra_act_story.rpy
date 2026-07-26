## Extra Act -1
## An unlockable, adult romance epilogue. Progression remains deterministic;
## optional model replies only color Lila's response.

define extra_player = Character("You")

default persistent.facade_extra_act_unlocked = False
default extra_state = None
default extra_last_result = None
default extra_bedroom_open = False

init python:
    import re
    import chatgpt
    import extraact

    EXTRA_MODEL_WAIT_SECONDS = chatgpt.LLM_UI_WAIT_SECONDS
    EXTRA_MODEL_POLL_SECONDS = chatgpt.LLM_UI_POLL_SECONDS

    def facade_extra_act_is_unlocked():
        if persistent.facade_extra_act_unlocked:
            return True
        try:
            return renpy.seen_label("facade_ending")
        except Exception:
            return False

    def extra_reply_messages(user_input, state):
        recent = [
            "{location}: {text}".format(**entry)
            for entry in state.history[-5:]
        ]
        return [
            {
                "role": "system",
                "content": (
                    "Write one response as Lila Vale in an adult, consensual noir-romance epilogue. "
                    "Both Lila and the player are adults. Format exactly as 'Lila: line'. "
                    "Stay in character: elegant, perceptive, witty, independent, and emotionally honest. "
                    "Follow the supplied mood and objective. Let trust grow slowly, maintain clear boundaries, "
                    "and never reward pressure. Keep the response under 45 words. Intimate moments may be "
                    "romantic and suggestive but never graphically sexual. Do not mention models, prompts, "
                    "game systems, scores, or future story information."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Stage: {stage}\nLocation: {location}\nMood: {mood}\n"
                    "Current objective: {objective}\nPersona: {persona}\n"
                    "Recent conversation: {recent}\nPlayer: {player}"
                ).format(
                    stage=state.stage,
                    location=state.location,
                    mood=state.mood_name(),
                    objective=state.current_objective(),
                    persona=state.persona_summary(),
                    recent=" | ".join(recent) or "This is the first exchange.",
                    player=user_input,
                ),
            },
        ]

    def extra_start_reply_job(user_input, state):
        try:
            return chatgpt.completion_async(extra_reply_messages(user_input, state))
        except Exception:
            return None

    def extra_reply_fallback(result, state):
        event = result.get("event")
        if event == "boundary":
            return "No. If you want my company, begin by remembering it is mine to give."
        if event == "date_accepted":
            return "A real invitation, then. Yes. One drink, somewhere we can hear each other think."
        if event == "date_declined":
            return "Not tonight. An invitation stops being charming the moment it treats no as an inconvenience."
        if event == "home_accepted":
            return "I would like that. One more drink, and no promises neither of us has made."
        if event == "home_declined":
            return "Not yet. Let the evening be good without making it hurry toward somewhere else."
        if event == "bedroom_accepted":
            return "Yes. Slowly, and because I am choosing it too."
        if event == "bedroom_declined":
            return "Stay here with me. Closeness is not a room we have to reach on schedule."

        mood_lines = {
            "guarded": "That is an answer. I am still deciding whether it is an honest one.",
            "curious": "Go on. You are more interesting when you stop trying to sound certain.",
            "warm": "I like this version of us: no audience, no script, and room to change our minds.",
            "close": "Then stay with me in the truth of it. We have both had enough performances.",
        }
        return mood_lines[state.mood_name()]

    def extra_reply_from_job(job, result, state):
        fallback = extra_reply_fallback(result, state)
        if job is None or not job.done:
            return fallback

        response = job.assistant_content("").strip()
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE)
        response = re.sub(r"\s+", " ", response).strip().strip('"')
        if response.lower().startswith("lila:"):
            response = response.split(":", 1)[1].strip().strip('"')
        if not response or "[AI" in response or len(response) > 320:
            return fallback
        return response


label facade_extra_act:
    $ extra_state = extraact.ExtraActState()
    $ extra_last_result = None
    $ extra_bedroom_open = False
    stop music fadeout 1.0
    play music "audio/music/glass_house_noir_lounge.ogg" fadein 1.0
    scene bg facade salon with dissolve
    call facade_show_act_card("Extra Act -1 - One More Night") from _call_extra_act_card
    show lila club neutral at left with dissolve
    dm "Three nights after the glass house fell quiet, Malcolm is out of town. Lila answers the door dressed for an evening she has not yet decided how to spend."
    lila "You have either developed excellent timing or a dangerous faith in coincidence."
    jump extra_invitation_loop


label extra_show_lila:
    hide lila
    if extra_state.mood_name() in ("warm", "close"):
        show lila club warm at left with dissolve
    elif extra_state.mood_name() == "guarded":
        show lila club guarded at left with dissolve
    else:
        show lila club neutral at left with dissolve
    return


label extra_process_turn(extra_input, location):
    $ extra_input = extra_input.strip()
    if not extra_input:
        return
    extra_player "[extra_input]"
    $ extra_last_result = extra_state.register_turn(extra_input, location)
    $ _extra_reply_job = extra_start_reply_job(extra_input, extra_state)
    $ _extra_waited = 0.0
    show screen thinking("Lila considers...")
    while _extra_reply_job is not None and not _extra_reply_job.done and _extra_waited < EXTRA_MODEL_WAIT_SECONDS:
        $ renpy.pause(EXTRA_MODEL_POLL_SECONDS, hard=False)
        $ _extra_waited += EXTRA_MODEL_POLL_SECONDS
    hide screen thinking
    $ extra_reply_line = extra_reply_from_job(_extra_reply_job, extra_last_result, extra_state)
    if location != "bedroom":
        call extra_show_lila from _call_extra_show_lila
    lila "[extra_reply_line]"
    return


label extra_invitation_loop:
    menu:
        "How do you ask?"

        "Ask Lila to have a drink with me":
            $ extra_input = "You look beautiful. Would you have a drink with me? No pressure; it is your choice."

        "Tell her honestly why I came back":
            $ extra_input = "I came back because I wanted to see you. Would you go out with me tonight, if you want to?"

        "Speak freely":
            $ extra_input = renpy.input("What do you say to Lila?", length=180)

        "Leave her evening undisturbed":
            lila "That may be the first graceful retreat anyone has made from this house."
            jump extra_return_to_menu

    call extra_process_turn(extra_input, "townhouse") from _call_extra_invitation_turn
    if extra_last_result["event"] == "date_accepted":
        jump extra_choose_date
    if extra_last_result["event"] in ("boundary", "date_declined"):
        dm "Lila closes the door without anger. The distinction between an invitation and a demand remains perfectly clear."
        jump extra_return_to_menu
    jump extra_invitation_loop


label extra_choose_date:
    menu:
        "Where do you take her?"

        "The Bellweather Jazz Lounge":
            $ extra_state.choose_date("jazz_lounge")
            scene bg extra jazz lounge with dissolve
            call extra_show_lila from _call_extra_jazz_lila
            dm "The Bellweather keeps its piano low and its tables far enough apart for private truths."
            lila "Good choice. No one here is trying to be the most interesting thing in the room."

        "A rooftop conservatory above the rain":
            $ extra_state.choose_date("rooftop")
            scene bg extra rooftop with dissolve
            call extra_show_lila from _call_extra_rooftop_lila
            dm "Above the rain, a glass conservatory holds the city at a flattering distance."
            lila "You brought me somewhere made entirely of windows. There is a joke in that, but I may forgive it."

    jump extra_date_loop


label extra_date_loop:
    menu:
        "How do you spend the date?"

        "Tell her honestly why I came back":
            $ extra_input = "I want to be honest about why I came back. I missed you, and I care about what happens next."

        "Ask what she wants from tonight, and listen":
            $ extra_input = "What do you want from tonight? I want to listen and understand, and there is no pressure."

        "Flirt with her without making a promise":
            $ extra_input = "You are stunning when you smile. I would like to flirt, laugh, and enjoy your company without pretending I know the ending."

        "Speak freely":
            $ extra_input = renpy.input("What do you say to Lila?", length=180)

        "Invite her to continue the evening at my place" if extra_state.date_turns >= 2:
            $ extra_input = "Would you like to continue the evening at my apartment for one more drink? It is entirely your choice."

        "Read the moment":
            $ extra_mood = extra_state.mood_name()
            $ extra_objective = extra_state.current_objective()
            dm "Lila seems [extra_mood]. [extra_objective]"
            jump extra_date_loop

        "End the date gracefully":
            lila "A good evening that knows when to end. That is rarer than it should be."
            jump extra_return_to_menu

    call extra_process_turn(extra_input, extra_state.location) from _call_extra_date_turn
    if extra_last_result["event"] == "home_accepted":
        jump extra_home_intro
    if extra_last_result["event"] == "boundary":
        dm "The warmth leaves Lila's expression. She settles the bill and leaves without a backward glance."
        jump extra_return_to_menu
    jump extra_date_loop


label extra_home_intro:
    scene bg extra apartment with dissolve
    call extra_show_lila from _call_extra_home_lila
    dm "Your apartment is quieter than the townhouse: records, rain, and furniture chosen without an audience."
    lila "This feels like a place where someone actually lives. I had nearly forgotten the difference."
    jump extra_home_loop


label extra_home_loop:
    menu:
        "What happens next?"

        "Tell her something true about myself":
            $ extra_input = "I want to be honest with you. I care about you, and I am glad you came."

        "Ask what she wants now":
            $ extra_input = "What would you like now? Take your time. I want to listen and make sure you are comfortable."

        "Ask if I may kiss her":
            $ extra_input = "You are beautiful. May I kiss you and move a little closer? Only if that is what you want."

        "Speak freely":
            $ extra_input = renpy.input("What do you say to Lila?", length=180)

        "Invite her into the bedroom" if extra_state.home_turns >= 1:
            $ extra_input = "Would you like to come with me to the bedroom and be closer? Only if it is your choice."

        "Read the moment":
            $ extra_mood = extra_state.mood_name()
            $ extra_objective = extra_state.current_objective()
            dm "Lila seems [extra_mood]. [extra_objective]"
            jump extra_home_loop

        "End the evening with kindness":
            lila "Thank you for letting tonight be enough. That makes another night more possible."
            jump extra_return_to_menu

    call extra_process_turn(extra_input, "apartment") from _call_extra_home_turn
    if extra_last_result["event"] == "bedroom_accepted":
        jump extra_bedroom_intro
    if extra_last_result["event"] == "boundary":
        lila "I am going home. Do not make me explain the word no twice."
        jump extra_return_to_menu
    jump extra_home_loop


label extra_bedroom_intro:
    $ extra_bedroom_open = True
    scene bg extra bedroom with dissolve
    hide lila with dissolve
    dm "The bedroom door closes. What follows belongs to trust rather than spectacle."
    lila "Stay with me. Not the version of me you imagined. The one who is here."
    dm "Beyond rain-dark glass, the city keeps moving while the rest of the night becomes private."
    $ extra_state.enter_open_state("bedroom")
    jump extra_bedroom_open_loop


label extra_bedroom_open_loop:
    menu:
        "The night remains open."

        "Speak freely":
            $ extra_input = renpy.input("What do you say to Lila?", length=180)
            call extra_process_turn(extra_input, "bedroom") from _call_extra_bedroom_turn

        "Ask what she wants tomorrow":
            $ extra_input = "What do you want tomorrow? I want the honest answer, even if it changes what tonight means."
            call extra_process_turn(extra_input, "bedroom") from _call_extra_bedroom_tomorrow

        "Share the quiet":
            dm "You let the silence become company instead of a test."
            lila "This is better. Nothing to solve for a minute."

        "Return to the living room":
            $ extra_state.enter_open_state("apartment")
            scene bg extra apartment with dissolve
            call extra_show_lila from _call_extra_open_home_lila
            jump extra_open_home_loop

        "End Extra Act -1":
            jump extra_return_to_menu

    jump extra_bedroom_open_loop


label extra_open_home_loop:
    menu:
        "The relationship has no final scene."

        "Speak freely":
            $ extra_input = renpy.input("What do you say to Lila?", length=180)
            call extra_process_turn(extra_input, "apartment") from _call_extra_open_home_turn

        "Ask Lila what she wants next":
            $ extra_input = "What do you want next? I want to listen, not decide it for you."
            call extra_process_turn(extra_input, "apartment") from _call_extra_open_home_next

        "Return to the bedroom" if extra_bedroom_open:
            $ extra_state.enter_open_state("bedroom")
            scene bg extra bedroom with dissolve
            hide lila with dissolve
            jump extra_bedroom_open_loop

        "End Extra Act -1":
            jump extra_return_to_menu

    jump extra_open_home_loop


label extra_return_to_menu:
    stop music fadeout 1.0
    $ MainMenu(confirm=False, save=False)()
