import streamlit as st
import google as genai


def askGemini(prompt: str, context: str = "", key_file_path: str = "gemini_api_key.txt") -> str:
    """
    Generates content using the Gemini API, reading the API key from a specified file.

    Args:
        prompt: The text prompt to send to the Gemini model.
        key_file_path: The path to the file containing the API key.

    Returns:
        The generated text response from the model, or an error message.
    """
    final_prompt = context + prompt

    # 1. Read API Key from File
    api_key = st.secrets["GEMINI_API_KEY"]

    # 2. Initialize the Gemini Client
    try:
        # Pass the key explicitly during client initialization
        client = genai.Client(api_key=api_key)
    except Exception as e:
        return f"Error initializing Gemini client: {e}"

    # 3. Generate Content
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=final_prompt
        )
        return response.text
    except Exception as e:
        return f"An unexpected error occurred during content generation: {e}"