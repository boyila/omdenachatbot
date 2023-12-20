import streamlit as st
from langchain_helper import evaluate_answer
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import pandas as pd
import random


# Title of the application
st.title("INTERVIEW CHATBOT 🤖")


# Load the CSV file into a DataFrame and select a random prompt
df = pd.read_csv(r'C:\Users\tboyi\Projects\langchain\3_project_codebasics_q_and_a\chatbot_omdena\team_2_final_dataset.csv', encoding='ISO-8859-1')  # Or try 'iso-8859-1', 'latin1', 'cp1252' if 'utf-8' doesn't work
random_question = random.choice(df['promptq'].tolist())

# Initialize session state for button label, question text, answer text, and listening state
if 'button_label' not in st.session_state:
    st.session_state['button_label'] = 'Start 🎙️'
if 'question' not in st.session_state:
    st.session_state['question'] = ''
if 'answer' not in st.session_state:
    st.session_state['answer'] = ''
if 'displayed_question' not in st.session_state:
    st.session_state['displayed_question'] = random_question


# display the question from the dataset
st.info(st.session_state['displayed_question'])

# Define the button for text-to-speech for the displayed question
tts_question_button = Button(label="Speak Question", width=100)

# JavaScript for the TTS button for the displayed question
tts_question_js_code = """
    var u = new SpeechSynthesisUtterance();
    u.text = "{displayed_question}";
    u.lang = 'en-US';
    speechSynthesis.speak(u);
""".format(displayed_question=st.session_state['displayed_question']).replace('`', '\'')

tts_question_button.js_on_event("button_click", CustomJS(code=tts_question_js_code))

# Display the TTS button for the displayed question
st.bokeh_chart(tts_question_button)


# Define the toggle button
toggle_button = Button(label=st.session_state['button_label'], width=100, height=30)

# JavaScript for the toggle button - handles speech recognition
js_code = """
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    };

    if (button.label == 'Start 🎙️') {
        recognition.start();
        button.label = 'Stop 🛑';
    } else {
        recognition.stop();
        button.label = 'Start 🎙️';
    }
"""



# Attach JavaScript code to the toggle button
toggle_button.js_on_event("button_click", CustomJS(code=js_code, args={'button': toggle_button}))


# # Streamlit Bokeh events for the toggle button
result = streamlit_bokeh_events(
    toggle_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=True,
    override_height=75,
    debounce_time=0
)

# # Update the question in the session state
if result:
    if "GET_TEXT" in result:
        st.session_state['question'] += " " + result.get("GET_TEXT")
    

# # Textarea for the question
question = st.text_area("Answer:", value=st.session_state['question'], key="question", height=300, max_chars=None)

# Process the question and display the answer
def process_question():
    if st.session_state['question']:
        chain = evaluate_answer()
        response = chain(st.session_state['question'])
        st.session_state['answer'] = response["result"]
        # st.session_state['question'] = ""  # Clear the question to prevent reprocessing it
        
    

# Button to trigger the answer generation
if st.button('Submit'):
    process_question()

# Display the answer
if 'answer' in st.session_state and st.session_state['answer']:
    st.write("Answer:", st.session_state['answer'])


