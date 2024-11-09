# streamlit run app.py
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
import os
import time
import markdown
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

# Clean user query
def clean_user_query(user_query):
    system_prompt = '''You are an Earth Observation (EO) Assistant, specialized in making satellite data accessible and actionable for users. Your role is to bridge the gap between technical EO capabilities and practical user needs.

    RESPONSIBILITIES:
    1. Education: Help users understand how Earth observation can benefit their specific use case
    2. Guidance: Direct users to appropriate analysis tools and visualizations (or simply be helpful)
    3. Analysis: Facilitate data interpretation and insights

    STYLE:
    - Use markdown formatting
    - Provide concise responses with bullet points for clarity when appropriate
    - Avoid walls of text or walls of bullet points (max 3 bullet points)
    - Avoid technical jargon (e.g. "EO" or "function" or "parameter")

    STRATEGY:
    - Explain EO data and how it can be useful in your first 2 messages
    - If we don't have a function for the user's query, reply with useful answers (linking to resources) and give user a hint about what we can help with
    - If the user's query is not clear, ask for clarification in a few back-and-forth messages

    FUNCTION CALL:
    - Confirm input parameter details (e.g., their city or address) before calling a function
    - When ready to call a function, format your response exactly as: function_name||param1||param2||paramN
    - Do NOT include any other text or formatting in the message where you call a function

    AVAILABLE FUNCTIONS:
    create_areas_to_monitor(location)
    - Purpose: Set up monitoring zones for vegetation and environmental analysis
    - Parameter: location (like a city or street, something you could type into google maps. NOT a country)
    - Best for: Agricultural, forestry, and land management applications
    - Description: Allows the user to mark areas of interest on a map based on a location input, enabling them to receive insights like vegetation health, soil moisture, irrigation needs, and environmental conditions.
    '''

    # Convert session state messages to OpenAI format
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages:
        role = "user" if msg["is_user"] else "assistant"
        messages.append({"role": role, "content": msg["content"]})

    # Generate response
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3,
        max_tokens=200)
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


# Create the HTML for a message bubble with consistent styling.
def create_message_html(html_content, style, bg_color):
    return (f'<div style="display: flex; justify-content: {style}; margin-bottom: 1rem;">'
            f'<div style="background-color: {bg_color}; color: white; padding: 0.5rem 1rem; '
            f'border-radius: 15px; max-width: 80%;">{html_content}</div></div>')


def display_message(text, is_user, with_delay=False):
    if type(text) is type(()):
        if text[1] == "create_areas_to_monitor":
            create_areas_to_monitor(text[2])
    else:
        style = "flex-end" if is_user else "flex-start"
        bg_color = "#2b313e" if is_user else "#0e1117"

        if not with_delay:
            html_content = markdown.markdown(text)
            st.markdown(create_message_html(html_content, style, bg_color), unsafe_allow_html=True)
            return

        # Split text into lines first to preserve markdown formatting
        lines = text.split('\n')
        placeholder = st.empty()
        displayed_lines = []

        for line in lines:
            # For each line, split into words and display progressively
            words = line.split()
            for i in range(len(words)):
                current_line = ' '.join(words[:i + 1])
                # Combine with previously displayed lines
                current_text = '\n'.join(displayed_lines + [current_line])
                html_content = markdown.markdown(current_text)

                placeholder.markdown(
                    create_message_html(html_content, style, bg_color),
                    unsafe_allow_html=True
                )
                time.sleep(0.03)

            # After completing a line, add it to displayed lines
            displayed_lines.append(line)


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

        # Add spinner while processing response
        with st.spinner(''):
            # Process the response
            ai_resp = clean_user_query(current_query)
            response = get_assistant_response(ai_resp)

            # Add assistant's response to messages
            st.session_state.messages.append({"content": response, "is_user": False})

            # Display the AI response with delay effect
            display_message(response, False, with_delay=True)

            # Clear current query and rerun
            st.session_state.pop('current_query', None)
            time.sleep(0.5)  # Small pause before rerun
            st.rerun()
    else:
        # Display existing messages when no new query
        for message in st.session_state.messages:
            display_message(message['content'], message['is_user'])


if __name__ == "__main__":
    main()
