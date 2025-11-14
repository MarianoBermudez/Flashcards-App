import streamlit as st
import google.generativeai as genai


def askGemini(prompt: str, context: str = "") -> str:
    """
    Generates content using the Gemini API, reading the API key from a specified file.

    Args:
        prompt: The text prompt to send to the Gemini model.
    Returns:
        The generated text response from the model, or an error message.
    """
    final_prompt = context + prompt
    api_key = st.secrets["GEMINI_API_KEY"]

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(final_prompt)
        return response.text

    except Exception as e:
        return f"An unexpected error occurred during content generation: {e}"