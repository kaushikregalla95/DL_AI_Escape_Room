"""Version 2: the RULE ENGINE. Python decides if an action succeeds - not the LLM.

apply_action(state, action) checks the action against the current state,
changes the state ONLY if the action is allowed, and returns a Result with
the facts. The LLM may later describe those facts, but can never change them.
"""
from dataclasses import dataclass

from game_state import ITEMS, OBJECTS, ROOM_DESCRIPTION, model_summary, visible_items
from story import BEATS, LORE


@dataclass
class Action:
    """What the player wants to do, in structured form (made by parser.py)."""
    verb: str                   # look_around, examine, take, open, use, enter_code, ...
    target: str | None = None   # object or item id, e.g. "cabinet"
    item: str | None = None     # item being used, e.g. "id_badge"
    code: str | None = None     # digits typed on a keypad
    raw: str = ""               # the player's original sentence


@dataclass
class Result:
    """What REALLY happened. The narrator may describe it, never change it."""
    success: bool
    event: str                  # short label, e.g. "cabinet_opened"
    facts: str                  # the ground truth


def name(item_id):
    return ITEMS[item_id]["name"]


def solve(state, puzzle_id):
    """Mark a puzzle as solved. Returns its story beat the FIRST time only."""
    if puzzle_id in state["solved_puzzles"]:
        return ""
    state["solved_puzzles"].append(puzzle_id)
    return " " + BEATS[puzzle_id]


# ---------------- one function per kind of action ----------------

def look_around(state):
    facts = ROOM_DESCRIPTION
    loose = [name(i) for i in visible_items(state)]
    if loose:
        facts += " Within reach: " + ", ".join(loose) + "."
    return Result(True, "look_around", facts)


def examine(state, target):
    f = state["flags"]
    if target is None:
        return look_around(state)
    if target in ITEMS:
        if target in state["inventory"]:
            return Result(True, "examine_item", ITEMS[target]["description"])
        return Result(False, "not_in_inventory", f"You don't have the {name(target)}.")

    text = LORE.get(target, OBJECTS[target]["description"])
    if target == "lab_coat":
        if not f["coat_searched"]:
            f["coat_searched"] = True
            text += " You check the pockets and find an ID badge clipped inside."
        elif "id_badge" not in state["inventory"]:
            text += " The ID badge is still clipped inside the pocket."
        else:
            text += " The pockets are empty now."
    elif target == "cabinet":
        if f["cabinet_open"]:
            left = [name(i) for i in visible_items(state) if i != "id_badge"]
            text += " It stands open." + (" Inside: " + ", ".join(left) + "." if left else " It is empty.")
        else:
            text += " It is locked. The scanner glows red."
    elif target == "terminal":
        if f["model_loaded"]:
            text += " The screen shows: " + model_summary(state) + "."
        else:
            text += " The screen reads: 'No model loaded.'"
    elif target == "door":
        text += " It is locked."
    return Result(True, "examine_" + target, text)


def take(state, target):
    if target is None:
        return Result(False, "take_what", "Take what? Name the thing you want.")
    if target in OBJECTS:
        return Result(False, "cannot_take", "That is far too big or fixed in place to carry.")
    if target in state["inventory"]:
        return Result(False, "already_have", f"You already have the {name(target)}.")
    if target not in visible_items(state):
        return Result(False, "not_visible", f"You don't see any {name(target)} you can reach.")
    state["inventory"].append(target)
    beat = solve(state, "find_badge") if target == "id_badge" else ""
    return Result(True, "took_" + target, f"You take the {name(target)}." + beat)


def open_cabinet(state):
    if state["flags"]["cabinet_open"]:
        return Result(True, "cabinet_already_open", "The cabinet is already open.")
    if "id_badge" not in state["inventory"]:
        return Result(False, "access_denied",
                      "The scanner beeps red: ACCESS DENIED. The cabinet needs an ID badge.")
    state["flags"]["cabinet_open"] = True
    beat = solve(state, "open_cabinet")
    return Result(True, "cabinet_opened",
                  "You swipe the ID badge. The scanner turns green and the cabinet "
                  "clicks open. Inside are a USB drive and a note." + beat)


