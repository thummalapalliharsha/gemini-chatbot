import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

from langfuse import get_client
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor


# Load environment variables
load_dotenv()


# -----------------------------
# Langfuse
# -----------------------------

langfuse = get_client()

if not langfuse.auth_check():
    st.error("Langfuse authentication failed. Check your .env keys.")
    st.stop()

GoogleGenAIInstrumentor().instrument()


# -----------------------------
# Gemini
# -----------------------------

gemini = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------
# Streamlit
# -----------------------------

st.set_page_config(
    page_title="Gemini Chatbot",
    page_icon="🤖"
)

st.title("🤖 Gemini Chatbot")
st.caption("Gemini + Langfuse")


# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display history
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# User input
if prompt := st.chat_input("Ask me anything..."):

    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })


    # Build conversation
    conversation = ""

    for message in st.session_state.messages:
        conversation += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )


    # Gemini
    response = gemini.models.generate_content(
        model="gemini-3.5-flash",
        contents=conversation
    )

    answer = response.text


    # Show response
    with st.chat_message("assistant"):
        st.markdown(answer)


    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


    # Send traces to Langfuse
    langfuse.flush()