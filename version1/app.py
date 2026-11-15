"""AI Escape Room - Version 1. Run: streamlit run version1/app.py"""
import os
import streamlit as st                      # builds the web page
from dotenv import load_dotenv              # reads the .env file
from google import genai                    # Google's Gemini library
from google.genai import types
from prompts import ESCAPE_TOKEN, INTRO_TEXT, SYSTEM_PROMPT   # our game text

# --- 1. Settings: read key + model name from .env -------------------------
load_dotenv()
MODEL = os.getenv("GEMINI_MODEL")


@st.cache_resource          # create the connection once, not on every re-run
def get_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# --- 2. Talk to Gemini -----------------------------------------------------
def ask_game_master(history):
    """Send the rules + the WHOLE conversation. The LLM has no other memory."""
    contents = [types.Content(role=m["role"], parts=[types.Part(text=m["text"])])
                for m in history]
    response = get_client().models.generate_content(
        model=MODEL,
        contents=contents,                                  # the chat so far
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,               # the rules
            temperature=0.8))                               # 0 = strict, 1 = creative
    return response.text or "(silence...)"


# --- 3. The web page --------------------------------------------------------
st.set_page_config(page_title="AI Escape Room V1", page_icon="🔐")
st.title("🔐 AI Escape Room - Version 1")

# session_state survives Streamlit's re-runs: it stores the game
if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.escaped = False

if st.sidebar.button("🔄 Restart game"):
    st.session_state.history = []
    st.session_state.escaped = False
    st.rerun()

st.markdown(INTRO_TEXT)

# show every message so far
for m in st.session_state.history:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["text"].replace(ESCAPE_TOKEN, ""))

# --- 4. One turn of the game ------------------------------------------------
if st.session_state.escaped:
    st.success("🎉 You escaped! Press Restart to play again.")
elif text := st.chat_input("What do you do?"):
    st.session_state.history.append({"role": "user", "text": text})
    try:
        reply = ask_game_master(st.session_state.history)
    except Exception as e:
        reply = f"⚠️ Error: {e}"
    st.session_state.history.append({"role": "model", "text": reply})
    if ESCAPE_TOKEN in reply:       # we TRUST the LLM that the player escaped
        st.session_state.escaped = True
    st.rerun()
