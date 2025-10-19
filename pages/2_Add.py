from modules.utils import *


initialize_session_state()

st.set_page_config(page_title="Add Flashcards", layout="centered", page_icon="📝")
st.title("📝 Add Flashcards")
st.write("")

with st.form("new_card_form_manage", clear_on_submit=True):
    word = st.text_input("Enter a word or expression", key="manage_q")
    submitted = st.form_submit_button("Add Card")
    
    if submitted and word:
        context = "You are a USA native english professor. Give me the back of a simple flashcard (use simple markdown). The first line of your response must be the word/expression (use '####'), then give the meaning/s of the following word/expression and a few diffrent examples The word/expression is: "
        fm.add_new_card(word, askGemini(word, context))
        refresh()
    elif submitted:
        st.error("Please write a word or expression")

st.write("")

with st.container(border=True):
    
    col_text, col_speak = st.columns([1, 0.1])
    with col_text:
        st.write(st.session_state.flashcards[-1]["card"]["back"])
    with col_speak:
        st.button("🔊", key="speak_front", on_click=lambda: st.session_state.update(tts=st.session_state.flashcards[-1]["card"]["front"]))
    st.caption("Last card")


audio_placeholder = st.empty()
speak(audio_placeholder, st.session_state.tts)

