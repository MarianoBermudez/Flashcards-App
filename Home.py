from modules.utils import * 
# streamlit run .\Home.py

def main():
    st.set_page_config(page_title="English Flashcards Generator", layout="centered", page_icon="🧠")
    initialize_session_state()
    
    st.title("🧠 English Flashcards Generator")
    st.write("")
    st.write("")

    col_review, col_add, col_manage = st.columns(3)

    with col_review:
        if st.button("Review", width='stretch'):
            st.session_state.review_index = 0
            st.session_state.show_answer = False
            st.switch_page("pages/1_Review.py")

    with col_add:
        if st.button("Add", use_container_width=True):
            st.switch_page("pages/2_Add.py")

    with col_manage:
        if st.button("Manage", use_container_width=True):
            st.switch_page("pages/3_Manage.py")

    st.divider()

if __name__ == '__main__':
    main()

