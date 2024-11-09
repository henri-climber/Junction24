# streamlit run app.py
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import time

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Valid types of user input
SPACE_DATA_TYPES = ['flood risk', 'irrigation', 'fire risk']

# Session state initialization
# Contains: messages, last_valid_type, last_valid_location
if 'messages' not in st.session_state: st.session_state.messages = []
if 'last_valid_type' not in st.session_state: st.session_state.last_valid_type = None
if 'last_valid_location' not in st.session_state: st.session_state.last_valid_location = None

# Clean user query
def clean_user_query(user_query):
    system_prompt = f"""
    Extract data type and city from user query.
    Valid data types are ONLY: {', '.join(SPACE_DATA_TYPES)}.
    Format output EXACTLY as: DATA_TYPE||CITY
    If data type not valid, output 'invalid' as DATA_TYPE.
    If not a real city, output 'missing' as CITY.

    EXAMPLES
	Input: wildfire risk in australia
	Output: fire risk||missing
	
	Input: should i worry of tornadoes in munich of baviera
	Output: invalid||Munich
    """
    response = client.chat.completions.create(model="gpt-4o",
        messages=[{"role": "system", "content": system_prompt}, 
        {"role": "user", "content": f"User query: {user_query}"}],
        temperature=0.3, max_tokens=100)
    return response.choices[0].message.content

# Get assistant response
def get_assistant_response(data_type, location):
    # Store valid parameters
    if data_type != 'invalid': st.session_state.last_valid_type = data_type
    if location != 'missing': st.session_state.last_valid_location = location
    
    final_type = st.session_state.last_valid_type or data_type
    final_location = st.session_state.last_valid_location or location

    if final_type == 'invalid' and final_location == 'missing':
        return f"Sorry, I need both a city location and the type of spatial information ({', '.join(SPACE_DATA_TYPES)})."
    elif final_type == 'invalid':
        return f"Sorry, I can only help with {', '.join(SPACE_DATA_TYPES)}. Which one interests you for {final_location}?"
    elif final_location == 'missing':
        return f"Please type a city name to visualize the {final_type} data."
    return f"Great! Showing {final_type} data for {final_location}..."

def display_message(text, is_user=False):
    style = "flex-end" if is_user else "flex-start"
    bg_color = "#2b313e" if is_user else "#0e1117"
    st.markdown(
        f'<div style="display: flex; justify-content: {style}; margin-bottom: 1rem;">'
        f'<div style="background-color: {bg_color}; color: white; padding: 0.75rem; '
        f'border-radius: 15px; max-width: 80%;">{text}</div></div>', unsafe_allow_html=True)

def main():
    # Set page config
    st.set_page_config(page_title="MapStronaut", page_icon="🌍")

    # Set font sizes
    st.markdown("""<style>
        .stMarkdown div div { font-size: 18px !important}
        textarea[data-testid="stChatInputTextArea"] {
            font-size: 18px !important
        }
        h1 a {display: none !important}
        </style>""", unsafe_allow_html=True)
    st.markdown("<br><br><h1 style='text-align: center;'>How can space data help you? 🌍</h1>", unsafe_allow_html=True)

    # Only show example queries if there are no messages yet AND no current query
    if not st.session_state.messages and not st.session_state.get('current_query'):
        example_queries = [
            ("💧 Irrigation in Madrid", "How often do I need to water my crops in Madrid?"),
            ("🔥 Fire risk in Athens", "What's the wildfire danger level in Athens?"),
            ("🌊 Flood risk in Mumbai", "What is the flood risk in Mumbai?")]

        # Create example buttons
        for button_text, full_example_query in zip(st.columns(3), example_queries):
            if button_text.button(full_example_query[0]):
                st.session_state['current_query'] = full_example_query[1]
                st.rerun()  # Immediately rerun to clear buttons

    current_query = st.chat_input("Message MapStronaut") or st.session_state.get('current_query')
    
    if current_query:
        # Immediately show the user's message
        st.session_state.messages.append({"content": current_query, "is_user": True})
        
        # Display all messages including the new user message
        for message in st.session_state.messages:
            display_message(message['content'], message['is_user'])
        
        # Process the response
        data_type, location = clean_user_query(current_query).split('||')
        response = get_assistant_response(data_type, location)
        
        # Add assistant's response to messages
        st.session_state.messages.append({"content": response, "is_user": False})
        
        # Wait 1 second before showing output (otherwise it's too fast)
        time.sleep(1)

        # Clear current query and rerun
        st.session_state.pop('current_query', None)
        st.rerun()
    else:
        # Display existing messages when no new query
        for message in st.session_state.messages:
            display_message(message['content'], message['is_user'])

    # Display map visualization if available
    if st.session_state.last_valid_type and st.session_state.last_valid_location:
        time.sleep(2)
        st.info("Visualization here", icon="📍")
        st.markdown("""
            <style>
            [data-testid="stAlertContentInfo"] {
                min-height: 300px;
                padding: 20px;
            }
            </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()