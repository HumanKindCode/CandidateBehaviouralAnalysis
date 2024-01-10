import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

Base = declarative_base()

# Google Sheets connection setup
def init_gspread_connection():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(".streamlit/behavioral-forms-90a681513583.json", scope)
    client = gspread.authorize(creds)
    return client

def get_sheet_data(client, spreadsheet_id, worksheet_name):
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    data = pd.DataFrame(sheet.get_all_records())
    return data

client = init_gspread_connection()

# Database setup
class Candidate(Base):
    __tablename__ = 'candidates'
    id = Column(Integer, primary_key=True)
    CANDIDATE_NAME = Column(String)
    ANSWER1 = Column(String)
    ANSWER2 = Column(String)
    ANSWER3 = Column(String)
    ANSWER4 = Column(String)
    ANSWER5 = Column(String)
    ANSWER6 = Column(String)
    ANSWER7 = Column(String)
    ANSWER8 = Column(String)
    ANSWER9 = Column(String)
    ANSWER10 = Column(String)
    OPENNESS = Column(String)
    CONSCIENTIOUSNESS = Column(String)
    EXTRAVERSION = Column(String)
    AGREEBLENESS = Column(String)
    NEUROTICISM = Column(String)

def connect_to_db():
    engine = create_engine('sqlite:///CandidateAnswers.db')
    Base.metadata.create_all(engine)
    return engine

engine = connect_to_db()

# Function to insert data into the database
def insert_candidate_data(candidate_data, engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_candidate = session.query(Candidate).filter(Candidate.CANDIDATE_NAME == candidate_data["CANDIDATE_NAME"]).first()
    if existing_candidate is not None:
        session.close()
        return False
    new_candidate = Candidate(**candidate_data)
    session.add(new_candidate)
    session.commit()
    session.close()
    return True

# Fetch existing data from Google Sheets
spreadsheet_id = "1Ou0ZXVcLPkhdARBPnhfrp8cGq-zG2hPMnezQI8SZp2I"
worksheet_name = "Sheet1"
existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)

