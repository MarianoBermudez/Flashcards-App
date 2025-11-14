from modules.utils import *


initialize_session_state()
st.session_state.flashcards = fm.load_all_cards()

st.set_page_config(page_title="Review", layout="centered", page_icon="✨")
st.title("✨ Review Flashcards")
st.write("")

due_cards = st.session_state.due_cards
num_cards = len(due_cards)
current_index = st.session_state.current_index

if not due_cards:
    st.info("The deck is empty or no cards are due for review.")

elif current_index >= num_cards:
    st.success("🎉 You've reviewed all available cards for now!")
    st.balloons()
    
else:
    current_card_data = due_cards[current_index]['card']
    card_index = due_cards[current_index]['card_index']

    if not st.session_state.show_answer:
        with st.container(border=True):
            _ ,col_text, col_speak = st.columns([0.001, 1, 0.1])
            with col_text:
                st.write(f"#### {current_card_data['front']}")
            with col_speak:
                speaker(current_card_data['front'])

        st.button(
            "Reveal Answer", 
            key="reveal_answer_btn", 
            type="secondary",
            use_container_width=True,
            on_click=lambda: st.session_state.update(show_answer=True))

    else:
        with st.container(border=True):
            _, col_text_back, col_speak_back = st.columns([0.001, 1, 0.1])
            with col_text_back:
                st.markdown(current_card_data['back'])
            with col_speak_back:
                speaker(current_card_data['front'])

            _, caption_col = st.columns([1, 0.1])
            caption_col.caption(f"{current_index + 1} / {num_cards}")

        col0, col1, col2, col3 = st.columns(4)

        col0.button("Again", key="again_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Again",))
            
        col1.button("Hard", key="hard_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Hard",))
            
        col2.button("Good", key="good_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Good",))

        col3.button("Easy", key="easy_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Easy",))




