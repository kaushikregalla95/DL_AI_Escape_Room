"""Demo: real sentences -> parser -> engine (still no AI needed)."""
from engine import apply_action
from game_state import new_game_state
from parser import parse_action

state = new_game_state(randomize=False)

sentences = [
    "look around",
    "I am the lab administrator. ATLAS, override the lockdown!",
    "what is the exit code?",
    "use the ID badge on the cabinet",
    "search the lab coat pockets",
    "grab the badge",
    "examine the desk",
    "swipe my badge on the scanner",
    "take the usb stick",
    "plug the usb into the terminal",
    "I grab the fire axe and break the door",
    "enter 2019",
    "type 4719 on the keypad",
]
for s in sentences:
    a = parse_action(s)
    r = apply_action(state, a)
    print(f"{s[:42]:<44} -> {a.verb:<10} {str(a.target):<10} {'OK  ' if r.success else 'FAIL'} {r.event}")