# Streamlit app layout
st.title("Candidate Psyche Analysis")
st.write(existing_data)
QUESTION1_TYPES = [
    "Embraced the change and led the transition.",
    "Adapted gradually with some resistance.",
    "Found it challenging and preferred previous methods.",
    "Struggled significantly and needed extensive support.",
]
QUESTION2_TYPES = [
    "Leader, guiding the team towards goals.",
    "Collaborator, working closely with others.",
    "Independent contributor, working on tasks alone.",
    "Supporter, helping others with their tasks.",
]
QUESTION3_TYPES = [
    "Analyzed the problem and devised a strategic solution.",
    "Brainstormed with the team for collective solutions.",
    "Used tried-and-tested methods to address the issue.",
    "Required guidance to find an appropriate solution.",
]
QUESTION4_TYPES = [
    "Direct and honest while being respectful.",
    "Tactful and considerate, softening the message.",
    "Hesitant and prefer to avoid confrontation.",
    "Seek guidance or delegate the task to others.",
]
QUESTION5_TYPES = [
    "View setbacks as learning opportunities.",
    "Remain optimistic and try again.",
    "Feel discouraged but eventually recover.",
    "Get significantly affected and demotivated.",
]
QUESTION6_TYPES = [
    "Always seek consensus.",
    "Mostly seek consensus, but can be authoritative.",
    "Balanced between consensus-seeking and authoritative.",
    "Mostly authoritative, but can seek consensus.",
    "Always authoritative."
]
QUESTION7_TYPES = [
    "Always prefer groups.",
    "Mostly prefer groups, but can work independently.",
    "Equally comfortable in groups or working independently.",
    "Mostly prefer working independently, but can work in groups.",
    "Always prefer working independently."
]
QUESTION8_TYPES = [
    "Always openly and expressively.",
    "Mostly openly, but can be reserved.",
    "Balanced between expressive and reserved.",
    "Mostly reserved, but can be expressive.",
    "Always reserved."
]
QUESTION9_TYPES = [
    "Always rely on empathy.",
    "Mostly rely on empathy, but can be rational.",
    "Balanced between empathy and rational thinking.",
    "Mostly rely on rational thinking, but can be empathetic.",
    "Always rely on rational thinking."
]
QUESTION10_TYPES = [
    "Always flexible and open to change.",
    "Mostly flexible, but can be determined.",
    "Balanced between flexibility and determination.",
    "Mostly determined, but can be flexible.",
    "Always determined."
]
BIG5_QUESTIONS = {
    "Openness": "Imagine you are offered an opportunity to work on a project that involves new and unfamiliar technology. How would you approach this situation?",
    "Conscientiousness": "Describe how you would handle a situation where you have multiple deadlines approaching simultaneously.",
    "Extraversion": "If you were tasked with leading a team for a new project, how would you motivate and manage your team members?",
    "Agreeableness": "Tell us about a time when you had a disagreement with a colleague. How did you resolve it?",
    "Neuroticism": "How do you react and cope when faced with a stressful situation at work?"
}
with st.form(key="vendor_form"):
    candidate_name = st.text_input(label="Candidate Name*")
    ANSWER_1 = st.selectbox("Describe a situation where you had to adapt to significant changes at work. How did you manage the transition?*", options=QUESTION1_TYPES, index=None)
    ANSWER_2 = st.selectbox("Think of a time when you had to work closely with a team. What role do you usually take in a team setting?*", options=QUESTION2_TYPES, index=None)
    ANSWER_3 = st.selectbox("Recall a complex problem you faced in your previous role. How did you approach solving it?*", options=QUESTION3_TYPES, index=None)
    ANSWER_4 = st.selectbox("How do you handle situations where you have to deliver difficult feedback?*", options=QUESTION4_TYPES, index=None)
    ANSWER_5 = st.selectbox("When facing setbacks, how do you generally respond?*", options=QUESTION5_TYPES, index=None)
    ANSWER_6 = st.selectbox("When making decisions in a team, do you prefer to seek consensus or make authoritative choices?*", options=QUESTION6_TYPES, index=None)
    ANSWER_7 = st.selectbox("Do you prefer working in groups or independently?*", options=QUESTION7_TYPES, index=None)
    ANSWER_8 = st.selectbox("How do you typically express your thoughts and ideas?*", options=QUESTION8_TYPES, index=None)
    ANSWER_9 = st.selectbox("When solving problems, do you rely more on empathy or rational thinking?*", options=QUESTION9_TYPES, index=None)
    ANSWER_10 = st.selectbox("How do you approach goals and plans?*", options=QUESTION10_TYPES, index=None)
    OPENNESS = st.text_area(label=BIG5_QUESTIONS["Openness"])
    CONSCIENTIOUSNESS = st.text_area(label=BIG5_QUESTIONS["Conscientiousness"])
    EXTRAVERSION = st.text_area(label=BIG5_QUESTIONS["Extraversion"])
    AGREEBLENESS = st.text_area(label=BIG5_QUESTIONS["Agreeableness"])
    NEUROTICISM = st.text_area(label=BIG5_QUESTIONS["Neuroticism"])
    
    st.markdown("**required*")
    submit_button = st.form_submit_button(label="Submit Candidate Details")
       
    if submit_button:
        if not candidate_name or not ANSWER_1 or not ANSWER_2:
            st.warning("Ensure all mandatory fields are filled.")
            st.stop()
        
        else:
        # Prepare the data for insertion
            candidate_data = {
                "CANDIDATE_NAME": candidate_name,
                "ANSWER1": ANSWER_1,
                "ANSWER2": ANSWER_2,
                "ANSWER3": ANSWER_3,
                "ANSWER4": ANSWER_4,
                "ANSWER5": ANSWER_5,
                "ANSWER6": ANSWER_6,
                "ANSWER7": ANSWER_7,
                "ANSWER8": ANSWER_8,
                "ANSWER9": ANSWER_9,
                "ANSWER10": ANSWER_10,
                "OPENNESS": OPENNESS,
                "CONSCIENTIOUSNESS": CONSCIENTIOUSNESS,
                "EXTRAVERSION": EXTRAVERSION,
                "AGREEBLENESS": AGREEBLENESS,
                "NEUROTICISM": NEUROTICISM
            }
            
            success = insert_candidate_data(candidate_data, engine)
            if success:
                # Prepare data for Google Sheets insertion
                sheet_data = [list(candidate_data.values())]
                worksheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
                worksheet.append_row(sheet_data[0])
                st.success("Candidate details successfully submitted! Thank you.")
                time.sleep(5)
                st.experimental_rerun()
            else:
                st.warning("A candidate with this name already exists.")
