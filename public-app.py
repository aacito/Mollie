
import streamlit as st
import openai
import time
from PIL import Image




from openai import OpenAI
import streamlit as st
import time
from PIL import Image
import re

# Configure the logo filepath
logo_filepath = "Vertical_VT_Full_Color_RGB.png"


# Configure site title, icon, and other
site_title = "Mollie 2"
site_icon = "🐶"

# Set the page title, description, and other text
page_title = "Mollie 2"
description = "I'm Mollie, your TA for ACIS 5194: Financial Statement Analysis. Woof!"
as_of = ''
other_text = '' # Optional sidebar text
instructions = "Please click on \'Start New Chat\' button on the left sidebar to get started."

tips = ""
chat_box_text = "Type your questions here."
footer_text = 'Last Updated 2023-11-20'

error_message = "ERROR: Please enter your OpenAI API key AND click \'Start New Chat\' to get started."        

# Set up the Streamlit page with a title and icon
st.set_page_config(page_title= site_title, page_icon= site_icon)

# Main chat interface setup
st.markdown(f"<h1 style='color: rgba(134, 31, 65, 1);'>{page_title}</h1>", unsafe_allow_html=True)
st.caption(description)
st.markdown(f"<h3 style='color: rgba(134, 31, 65, 1);'>Instructions</h3>", unsafe_allow_html=True)
st.markdown(instructions)
st.markdown(tips)
st.divider()

# Display the image in the sidebar
image = Image.open(logo_filepath)
st.sidebar.image(image)
st.sidebar.divider()

# Set OpenAI contants 
if st.secrets:
    if 'ASSISTANT_ID' in st.secrets:
        ASSISTANT_ID = st.secrets['ASSISTANT_ID']
    if 'OPENAI_API_KEY' in st.secrets:
        OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']
    client = OpenAI(api_key=OPENAI_API_KEY)

if "THREAD_ID" not in st.session_state:
    st.session_state.THREAD_ID = None

if "messages" not in st.session_state:
    st.session_state.messages = []




if st.sidebar.button("Start New Chat"):
    thread = client.beta.threads.create()
    st.session_state.THREAD_ID = thread.id
    st.session_state.messages = []


# Create a sidebar for API key configuration and additional features
st.sidebar.divider()
st.sidebar.markdown(f"<h3 style='color: rgba(134, 31, 65, 1);'>Tips and Tricks:</h3>", unsafe_allow_html=True)
st.sidebar.markdown(tips)
st.sidebar.divider()

feedback_text = "This app is a prototype and still a work-in-process. Please help improve it by sharing your feedback [here](https://forms.gle/3DfPAG86RyepVXMo8)."

st.sidebar.markdown(feedback_text)

st.sidebar.divider()

st.markdown("""
    <style>
    .element-container .stTextInput input::placeholder {
        color: #E5751F; 
    }
    .element-container .stTextInput input {
        color: black; 
    }
    </style>
    """, unsafe_allow_html=True)

# Display existing messages in the chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input for the user
if prompt := st.chat_input(chat_box_text):
    if st.session_state.THREAD_ID is None:
        st.markdown(f"<h3 style='color: rgba(232, 119, 49, 1);'>{error_message}</h3>", unsafe_allow_html=True)
    else:
        format_prompt = prompt.replace("$", "\\$")
        # Add user message to the state and display it
        st.session_state.messages.append({"role": "user", "content": format_prompt})
        with st.chat_message("user"):
            st.write(str(format_prompt))

        # Add the user's message to the existing thread
        client.beta.threads.messages.create(
            thread_id = st.session_state.THREAD_ID,
            role="user",
            content=prompt
        )

        # Create a run with additional instructions
        run = client.beta.threads.runs.create(
            thread_id = st.session_state.THREAD_ID,
            assistant_id=ASSISTANT_ID
        )

        # Poll for the run to complete and retrieve the assistant's messages
        while run.status != 'completed':
            time.sleep(.5)
            run = client.beta.threads.runs.retrieve(
                thread_id = st.session_state.THREAD_ID,
                run_id=run.id
            )

        # Retrieve messages added by the assistant
        messages = client.beta.threads.messages.list(
            thread_id =  st.session_state.THREAD_ID, 
            order="asc"
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages 
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            response = message.content[0].text.value
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(f"{response}", unsafe_allow_html=True)



def footer(text):
    footer_html = f"""
    <style>
    .footer {{
        position: fixed;
        left: 10;
        bottom: 0;
        width: 100%;
        background-color: rgba(241, 241, 241, 0);
        color: rgba(117, 120, 123, 1);
        text-align: left;
    }}
    </style>
    <div class='footer'>
        <p>{text}</p>
    </div>
    """
    st.sidebar.markdown(footer_html, unsafe_allow_html=True)

footer(footer_text)