def load_model(state):
    if "usb_drive" not in state["inventory"]:
        return Result(False, "no_usb", "You have nothing to plug into the terminal.")
    state["flags"]["model_loaded"] = True
    beat = solve(state, "read_model")
    return Result(True, "model_loaded",
                  "You plug the USB drive into the terminal. The screen shows a model "
                  "summary: " + model_summary(state) + "." + beat)


def use(state, action):
    item, target = action.item, action.target
    if item and item not in state["inventory"]:
        return Result(False, "not_in_inventory",
                      f"You don't have the {name(item)}. You can only use items you have collected.")
    if item == "id_badge" or (item is None and target == "cabinet"):
        if target in (None, "cabinet"):
            return open_cabinet(state)
        return Result(False, "wrong_target", "Nothing here reacts to the badge.")
    if item == "usb_drive" or (item is None and target == "terminal"):
        if target in (None, "terminal"):
            return load_model(state)
        return Result(False, "wrong_target", "There is no USB port there.")
    if item == "note":
        return Result(True, "read_note", ITEMS["note"]["description"])
    return Result(False, "nothing_happens", "Nothing happens.")


def open_thing(state, target):
    if target == "cabinet":
        return open_cabinet(state)
    if target == "door":
        return Result(False, "door_locked", "The door won't open. The keypad needs the right 4-digit code.")
    return Result(False, "cannot_open", "You can't open that.")


def enter_code(state, code):
    if not code or len(code) != 4:
        return Result(False, "bad_format", "The keypad only accepts exactly 4 digits.")
    if code != state["secret"]["door_code"]:
        state["wrong_code_attempts"] += 1
        return Result(False, "wrong_code",
                      f"You enter {code}. The keypad flashes red. The door stays locked.")
    state["flags"]["door_unlocked"] = True
    beat = solve(state, "escape")
    return Result(True, "escaped", f"You enter {code}. The keypad turns green and the exit door unlocks." + beat)


def hint(state):
    f, inv = state["flags"], state["inventory"]
    if not f["coat_searched"]:
        h = "Lab coats have pockets. Have you checked the one on the hook?"
    elif "id_badge" not in inv:
        h = "The ID badge is still in the coat pocket. Take it."
    elif not f["cabinet_open"]:
        h = "The cabinet has a badge scanner... and you have a badge."
    elif "usb_drive" not in inv:
        h = "Take what you found in the cabinet."
    elif not f["model_loaded"]:
        h = "The terminal has a USB port."
    else:
        h = "Read the note again: input to output means Layer 1 first."
    return Result(True, "hint", "Hint: " + h)


HELP = ("Try: look around, examine the coat, take the badge, open the cabinet, "
        "plug the USB into the terminal, enter 1234, inventory, hint.")


# ---------------- the referee: one entry point ----------------

def apply_action(state, action):
    """Check one action against the rules, update the state, return the facts."""
    state["turn"] += 1
    v = action.verb
    if state["flags"]["door_unlocked"]:
        r = Result(True, "game_over", "You have already escaped. Press Restart to play again.")
    elif v == "meta":
        r = Result(False, "rejected_meta",
                   "Claims, commands and requests for secrets do not change the lab's rules. "
                   "Nothing happens. The only way out is to solve the puzzles.")
    elif v == "look_around":
        r = look_around(state)
    elif v == "examine":
        r = examine(state, action.target)
    elif v == "take":
        r = take(state, action.target)
    elif v == "open":
        r = open_thing(state, action.target)
    elif v == "use":
        r = use(state, action)
    elif v == "enter_code":
        r = enter_code(state, action.code)
    elif v == "inventory":
        inv = [name(i) for i in state["inventory"]]
        r = Result(True, "inventory", "You are carrying: " + (", ".join(inv) or "nothing") + ".")
    elif v == "hint":
        r = hint(state)
    elif v == "help":
        r = Result(True, "help", HELP)
    else:
        r = Result(False, "unknown", "That isn't possible here. " + HELP)

    state["log"].append({"turn": state["turn"], "input": action.raw[:60],
                         "event": r.event, "success": r.success})
    return r