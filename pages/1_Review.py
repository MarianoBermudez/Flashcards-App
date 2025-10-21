import streamlit as st
from modules.utils import *


initialize_session_state()


st.set_page_config(page_title="Review Flashcards", layout="centered", page_icon="✨")
st.title("✨ Review Flashcards")
st.write("")

due_cards = st.session_state.due_cards
num_cards = len(due_cards)
current_index = st.session_state.current_index

if not due_cards:
    st.info("The deck is empty or no cards are due for review!")

elif current_index >= num_cards:
    st.success("🎉 You've reviewed all available cards for now! Come back later.")

else:
    current_card_data = due_cards[current_index]['card']
    card_index = due_cards[current_index]['card_index']

    if not st.session_state.show_answer:
        with st.container(border=True):
            col_text, col_speak = st.columns([1.4, 0.1])
            with col_text:
                st.write(f"#### {current_card_data['front']}")
            with col_speak:
                st.button("🔊", key="speak_front", on_click=lambda: st.session_state.update(tts=current_card_data['front']), type="tertiary")
        
        st.button(
            "Reveal Answer", 
            key="reveal_answer_btn", 
            type="secondary",
            use_container_width=True,
            on_click=lambda: st.session_state.update(show_answer=True))

    else:
        with st.container(border=True):
            col_text_back, col_speak_back = st.columns([1.4, 0.1])
            with col_text_back:
                st.markdown(current_card_data['back'])
            with col_speak_back:
                st.button("🔊", key="speak_back", on_click=lambda: st.session_state.update(tts=current_card_data['front']), type="tertiary")

            st.caption(f"{current_index + 1} / {num_cards}")

        col0, col1, col2, col3 = st.columns(4)

        col0.button("Again", key="again_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Again",))
            
        col1.button("Hard", key="hard_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Hard",))
            
        col2.button("Good", key="good_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Good",))

        col3.button("Easy", key="easy_btn", type="secondary", use_container_width=True,
            on_click=update_review_status_action, args=(card_index, "Easy",))


audio_placeholder = st.empty()
speak(audio_placeholder, st.session_state.tts)

