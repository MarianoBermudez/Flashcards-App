from modules.utils import *


initialize_session_state()

st.set_page_config(page_title="Add", layout="centered", page_icon="📝")
st.title("📝 Add Flashcards")
st.write("")

with st.form("new_card_form_manage", clear_on_submit=True):
    word = st.text_input("Enter a word or expression", key="manage_q")
    submitted = st.form_submit_button("Add Card")
    
    if submitted and word:
        context = """You are a USA native english professor. Give me the back of a simple flashcard (use simple markdown). The first line of your response must be the word/expression (use '####'), then give the meaning/s of the following word/expression and a few diffrent examples For example, for the word 'court' your response should look like:
'#### court

A place where legal cases are heard, or the judicial body itself.
* The lawyer presented her arguments to the judge and jury in **court**.

An area specifically prepared and marked out for playing certain ball games, like tennis, basketball, or volleyball.
* We need to reserve the tennis **court** for an hour this afternoon.

To try to win the affection, support or attention of someone, often with romantic intentions. Example:
* In the old days, a gentleman would **court** a lady with gifts and visits before proposing marriage.
* The candidate is trying to **court** voters in swing states with promises of tax cuts.

To risk something, often something negative or undesirable.
* By not wearing a helmet, he was actively **courting** a serious injury.
* Her rebellious attitude always seemed to **court** controversy.'
Do not add redundant examples. The word/expression is: """
        response = askGemini(word, context)
        fm.add_new_card(word, response)
        st.session_state.last_card = {"front": word, "back": response}
    elif submitted:
        st.error("Please write a word or expression")

if st.session_state.last_card:
    st.write("")
    with st.container(border=True):
        _, col_text_back, col_speak_back = st.columns([0.001, 1, 0.1])
        with col_text_back:
            st.write(st.session_state.last_card["back"])
        with col_speak_back:
            speaker(st.session_state.last_card['front'])
        _, caption_col = st.columns([1, 0.15])
        caption_col.caption("Last card")


