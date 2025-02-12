import streamlit as st
import requests
from datetime import datetime

# Initialize session states
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'conversation_mode' not in st.session_state:
    st.session_state.conversation_mode = "QA"  # Default to Q&A mode
if 'debate_rounds' not in st.session_state:
    st.session_state.debate_rounds = []

# Page configuration
st.set_page_config(page_title="Steve Jobs & Peter Thiel Debate", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .chat-container {
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        background-color: #f5f5f5;
        color:rgb(25, 25, 25);
    }
    .jobs-message {
        background-color: #E8F4F9;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #0077B5;
        color:rgb(25, 25, 25);
    }
    .thiel-message {
        background-color: #F9F2E8;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #FF9900;
        color:rgb(25, 25, 25);
    }
    .user-message {
        background-color: #E8E8E8;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
        color:rgb(25, 25, 25);
    }
    .debate-round {
        border: 1px solid #ddd;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("💭 Steve & Peter Debate")
    st.markdown("Welcome to the debate between two tech titans! Engage in insightful conversations or watch them debate on various topics.")
    st.markdown("---")

    # Conversation mode selector
    st.subheader("Conversation Mode")
    conversation_mode = st.radio(
        "Select mode:",
        ["Q&A", "Debate"],
        key="mode_selector"
    )
    st.session_state.conversation_mode = conversation_mode

    if conversation_mode == "Debate":
        st.info("In debate mode, Steve Jobs and Peter Thiel will engage in a back-and-forth discussion with 200-character limits per response.")

    st.markdown("---")

    # Personality descriptions
    st.subheader("🧠 Personalities")

    st.markdown("""
    **Steve Jobs:**
    - Co-founder of Apple
    - Known for revolutionary products
    - Focus on design and user experience
    - "Think Different" philosophy
    """)

    st.markdown("""
    **Peter Thiel:**
    - PayPal co-founder
    - Venture capitalist
    - Contrarian thinker
    - Zero to One author
    """)

    st.markdown("---")

    # Clear history button
    if st.button("Clear History"):
        st.session_state.chat_history = []
        st.session_state.debate_rounds = []
        st.rerun()

# Main content
st.title("Steve Jobs & Peter Thiel Debate 🎭")

# API interaction functions
def get_response(api_url, question, prompt):
    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "Llama-3.2-3B-Instruct",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ]
    }
    try:
        # st.write(f"Sending request to {api_url} with data: {data}")
        response = requests.post(api_url, headers=headers, json=data)
        # st.write(f"Received response: {response.status_code}, {response.content}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        st.error(f"Response content: {response.content if 'response' in locals() else 'No response'}")
        return None

def display_response(response):
    if response and 'choices' in response and len(response['choices']) > 0:
        return response['choices'][0]['message']['content']
    return 'No response received.'

# Prompts
JOBS_PROMPT = '''You're Steve Jobs. Respond authentically as Steve would, drawing from his known perspectives, experiences, and personality. Keep responses concise and impactful.'''
THIEL_PROMPT = '''You're Peter Thiel. Respond with his characteristic contrarian wisdom, focus on monopolistic advantage, and emphasis on bold thinking. Stay sharp, analytical, and direct.'''

# Input section
question = st.text_input('Ask your question:', key='question_input')

if question:
    if st.session_state.conversation_mode == "Q&A":
        # Q&A Mode
        steve_jobs_response = get_response('https://0x5259b4d33591e7d48e9e044ed7c120058ba8e605.gaia.domains/v1/chat/completions',
                                        question, JOBS_PROMPT)
        peter_thiel_response = get_response('https://0x4d4d7154309dc9c2059312fda3ead7219ebd94e8.gaia.domains/v1/chat/completions',
                                          question, THIEL_PROMPT)

        if steve_jobs_response and peter_thiel_response:
            st.session_state.chat_history.append({
                'mode': 'Q&A',
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'question': question,
                'steve_jobs': display_response(steve_jobs_response),
                'peter_thiel': display_response(peter_thiel_response)
            })

    else:
        # Debate Mode
        debate_round = []

        # Initial responses
        jobs_response = get_response('https://0x5259b4d33591e7d48e9e044ed7c120058ba8e605.gaia.domains/v1/chat/completions',
                                   f"{question} (Respond in under 200 characters)", JOBS_PROMPT)
        if jobs_response:
            jobs_content = display_response(jobs_response)
            debate_round.append(('Steve Jobs', jobs_content))

            thiel_response = get_response('https://0x4d4d7154309dc9c2059312fda3ead7219ebd94e8.gaia.domains/v1/chat/completions',
                                        f"Respond to this point by Steve Jobs: {jobs_content} (Respond in under 200 characters)",
                                        THIEL_PROMPT)
            if thiel_response:
                thiel_content = display_response(thiel_response)
                debate_round.append(('Peter Thiel', thiel_content))

                # Follow-up round
                jobs_rebuttal = get_response('https://0x5259b4d33591e7d48e9e044ed7c120058ba8e605.gaia.domains/v1/chat/completions',
                                           f"Respond to this point by Peter Thiel: {thiel_content} (Respond in under 200 characters)",
                                           JOBS_PROMPT)
                if jobs_rebuttal:
                    debate_round.append(('Steve Jobs', display_response(jobs_rebuttal)))

                    thiel_closing = get_response('https://0x4d4d7154309dc9c2059312fda3ead7219ebd94e8.gaia.domains/v1/chat/completions',
                                               f"Give a final response to Steve Jobs' point: {display_response(jobs_rebuttal)} (Respond in under 200 characters)",
                                               THIEL_PROMPT)
                    if thiel_closing:
                        debate_round.append(('Peter Thiel', display_response(thiel_closing)))

                        st.session_state.debate_rounds.append({
                            'question': question,
                            'timestamp': datetime.now().strftime("%H:%M:%S"),
                            'exchanges': debate_round
                        })

# Display chat history
st.markdown("### 💬 Conversation History")

if st.session_state.conversation_mode == "Q&A":
    for chat in reversed(st.session_state.chat_history):
        if chat['mode'] == 'Q&A':
            st.markdown(f"**Time:** {chat['timestamp']}")
            st.markdown(f"<div class='user-message'>🤔 **Question:** {chat['question']}</div>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"<div class='jobs-message'>🍎 **Steve Jobs:** {chat['steve_jobs']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='thiel-message'>💰 **Peter Thiel:** {chat['peter_thiel']}</div>", unsafe_allow_html=True)
            st.markdown("---")
else:
    for debate in reversed(st.session_state.debate_rounds):
        st.markdown(f"**Time:** {debate['timestamp']}")
        st.markdown(f"<div class='user-message'>🤔 **Topic:** {debate['question']}</div>", unsafe_allow_html=True)

        for speaker, response in debate['exchanges']:
            if speaker == "Steve Jobs":
                st.markdown(f"<div class='jobs-message'>🍎 **{speaker}:** {response}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='thiel-message'>💰 **{speaker}:** {response}</div>", unsafe_allow_html=True)
        st.markdown("---")
