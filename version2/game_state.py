"""Version 2: the game's TRUTH lives here, in Python - not in the LLM."""
import random

ROOM_DESCRIPTION = (
    "The Deep Learning Lab is bathed in red emergency light. You see a lab coat "
    "on a hook, a locked supply cabinet with a badge scanner, an old computer "
    "terminal, a cluttered desk, a framed certificate on the wall, and the exit "
    "door with a 4-digit keypad."
)

# Fixed things in the room. "aliases" = words a player might use for them.
OBJECTS = {
    "lab_coat":    {"aliases": ["lab coat", "coat", "pocket", "pockets", "hook"],
                    "description": "A white lab coat hanging on a hook."},
    "cabinet":     {"aliases": ["supply cabinet", "cabinet", "badge scanner", "scanner", "locker"],
                    "description": "A steel supply cabinet with a badge scanner."},
    "terminal":    {"aliases": ["terminal", "computer", "screen", "monitor", "usb port", "port", "pc"],
                    "description": "An old computer terminal with a USB port."},
    "desk":        {"aliases": ["desk", "table", "coffee", "papers", "mug"],
                    "description": "A cluttered desk with cold coffee and old papers."},
    "certificate": {"aliases": ["certificate", "award", "frame", "wall"],
                    "description": "A framed certificate: 'Deep Learning Award 2019'."},
    "door":        {"aliases": ["exit door", "door", "exit", "keypad"],
                    "description": "The exit door, sealed. A keypad waits for a 4-digit code."},
}

# Things the player can pick up and carry.
ITEMS = {
    "id_badge":  {"name": "ID badge", "aliases": ["id badge", "id card", "keycard", "badge", "card"],
                  "description": "A lab ID badge with a magnetic stripe."},
    "usb_drive": {"name": "USB drive", "aliases": ["usb drive", "usb stick", "usb", "drive", "stick"],
                  "description": "A small USB drive labelled 'final_model'."},
    "note":      {"name": "note", "aliases": ["note", "paper note", "message"],
                  "description": "A handwritten note: 'Read the layers from input to output.'"},
}

PUZZLES = {"find_badge": "Find the ID badge",
           "open_cabinet": "Open the supply cabinet",
           "read_model": "Read the model summary",
           "escape": "Unlock the exit door"}


def new_game_state(randomize=True, seed=None):
    """Create a fresh game. The exit code is random each game (digits 1-9)."""
    if randomize:
        rng = random.Random(seed)
        code = "".join(str(rng.randint(1, 9)) for _ in range(4))
    else:
        code = "4719"                      # fixed code, used by the tests
    return {
        "secret": {"door_code": code},     # NEVER sent to the LLM
        "flags": {"coat_searched": False, "cabinet_open": False,
                  "model_loaded": False, "door_unlocked": False},
        "inventory": [],
        "solved_puzzles": [],
        "wrong_code_attempts": 0,
        "turn": 0,
        "log": [],
    }


def visible_items(state):
    """Items lying in the room that the player can pick up right now."""
    items = []
    if state["flags"]["coat_searched"]:
        items.append("id_badge")
    if state["flags"]["cabinet_open"]:
        items += ["usb_drive", "note"]
    return [i for i in items if i not in state["inventory"]]


def model_summary(state):
    """What the terminal shows: layer sizes = code digits, listed OUT of order."""
    c = state["secret"]["door_code"]
    return (f"Layer 3: {c[2]} neurons, Layer 1: {c[0]} neurons, "
            f"Layer 4: {c[3]} neurons, Layer 2: {c[1]} neurons")


def public_view(state):
    """The state WITHOUT secrets - safe to show the player or send to the LLM."""
    return {k: v for k, v in state.items() if k != "secret"}
