import streamlit as st
from gtts import gTTS
import io
import base64
import random
import modules.flashcards_manager as fm
from modules.gemini_api import askGemini

def initialize_session_state():
    if "flashcards" not in st.session_state:
        print("initializing session state")
        st.session_state.flashcards = fm.load_all_cards()
        st.session_state.due_cards = fm.get_due_cards()
        st.session_state.current_index = 0
        st.session_state.show_answer = False
        st.session_state.view_mode = 'review'
        st.session_state.last_card = None
        st.session_state.card_to_edit = None
        st.session_state.tts = ""

def delete_flashcard_action(original_index):
    fm.delete_card_by_index(original_index)
    st.session_state.show_answer = False

def update_review_status_action(original_index, grade_string):
    fm.update_review_status(original_index, grade_string)
    st.session_state.show_answer = False
    st.session_state.current_index += 1

@st.fragment()
def speaker(word):
    st.button("🔊", key="speaker", on_click=lambda: st.session_state.update(tts=word), type="tertiary")
    with st.container(border=0,height=1):
        audio_placeholder = st.empty()
    speak(audio_placeholder, st.session_state.tts)
    st.session_state.tts = ""
    
def speak(placeholder, text_to_speak):
    """Generates audio from text and plays it automatically in a placeholder."""
    if text_to_speak:
        try:
            audio_bytes = io.BytesIO()
            tts = gTTS(text=text_to_speak, lang='en', slow=False)
            tts.write_to_fp(audio_bytes)
            
            audio_bytes.seek(0)
            audio_base64 = base64.b64encode(audio_bytes.read()).decode('utf-8')
            key = random.random()
            audio_html = f"""
                <audio autoplay style="display:none;" id="audio-{key}" onended="this.remove()">
                  <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """
            placeholder.markdown(audio_html, unsafe_allow_html=True)
            print("speaking")
        except Exception as e:
            st.error(f"Sorry, an error occurred during TTS: {e}")
