import streamlit as st
import requests

# FastAPI endpoint
API_URL = "http://0.0.0.0:8000/agent"

st.set_page_config(layout="wide")

# Create two columns: one for the sidebar and one for the main content
sidebar, main_content = st.columns([1, 3])

# Sidebar inputs
with sidebar:
    st.header("Settings")
    
    model_service = st.selectbox(
        "Model Service",
        ["openai", "groq", "ollama"],
        key="model_service"
    )
    
    if model_service == "openai":
        model_name = st.selectbox("Model Name", ["gpt-3.5-turbo"], key="model_name")
    elif model_service == "groq":
        model_name = st.selectbox(
            "Model Name", 
            ["qwen-2.5-32b", "deepseek-r1-distill-qwen-32b", "deepseek-r1-distill-llama-70b-specdec", "llama-3.3-70b-specdec"],
            key="model_name"
        )
    else:  # ollama
        model_name = st.selectbox("Model Name", ["deepseek-r1", "llama3.3", "phi4"], key="model_name")
    
    dealers_id = st.number_input("Dealers ID", min_value=1, value=1, step=1, key="dealers_id")
    lead_id = st.number_input("Lead ID", min_value=1, value=1, step=1, key="lead_id")
    lead_crm_id = st.number_input("Lead CRM ID", min_value=1, value=1, step=1, key="lead_crm_id")
    product_id = st.number_input("Product ID", min_value=1, value=1, step=1, key="product_id")

# Main content
with main_content:
    st.title("Car Dealer Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Create a container for chat messages
    chat_container = st.container()

    # Create a container for the input box at the bottom
    input_container = st.container()

    # Display chat messages from history on app rerun
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Move the chat input to the bottom
    with input_container:
        prompt = st.chat_input("Ask about car dealers offering test drives")

    # React to user input
    if prompt:
        # Display user message in chat message container
        with chat_container:
            st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Prepare the payload for the API request
        payload = {
            "prompt": prompt,
            "model_service": st.session_state.model_service,
            "model_name": st.session_state.model_name,
            "dealers_id": st.session_state.dealers_id,
            "lead_id": st.session_state.lead_id,
            "lead_crm_id": st.session_state.lead_crm_id,
            "product_id": st.session_state.product_id
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
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # Optionally, display raw API response for debugging
        with st.expander("Debug: Raw API Response"):
            st.write(response.text if 'response' in locals() else "No response received")

    # Force a rerun to update the chat container after new messages
  