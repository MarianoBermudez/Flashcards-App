from modules.utils import st, initialize_session_state, delete_flashcard_action, refresh
from datetime import datetime


initialize_session_state()
refresh()

st.set_page_config(page_title="Manage Flashcards", layout="centered", page_icon="📚")
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
        original_index = item['original_index']
        
        with cols[col_index]:
            with st.expander(f"#### Card {original_index + 1}: {card['front']}"):
                st.markdown(f"**Answer:**\n> {card['back']}")
                
                review_date_dt = datetime.fromisoformat(card['next_review_date'])
                review_date_display = review_date_dt.strftime('%Y-%m-%d')
                
                st.markdown(f"**Next Review:** `{review_date_display}`")
                st.markdown(f"**Interval:** `{int(round(card['interval']))}` days")
                st.markdown(f"**EF:** `{card['easiness_factor']:.2f}`")
            
                st.button(
                    "Delete Card", 
                    key=f"delete_btn_{original_index}", 
                    on_click=delete_flashcard_action, 
                    args=(original_index,), 
                    type="secondary"
                )

        col_index = (col_index + 1) % 2
        
    st.caption(f"Total flashcards: {len(cards)}")

