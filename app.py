import streamlit as st
from datetime import datetime
import requests


def display_history() -> None:
    """Display the chat history in the app"""
    for message in st.session_state.chat_history:
        if message["type"] == "userMessage":
            with st.chat_message("user"):
                st.write(message["message"])
        elif message["type"] == "apiMessage":
            with st.chat_message("assistant"):
                st.write(message["message"])


# Function to interact with the API
def query(payload) -> dict:
    """Send a query to the Flowise API and return the response"""
    if st.session_state["flowise_url"] is None:
        st.error(
            "Please enter a valid Flowise URL. [See docs](https://docs.flowiseai.com/how-to-use)"
        )
        st.stop()
    st.session_state.chat_history.append(
        {"type": "userMessage", "message": user_message}
    )
    with st.spinner("AI is writing..."):
        try:
            response = requests.post(st.session_state["flowise_url"], json=payload)
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not connect to Flowise. Please check your URL and try again."
            )
            st.stop()

    if type(response.json()) == str:
        response_text = response.json()
    response_text = response.json()["text"]

    st.session_state.chat_history.append(
        {"type": "apiMessage", "message": response_text}
    )
    display_history()
    return response_text


st.title("Flowise Streamlit App")

if "flowise_url" not in st.session_state:
    st.session_state["flowise_url"] = None

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "override_config" not in st.session_state:
    st.session_state["override_config"] = {}

with st.sidebar:
    st.session_state["flowise_url"] = st.text_input(
        "Flowise URL", value=st.session_state["flowise_url"]
    )
    st.session_state["override_config"] = st.text_area(
        "Override Config",
        value="{}",
        height=200,
        help="[See docs](https://docs.flowiseai.com/how-to-use#api)",
    )

# Create chat input
user_message = st.chat_input("Type a message...")

# If user sends a message, append it to chat history and interact with the API
if user_message:
    # Keep only the most recent 5 messages in the history when sending to the API
    payload = {
        "question": f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{user_message}",
        "history": st.session_state.chat_history[-4:],
        "overrideConfig": {"returnSourceDocuments": True},
    }
    query(payload)
