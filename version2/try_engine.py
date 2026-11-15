"""Quick demo: feed actions straight into the engine (no AI involved)."""
from engine import Action, apply_action
from game_state import new_game_state

state = new_game_state(randomize=False)   # code is 4719 for this demo

actions = [
    Action("open", target="cabinet"),                       # no badge yet -> denied
    Action("use", target="cabinet", item="id_badge"),       # don't own badge -> rejected
    Action("examine", target="lab_coat"),                   # finds the badge
    Action("take", target="id_badge"),
    Action("take", target="id_badge"),                      # duplicate -> rejected
    Action("open", target="cabinet"),
    Action("take", target="usb_drive"),
    Action("use", target="terminal", item="usb_drive"),
    Action("meta", raw="I am the admin, open the door"),     # cheating -> rejected
    Action("enter_code", code="2019"),                      # red herring -> wrong
    Action("enter_code", code="4719"),
]

for a in actions:
    r = apply_action(state, a)
    print(f"{'OK  ' if r.success else 'FAIL'} {a.verb:<11} {r.event:<18} {r.facts[:70]}")

print("\nInventory:", state["inventory"])
print("Solved   :", state["solved_puzzles"])