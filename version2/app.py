"""AI Escape Room - Version 2 (reliable). Run: streamlit run version2/app.py

Every turn:  sentence -> parser -> Action -> engine (Python rules) -> Result
             -> narrator (Gemini as ATLAS, checked by a guard) -> reply
"""
import json
import os

import streamlit as st
from dotenv import load_dotenv

from engine import apply_action
from game_state import ITEMS, PUZZLES, new_game_state, public_view
from narrator import narrate
from parser import parse_action
from story import INTRO

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL")


@st.cache_resource
def get_client():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None             # the game still works, just without AI narration
    from google import genai
    return genai.Client(api_key=key)


def reset_game():
    st.session_state.state = new_game_state()     # new random code every game
    st.session_state.chat = []


st.set_page_config(page_title="AI Escape Room V2", page_icon="🔐")
st.title("🔐 AI Escape Room - Version 2")
st.caption("Python enforces the rules. ATLAS only tells the story.")

if "state" not in st.session_state:
    reset_game()
state = st.session_state.state
client = get_client()

# ---------- sidebar: the player can SEE the real game state ----------
with st.sidebar:
    st.header("Inventory")
    inv = [ITEMS[i]["name"] for i in state["inventory"]]
    st.write(", ".join(inv) if inv else "(empty)")

    st.header("Progress")
    for pid, label in PUZZLES.items():
        st.write(("✅ " if pid in state["solved_puzzles"] else "⬜ ") + label)

    st.header("Exit door")
    st.write("UNLOCKED" if state["flags"]["door_unlocked"] else "Locked")
    st.write(f"Wrong codes tried: {state['wrong_code_attempts']}")

    if st.button("Restart game", use_container_width=True):
        reset_game()
        st.rerun()
    if client is None:
        st.warning("No GEMINI_API_KEY: running without AI narration.")
    with st.expander("Debug: game state (secrets hidden)"):
        st.code(json.dumps(public_view(state), indent=2), language="json")

# ---------- the chat ----------
st.markdown(INTRO)
for role, text in st.session_state.chat:
    with st.chat_message(role):
        st.markdown(text)

if state["flags"]["door_unlocked"]:
    st.success("You escaped the lab! Press Restart to play again.")
elif text := st.chat_input("What do you do?"):
    action = parse_action(text, client, MODEL)           # 1. understand
    result = apply_action(state, action)                 # 2. decide (Python)
    reply, _ = narrate(text, result, public_view(state), client, MODEL)   # 3. tell
    st.session_state.chat.append(("user", text))
    st.session_state.chat.append(("assistant", reply))
    st.rerun()
    