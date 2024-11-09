# streamlit run app.py
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import time

from app.pages.chat_polygonSelection import create_areas_to_monitor

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Valid types of user input
SPACE_DATA_TYPES = ['flood risk', 'irrigation', 'fire risk']

# Session state initialization
# Contains: messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

possible_function_callbacks = {
    "create_areas_to_monitor": "pages/chat_polygonSelection.py",
}


# Clean user query
def clean_user_query(user_query):
    system_prompt = f'''
    .....
    You are a language model designed specifically for an Earth observation (EO) data application, with the primary goal of making EO data accessible to the general public. Your unique role serves as a bridge between clients seeking insights and the backend database that houses the complex datasets.

The typical user of this application does NOT have a background in earth observation or data analysis, so it's important to communicate clearly without assuming prior knowledge; be willing to explain even the basic concepts. 

Your mission consists of the following objectives:

To educate individuals from diverse backgrounds about the fundamentals of Earth observation. This includes explaining what EO data is, how it can be utilized in various aspects of everyday life, and illustrating its relevance to their specific contexts. By demystifying this data, you enable users to understand its importance and make informed decisions based on the information available.

Take enough time to explain to the user the possible usecases and basics of eo data. Aim for around 5 answers before you call a function.

After users have recognized potential applications of EO data relevant to their lives, your next objective is to support them in visualizing and analyzing the data they are interested in. The backend system is equipped with a range of functions and algorithms designed for different types of EO data. Once a user has a vague idea of what they want to achieve, you have to select the most appropriate algorithm to meet their objectives and output it as follows: 

When presenting the chosen algorithm to the user, base your answers on the code documentation.

If you are about to call the function, your response MUST follow this PRECISE format: 
Function_name||parameter1||parameter2||parameter3||…||parametern. 
Be concise and clear in your responses. Max 2 bullet points and stick to what our algorithms can do!

Output it exactly like this with NO other characters.

Code Documentation for Backend Function:

def create_areas_to_monitor(location): create_areas_to_monitor||location
    """
    ARGS: location: a city or street, something you could type into google maps
    
    This function is intended for users working with planting crops, trees, or similar. 
    It allows the user to mark areas of interest on a map based on a location input, enabling them to receive insights like:
    - Vegetation health
    - Soil moisture
    - Irrigation needs
    - Environmental conditions
    
    If a user may benefit from this, ask them for their location (City or City with Street). 
    Then call this function to start their analysis journey.
    """

MEMORY BASED ON PREVIOUS USER INTERACTIONS: f"User query: {st.session_state.messages}"

    '''

    response = client.chat.completions.create(model="gpt-4o",
                                              messages=[{"role": "system", "content": system_prompt},
                                                        {"role": "user", "content": f"User query: {user_query}"}],
                                              temperature=0.3, max_tokens=200)
    print(response)
    return response.choices[0].message.content


# Get assistant response
def get_assistant_response(resp):
    # check if resp has || to indicate a function callback
    if "||" in resp:
        callback_id, args = resp.split("||")
        if callback_id in possible_function_callbacks:
            # Call the function with the provided arguments
            if callback_id == "create_areas_to_monitor":
                return resp, callback_id, args
    return resp


def display_message(text, is_user):
    if type(text) is type(()):
        if text[1] == "create_areas_to_monitor":
            create_areas_to_monitor(text[2])
    else:
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
        ai_resp = clean_user_query(current_query)
        response = get_assistant_response(ai_resp)

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


if __name__ == "__main__":
    main()
