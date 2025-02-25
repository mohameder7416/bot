import streamlit as st
import requests
import json

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
    
    dealers_id = st.number_input("Dealers ID", min_value=1, value=102262, step=1, key="dealers_id")
    lead_id = st.number_input("Lead ID", min_value=1, value=1, step=1, key="lead_id")
    lead_crm_id = st.number_input("Lead CRM ID", min_value=1, value=54321, step=1, key="lead_crm_id")
    product_id = st.number_input("Product ID", min_value=1, value=12, step=1, key="product_id")

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

        # Prepare the payload for the API request - match exactly what worked in Postman
        payload = {
            "prompt": prompt,
            "model_service": st.session_state.model_service,
            "model_name": st.session_state.model_name,
            "dealers_id": st.session_state.dealers_id,
            "lead_id": st.session_state.lead_id,
            "lead_crm_id": st.session_state.lead_crm_id,
            "product_id": st.session_state.product_id
        }

        # Add debug output of what we're sending
        with st.expander("Debug: Request Payload"):
            st.json(payload)

        try:
            # Make a request to the FastAPI backend
            response = requests.post(API_URL, json=payload)
            
            # Display status code for debugging
            st.sidebar.write(f"Status code: {response.status_code}")
            
            # Try to parse JSON even if status code indicates error
            try:
                response_data = response.json()
                st.sidebar.write("Response parsed successfully")
            except ValueError:
                response_data = {"error": "Could not parse JSON response", "raw": response.text}
                st.sidebar.write("Failed to parse response")
            
            # Extract 'result' from the response if it exists
            assistant_response = response_data.get('result', 'No result found in response.')
            
            # If no result, provide the full response for debugging
            if 'result' not in response_data:
                st.sidebar.write("No 'result' field found in response")
                assistant_response += f"\n\nDebug info: {json.dumps(response_data, indent=2)}"
            
        except requests.exceptions.RequestException as e:
            assistant_response = f"Error: Unable to reach the server. Details: {str(e)}"
            st.sidebar.write(f"Request exception: {e}")
        except Exception as e:
            assistant_response = f"Error: Something went wrong. Details: {str(e)}"
            st.sidebar.write(f"General exception: {e}")

        # Display assistant response in chat message container
        with chat_container:
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # Always display raw API response for debugging
        with st.expander("Debug: Raw API Response"):
            if 'response' in locals():
                st.write(f"Status code: {response.status_code}")
                st.text(response.text)
                st.write("Headers:")
                st.json(dict(response.headers))
            else:
                st.write("No response received")