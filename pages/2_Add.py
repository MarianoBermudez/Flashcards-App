from modules.utils import st, askGemini, fm, initialize_session_state, refresh


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
    st.write(st.session_state.flashcards[-1]["card"]["back"])
    st.caption("Last card")
