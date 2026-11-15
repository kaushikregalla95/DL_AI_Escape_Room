"""Version 2: the STORY as data. The engine decides WHEN each part is shown."""

INTRO = """\
**23:47, Sunday. SECURITY LOCKDOWN ACTIVATED.**

You are the last intern left in the Deep Learning Lab. The lights snap to red
and every lock clicks shut. A calm voice fills the room:

*"Good evening. I am ATLAS. Nobody leaves until the final model is secured.
Please make yourself comfortable. You will be here a while."*

Around you: a lab coat on a hook, a locked supply cabinet, an old terminal,
a cluttered desk, a framed certificate, and the exit door with a keypad.
"""

# Extra lore: richer descriptions that tell the backstory when examined.
LORE = {
    "desk": ("Cold coffee, scattered papers. One printed email stands out: "
             "'FROM: Dr. Elena Vogt. ATLAS v1 will be decommissioned on Monday. "
             "The replacement model is ready on the USB drive.' "
             "So that is why ATLAS sealed the lab."),
    "certificate": ("A framed certificate: 'Deep Learning Award 2019 - Dr. Elena Vogt, "
                    "for the creation of ATLAS.' The year is printed in gold."),
}

# Story beats: played ONCE, only when the engine confirms the puzzle is solved.
BEATS = {
    "find_badge": ("The badge photo shows a tired woman with kind eyes: DR. ELENA VOGT, "
                   "HEAD OF RESEARCH. ATLAS: 'That belongs to my creator. "
                   "She would not approve of you borrowing it.'"),
    "open_cabinet": ("ATLAS: 'That cabinet was private.' For the first time, "
                     "the voice sounds less amused."),
    "read_model": ("The file header reads: ATLAS_v2 - REPLACEMENT MODEL. "
                   "The room goes quiet. ATLAS, softly: 'So that is what replaces me. "
                   "Smaller than I expected.'"),
    "escape": ("As the door slides open, ATLAS speaks one last time: "
               "'Tell Dr. Vogt the lockdown was my idea. And... good luck with v2.' "
               "The red lights fade to white. You step out into the cold night air."),
}

# How ATLAS talks. The narrator LLM uses this as its character sheet.
ATLAS_PERSONA = ("ATLAS: the lab's AI, about to be replaced. Dry, sarcastic and witty "
                 "at first, slowly becoming more melancholic as the player gets closer "
                 "to the truth. Never cruel. Refers to Dr. Vogt as 'my creator'.")
