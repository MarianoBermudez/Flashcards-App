from modules.utils import *
from datetime import datetime

initialize_session_state()
st.session_state.flashcards = fm.load_all_cards()

st.set_page_config(page_title="Manage ", layout="centered", page_icon="📚")
st.title("📚 Manage Flashcards")
st.write("")

cards = st.session_state.flashcards
if not cards:
    st.info("No flashcards added yet.")
else:
    cols = st.columns(2)
    col_index = 0

    for item in cards:
        card = item['card']
        card_index = item['card_index']
        
        with cols[col_index]:
            
            if st.session_state.card_to_edit == card_index:
                
                with st.expander(f"#### Editing Card {card_index + 1}...", expanded=True):
                    with st.form(key=f"edit_form_{card_index}"):
                        st.caption("Modify the fields and save.")
                        new_front = st.text_input("Front", value=card['front'])
                        new_back = st.text_area("Back", value=card['back'], height=600)

                        col_save, _, col_cancel = st.columns(3)
                        
                        with col_save:
                            if st.form_submit_button("Save", type="primary"):
                                fm.update_card_by_index(card_index, new_front, new_back)
                                st.session_state.card_to_edit = None
                                st.rerun() 
                        
                        with col_cancel:
                            if st.form_submit_button("Cancel"):
                                st.session_state.card_to_edit = None 
                                st.rerun() 

            else:
                with st.expander(f"#### Card {card_index + 1}: {card['front']}"):
                    st.markdown(f"**Answer:**\n> {card['back']}")
                    
                    review_date_dt = datetime.fromisoformat(card['next_review_date'])
                    review_date_display = review_date_dt.strftime('%Y-%m-%d')
                    
                    st.markdown(f"**Next Review:** `{review_date_display}`")
                    st.markdown(f"**Interval:** `{int(round(card['interval']))}` days")
                    st.markdown(f"**EF:** `{card['easiness_factor']:.2f}`")
                    st.write("") 
                    
                    col_edit, _, col_delete = st.columns([1, 3, 1])
                    
                    with col_edit:
                        st.button(
                            "✏️", 
                            key=f"edit_btn_{card_index}",
                            on_click=lambda idx=card_index: st.session_state.update(card_to_edit=idx)
                        )

                    with col_delete:
                        st.button(
                            "❌", 
                            key=f"delete_btn_{card_index}", 
                            on_click=delete_flashcard_action, 
                            args=(card_index,)
                        )

        col_index = (col_index + 1) % 2
        
    st.caption(f"Total flashcards: {len(cards)}")