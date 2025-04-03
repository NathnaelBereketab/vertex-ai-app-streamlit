import streamlit as st
from vertexai.generative_models import GenerativeModel
import json
from google.cloud import aiplatform

# Setup
def initialize_ai():
    aiplatform.init(project="ultra-surfer-450918-h7", location="us-central1")
    return GenerativeModel("gemini-1.0-pro")

# Data retrieval
def query_neighbors(ai_engine, query_state):
    instruction = f"""
    For the state of {query_state}, list all states that share a physical border.
    Return only JSON formatted as: {{"neighboring_states": ["State1", "State2"]}}
    For invalid input, return: {{"error": "Not a valid US state"}}
    """
    
    config = {
        "temperature": 0.1,
        "max_output_tokens": 1024,
        "top_k": 40,
        "top_p": 0.8,
    }
    
    return ai_engine.generate_content(instruction, generation_config=config)

# Process response
def process_ai_response(raw_response):
    response_text = raw_response.text.strip()
    
    try:
        # Try direct parsing
        return json.loads(response_text)
    except:
        # Extract JSON if embedded in other text
        try:
            if "{" in response_text and "}" in response_text:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                json_portion = response_text[start_idx:end_idx]
                return json.loads(json_portion)
        except:
            pass
            
        # Return error if parsing fails
        return {"error": "Unable to process response"}

# Display logic
def display_neighbor_results(result_data, state_name):
    if "error" in result_data:
        st.error(result_data["error"])
        return
        
    state_list = result_data.get("neighboring_states", [])
    
    if not state_list:
        if state_name.lower() in ["alaska", "hawaii"]:
            st.info(f"{state_name} has no land borders with other states")
        else:
            st.warning(f"No neighboring states found for {state_name}")
        return
    
    st.info(f"{state_name} has {len(state_list)} neighboring states:")
    for neighboring_state in state_list:
        st.write(f"• {neighboring_state}")

# Main application
def run_neighbor_finder():
    st.title("Find your neighboring states")
    st.write("Enter a U.S. state to discover its neighbors")
    
    state_input = st.text_input("Enter a state name:", placeholder="e.g. Colorado")
    search_button = st.button("Find Neighbors")
    
    if search_button:
        if not state_input.strip():
            st.error("Please enter a state name")
            return
            
        with st.spinner(f"Looking up neighbors for {state_input}..."):
            model = initialize_ai()
            response = query_neighbors(model, state_input)
            results = process_ai_response(response)
            display_neighbor_results(results, state_input)

# Run application
if __name__ == "__main__":
    run_neighbor_finder()