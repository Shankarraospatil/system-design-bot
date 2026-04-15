import os
import time

import streamlit as st
from google import genai
from google.genai import types

# --- CONFIGURATION ---
GOOGLE_API_KEY = "AIzaSyArV7XYXmLtPwIGWwvHfev5iQGggar2tNs"
PDF_PATH = "system_design_book.pdf"
PREFERRED_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]

if not GOOGLE_API_KEY:
    st.error("Missing GOOGLE_API_KEY. Add it to .env or Streamlit secrets.")
    st.stop()
if GOOGLE_API_KEY.strip() in ("", "PASTE_YOUR_GOOGLE_API_KEY_HERE"):
    st.error("Set GOOGLE_API_KEY directly in app.py before running the app.")
    st.stop()

# Initialize client
client = genai.Client(api_key=GOOGLE_API_KEY)

st.set_page_config(
    page_title="System Design Expert",
    page_icon="SD",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_custom_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f3f7ff 0%, #edf3ff 100%);
            color: #0f172a;
        }
        .block-container {
            padding-top: 3.2rem;
            padding-bottom: 6rem;
            max-width: 920px;
        }
        .topbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            background: #ffffff;
            border: 1px solid #d7e4fb;
            border-radius: 14px;
            padding: 0.8rem 1rem;
            margin-bottom: 0.9rem;
            box-shadow: 0 8px 18px rgba(13, 44, 86, 0.06);
        }
        .brand {
            font-size: 1.05rem;
            font-weight: 700;
            color: #123b73;
        }
        .chips {
            display: flex;
            align-items: center;
            gap: 0.45rem;
            flex-wrap: wrap;
        }
        .chip {
            font-size: 0.78rem;
            font-weight: 600;
            color: #113968;
            background: #eaf1ff;
            border: 1px solid #c7dbff;
            padding: 0.2rem 0.5rem;
            border-radius: 999px;
        }
        .status-ok {
            color: #0f5132;
            background: #dcfce7;
            border-color: #bbf7d0;
        }
        .status-bad {
            color: #7f1d1d;
            background: #fee2e2;
            border-color: #fecaca;
        }
        [data-testid="stChatMessage"] {
            border-radius: 16px;
            padding: 0.72rem 0.95rem;
            border: 1px solid #dbe8f9;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 12px rgba(15, 34, 66, 0.06);
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background: #1f6feb;
            border-color: #1f6feb;
            margin-left: 12%;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background: #ffffff;
            margin-right: 12%;
        }
        [data-testid="stChatMessage"] *,
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] span,
        [data-testid="stChatMessage"] div {
            color: #0f172a !important;
        }
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) *,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) li,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) span,
        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) div {
            color: #ffffff !important;
        }
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] strong,
        [data-testid="stMarkdownContainer"] code {
            color: #0f172a !important;
        }
        [data-testid="stChatInput"] {
            background: #ffffff !important;
            border: 1px solid #c9ddf7 !important;
            border-radius: 14px !important;
        }
        [data-testid="stChatInput"] > div {
            background: #ffffff !important;
            border-radius: 14px !important;
        }
        [data-testid="stChatInput"] textarea {
            color: #0f172a !important;
            caret-color: #0f172a !important;
            background: #ffffff !important;
        }
        [data-testid="stChatInput"] textarea::placeholder {
            color: #64748b !important;
            opacity: 1 !important;
        }
        div[data-testid="stButton"] > button {
            background: #1f6feb !important;
            color: #ffffff !important;
            border: 1px solid #1f6feb !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
        }
        div[data-testid="stButton"] > button:hover {
            background: #165ac2 !important;
            border-color: #165ac2 !important;
            color: #ffffff !important;
        }
        div[data-testid="stButton"] > button:focus {
            box-shadow: 0 0 0 0.2rem rgba(31, 111, 235, 0.25) !important;
            color: #ffffff !important;
        }
        .stSpinner > div,
        .stInfo, .stSuccess, .stError {
            color: #0f172a !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_styles()


@st.cache_resource
def pick_supported_model() -> str:
    """Pick a supported generateContent model dynamically to avoid 404s."""
    try:
        available = []
        for model in client.models.list():
            actions = getattr(model, "supported_actions", None) or []
            if "generateContent" in actions:
                name = getattr(model, "name", "")
                if name.startswith("models/"):
                    name = name.split("/", 1)[1]
                if name:
                    available.append(name)

        if not available:
            return "gemini-2.5-flash"

        for candidate in [m for m in PREFERRED_MODELS if m]:
            if candidate in available:
                return candidate

        for name in available:
            if "flash" in name:
                return name

        return available[0]
    except Exception:
        return "gemini-2.5-flash"


@st.cache_resource
def prepare_book_context(path: str):
    if not os.path.exists(path):
        st.error(f"PDF not found! Please ensure '{path}' is in the folder.")
        return None

    try:
        book_file = client.files.upload(file=path)

        while book_file.state.name == "PROCESSING":
            time.sleep(2)
            book_file = client.files.get(name=book_file.name)

        if book_file.state.name == "FAILED":
            st.error("Google servers failed to process this PDF.")
            return None

        return book_file
    except Exception as e:
        st.error(f"Upload failed: {str(e)}")
        return None


file_context = prepare_book_context(PDF_PATH)
MODEL_NAME = pick_supported_model()
CONTEXT_READY = file_context is not None

context_chip_class = "status-ok" if CONTEXT_READY else "status-bad"
context_text = "Context Ready" if CONTEXT_READY else "Context Missing"
st.markdown(
    f"""
    <div class="topbar">
      <div class="brand">System Design Architect Bot</div>
      <div class="chips">
        <span class="chip">Model: {MODEL_NAME}</span>
        <span class="chip {context_chip_class}">{context_text}</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

controls_col1, controls_col2 = st.columns([3, 1])
with controls_col1:
    temperature = st.slider("Response precision", min_value=0.0, max_value=1.0, value=0.1, step=0.1)
with controls_col2:
    st.write("")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

expert_instruction = (
    "You are a specialized System Design Expert. Your knowledge is based on the attached book. "
    "Use the content of the book to answer software architecture and scalability questions. "
    "CRITICAL RULE: If a user asks a question unrelated to system design, architecture, or tech "
    "(like sports, food, or general chat), you MUST say: 'I am a System Design Expert. "
    "Please ask me questions related to system architecture.'"
)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about high-level design or scalability..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing architecture..."):
            if file_context:
                try:
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=[file_context, prompt],
                        config=types.GenerateContentConfig(
                            system_instruction=expert_instruction,
                            temperature=temperature,
                        ),
                    )
                    answer = response.text
                except Exception as e:
                    answer = f"Connection error with model '{MODEL_NAME}': {str(e)}"
            else:
                answer = "System error: The PDF context could not be loaded."

            st.markdown(answer)
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
