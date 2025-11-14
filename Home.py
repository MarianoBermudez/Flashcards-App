from modules.utils import * 
import pandas as pd
import plotly.express as px  
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


# --- Page Setup ---
st.set_page_config(page_title="Your Stats", layout="wide", page_icon="📊")
st.title("📊 Your Stats")


# --- Data Loading and Guardrail ---
all_cards = st.session_state.flashcards

if not all_cards:
    st.info("You don't have any flashcards yet. Add some cards to see your stats!")
    st.stop()

# --- Data Processing ---
try:
    processed_data = []
    for item in all_cards:
        card_data = item['card']
        processed_data.append({
            "front": card_data.get('front', 'N/A'),
            "next_review_date": card_data.get('next_review_date'),
            "interval": card_data.get('interval', 0),
            "easiness": card_data.get('easiness', 2.5)
        })

    df = pd.DataFrame(processed_data)
    df['next_review_date'] = pd.to_datetime(df['next_review_date'], errors='coerce')
    df = df.dropna(subset=['next_review_date'])
    df['next_review_date'] = df['next_review_date'].dt.tz_localize(None)

except KeyError as e:
    st.error(f"Could not process your card data. It seems to be missing a key: {e}")
    st.error("This stats page assumes your cards have 'next_review_date', 'interval', and 'easiness' properties.")
    st.stop()
except Exception as e:
    st.error(f"An unexpected error occurred while processing your data: {e}")
    st.stop()


# --- 1. Key Metrics (KPIs) ---
st.subheader("At a Glance")

mature_card_count = len(df[df['interval'] >= 21])
total_card_count = len(df)
due_today_count = len(st.session_state.due_cards)

col1, col2, col3 = st.columns(3)
col1.metric("Total Cards", f"{total_card_count}")
col2.metric("Due Today", f"{due_today_count}")
col3.metric("Mature Cards", f"{mature_card_count}")


# --- 2. Review Forecast (Plotly) ---
today = pd.to_datetime('today').normalize()
next_30_days = pd.date_range(start=today, periods=30)

df_due = df[df['next_review_date'] >= today]

due_counts = df_due.groupby(df_due['next_review_date'].dt.date).size().reset_index(name='Cards Due')
due_counts = due_counts.set_index('next_review_date')

due_forecast = due_counts.reindex(next_30_days.date, fill_value=0)
due_forecast.index.name = "Date"

# --- NEW PLOT CODE (Plotly) ---

# Reset index to make 'Date' a column for Plotly
chart_data = due_forecast.reset_index()

# Create the interactive bar chart using Plotly Express
fig = px.bar(
    chart_data,
    x='Date',
    y='Cards Due',
    title="Review Forecast (Next 30 Days)",
    labels={'Cards Due': 'Number of Cards Due', 'Date': 'Date'}, # Clean up axis labels
    template='plotly_white' # Use a clean, minimal theme
)

# Customize the hover information for clarity
fig.update_traces(
    hovertemplate="<b>%{x|%A, %b %d}</b><br>Cards Due: %{y}<extra></extra>"
)

# Customize the x-axis to show the date format we want (e.g., "Oct 23")
fig.update_xaxes(
    tickformat="%b %d"
)

# Display the interactive Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)