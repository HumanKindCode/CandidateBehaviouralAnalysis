import streamlit as st
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pandas as pd
import random
import uuid

Base = declarative_base()
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
# PostgreSQL database connection setup
def connect_to_db():
    PGEND_POINT = "database-1.clm0wcc6k54c.ap-southeast-2.rds.amazonaws.com"
    PGDATABASE_NAME = "CandidPersonaAnalysis"
    PGUSER_NAME = 'mike'
    PGPASSWORD = 'HumanKind25'
    DB_PORT = "5432"
    
    # Format for connection string: "postgresql://user:password@host:port/database_name"
    engine = create_engine(f'postgresql://{PGUSER_NAME}:{PGPASSWORD}@{PGEND_POINT}:{DB_PORT}/{PGDATABASE_NAME}')
    Base.metadata.create_all(engine)
    return engine

# Candidate model
class Candidate(Base):

    __tablename__ = 'candidates'
    # id = Column(Integer)
    uniqueid = Column(String, primary_key=True)
    candidate_name = Column(String)
    answer1 = Column(String)
    answer2 = Column(String)
    answer3 = Column(String)
    answer4 = Column(String)
    answer5 = Column(String)
    answer6 = Column(String)
    answer7 = Column(String)
    answer8 = Column(String)
    answer9 = Column(String)
    answer10 = Column(String)
    openness = Column(String)
    conscientiousness = Column(String)
    extraversion = Column(String)
    agreeableness = Column(String)
    neuroticism = Column(String)

# Function to insert data into the database
def insert_candidate_data(candidate_data, engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_candidate = session.query(Candidate).filter(Candidate.candidate_name == candidate_data["candidate_name"]).first()
    if existing_candidate is not None:
        session.close()
        return False
    new_candidate = Candidate(**candidate_data)
    session.add(new_candidate)
    session.commit()
    session.close()
    return True

# Connect to the PostgreSQL database
engine = connect_to_db()

# Streamlit app setup
st.title("Candidate Psyche Analysis")

# Example questions and options (simplified for brevity)
# Add the rest of your question types here


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

    unique_id = str(uuid.uuid4())
# After the form is submitted:
    if st.form_submit_button("Submit Candidate Details"):
        candidate_data = {
            "uniqueid": unique_id,
            "candidate_name": candidate_name,
            "answer1": ANSWER_1,
            "answer2": ANSWER_2,
            "answer3": ANSWER_3,
            "answer4": ANSWER_4,
            "answer5": ANSWER_5,
            "answer6": ANSWER_6,
            "answer7": ANSWER_7,
            "answer8": ANSWER_8,
            "answer9": ANSWER_9,
            "answer10": ANSWER_10,
            "openness": OPENNESS,
            "conscientiousness": CONSCIENTIOUSNESS,
            "extraversion": EXTRAVERSION,
            "agreeableness": AGREEBLENESS,
            "neuroticism": NEUROTICISM,
        }

        # Now call the insert function with the correct data
        success = insert_candidate_data(candidate_data, engine)
        if success:
            st.success("Candidate data inserted successfully.")
        else:
            st.error("Candidate data insertion failed. The candidate may already exist.")


