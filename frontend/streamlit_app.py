import streamlit as st
import requests

# FastAPI endpoint
API_URL = "http://0.0.0.0:8000/agent"

st.title("Car Dealer Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask about car dealers offering test drives"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Prepare the payload for the API request
    payload = {
        "prompt": prompt,
        "model_service": "openai",
        "dealers_id": 1
    }

    try:
        # Make a request to the FastAPI backend
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the JSON response
        response_data = response.json()
        
        # Extract 'result' from the response if it exists
        assistant_response = response_data.get('result', 'No result found.')
    except requests.exceptions.RequestException as e:
        assistant_response = f"Error: Unable to reach the server. Details: {str(e)}"
    except ValueError as e:
        assistant_response = f"Error: Invalid response from server. Details: {str(e)}"

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    # Optionally, display raw API response for debugging
    with st.expander("Debug: Raw API Response"):
        st.write(response.text if 'response' in locals() else "No response received")
