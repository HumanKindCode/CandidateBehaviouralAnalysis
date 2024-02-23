import streamlit as st
import redis
import os
from langchain.llms import OpenAI
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import openai
import pandas as pd
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import gspread
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv, find_dotenv
import spacy
from spacy import displacy
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains import SequentialChain, LLMChain
# nlp = spacy.load("en_core_web_sm")
import re
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.chains import SequentialChain, LLMChain
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from langchain.callbacks import ContextCallbackHandler
import plotly.graph_objs as go
from plotly.subplots import make_subplots
load_dotenv(find_dotenv(), override=True)
# from langchain.callbacks.confident_callback import DeepEvalCallbackHandler
# from deepeval.metrics.answer_relevancy import AnswerRelevancy
import pymongo
from pymongo import MongoClient
import plotly.express as px
import json  
import os
# from langchain.callbacks import LLMonitorCallbackHandler
# from langchain_openai import OpenAI
# from langchain_openai import ChatOpenAI
from langchain.callbacks import LLMonitorCallbackHandler
import random
import string
from oauth2client.service_account import ServiceAccountCredentials
# Fetch existing data from Google Sheets

openai.api_key = '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'
answer_mappings  = {
    "QUESTION1_TYPES": {
        "Embraced the change and led the transition.": 5,
        "Adapted gradually with some resistance.": 4,
        "Found it challenging and preferred previous methods.": 3,
        "Struggled significantly and needed extensive support.": 2,
    },
    "QUESTION2_TYPES": {
        "Leader, guiding the team towards goals.": 5,
        "Collaborator, working closely with others.": 4,
        "Independent contributor, working on tasks alone.": 3,
        "Supporter, helping others with their tasks.": 2,
    },
    "QUESTION3_TYPES": {
        "Analyzed the problem and devised a strategic solution.": 5,
        "Brainstormed with the team for collective solutions.": 4,
        "Used tried-and-tested methods to address the issue.": 3,
        "Required guidance to find an appropriate solution.": 2,
    },
    "QUESTION4_TYPES": {
        "Direct and honest while being respectful.": 5,
        "Tactful and considerate, softening the message.": 4,
        "Hesitant and prefer to avoid confrontation.": 3,
        "Seek guidance or delegate the task to others.": 2,
    },
    "QUESTION5_TYPES": {
        "View setbacks as learning opportunities.": 5,
        "Remain optimistic and try again.": 4,
        "Feel discouraged but eventually recover.": 3,
        "Get significantly affected and demotivated.": 2,
    },
    "QUESTION6_TYPES": {
        "Always seek consensus.": 5,
        "Mostly seek consensus, but can be authoritative.": 4,
        "Balanced between consensus-seeking and authoritative.": 3,
        "Mostly authoritative, but can seek consensus.": 2,
        "Always authoritative.": 1,
    },
    "QUESTION7_TYPES": {
        "Always prefer groups.": 5,
        "Mostly prefer groups, but can work independently.": 4,
        "Equally comfortable in groups or working independently.": 3,
        "Mostly prefer working independently, but can work in groups.": 2,
        "Always prefer working independently.": 1,
    },
    "QUESTION8_TYPES": {
        "Always openly and expressively.": 5,
        "Mostly openly, but can be reserved.": 4,
        "Balanced between expressive and reserved.": 3,
        "Mostly reserved, but can be expressive.": 2,
        "Always reserved.": 1,
    },
    "QUESTION9_TYPES": {
        "Always rely on empathy.": 5,
        "Mostly rely on empathy, but can be rational.": 4,
        "Balanced between empathy and rational thinking.": 3,
        "Mostly rely on rational thinking, but can be empathetic.": 2,
        "Always rely on rational thinking.": 1,
    },
    "QUESTION10_TYPES": {
        "Always flexible and open to change.": 5,
        "Mostly flexible, but can be determined.": 4,
        "Balanced between flexibility and determination.": 3,
        "Mostly determined, but can be flexible.": 2,
        "Always determined.": 1,
    }
}
trait_questions = {
    "Openness": ['ANSWER1', 'ANSWER10', 'ANSWER3'],
    "Conscientiousness": ['ANSWER6', 'ANSWER7', 'ANSWER3'],
    "Extraversion": ['ANSWER2', 'ANSWER8'],
    "Agreeableness": ['ANSWER4', 'ANSWER9'],
    "Neuroticism": ['ANSWER5'],
}
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

def format_candidate_data(row):
    # Return a dictionary of candidate details instead of a formatted string
    return {
        "Candidate Name": row['CandidateName'],
        "Openness": row['OPENNESS'],
        "Conscientiousness": row['CONSCIENTIOUSNESS'],
        "Extraversion": row['EXTRAVERSION'],
        "Agreeableness": row['AGREEABLENESS'],
        "Neuroticism": row['NEUROTICISM']
    }

def calculate_average(questions, data):
    total_score = 0
    for question in questions:
        total_score += int(data[question])  # Convert answer to integer. Adjust conversion as needed based on your data
    return total_score / len(questions)

def extract_score_from_text(text):
    # Search for a pattern that identifies the score in the text
    match = re.search(r'\b\d+(\.\d+)?\b', text)
    if match:
        return float(match.group())
    else:
        return None

def generate_random_id(length=8):
    """Generate a random string of letters and digits."""
    characters = string.ascii_letters + string.digits  # Include both letters and digits
    return ''.join(random.choice(characters) for i in range(length))

spreadsheet_id = "1Ou0ZXVcLPkhdARBPnhfrp8cGq-zG2hPMnezQI8SZp2I"
worksheet_name = "Sheet1"
existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)

def calculate_big_five_scores(candidate_data):

        
        big_five_scores = {trait: 0 for trait in trait_questions.keys()}
        for trait, questions in trait_questions.items():
            scores = []  # List to store scores for the current trait
            for question in questions:
                response = candidate_data[question]
                question_num = question.replace('ANSWER', '')
                question_type = f"QUESTION{question_num}_TYPES"
                score = answer_mappings[question_type].get(response, 0)  # Default to 0 if the response is not in the mapping
                scores.append(score)
            # Avoid division by zero
            if scores:
                big_five_scores[trait] = sum(scores) / len(scores)
        return big_five_scores   
    
def main():
    # Streamlit app layout setup
    st.header("Team Analysis")
   
    # Load candidate names from the Google Sheets data

    # Dropdown for candidate selection
    client = init_gspread_connection()
    spreadsheet_id = "1Ou0ZXVcLPkhdARBPnhfrp8cGq-zG2hPMnezQI8SZp2I"
    worksheet_name = "Sheet1"
    existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
    candidate_names = existing_data['CandidateName'].unique()
    selected_candidates = st.multiselect("Select a Candidate:", candidate_names)


    # Fetch and display candidate details

            
    if selected_candidates:


            # Placeholder for plots
            plot_placeholder = st.empty()
            if selected_candidates:
                all_scores_df = pd.DataFrame()  # DataFrame to hold all scores for plotting
                for candidate in selected_candidates:
                    candidate_data = existing_data[existing_data['CandidateName'] == candidate].iloc[0]
                    big_five_scores = calculate_big_five_scores(candidate_data)
                    data = [{'Candidate': candidate, 'Trait': trait, 'Score': score} for trait, score in big_five_scores.items()]
                    candidate_scores_df = pd.DataFrame(data)
                    all_scores_df = pd.concat([all_scores_df, candidate_scores_df], ignore_index=True)

                # Plotting the scores for each trait for all selected candidates
                fig = px.bar(all_scores_df, x='Trait', y='Score', color='Candidate', barmode='group',
                            text='Score', title="Big Five Personality Traits Scores",
                            labels={'Score': 'Score', 'Trait': 'Personality Trait', 'Candidate': 'Candidate'})
                fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                                yaxis=dict(title='Score', range=[0, 6]),  # Adjusting range based on your scoring system
                                xaxis=dict(title='Personality Trait'))
                plot_placeholder.plotly_chart(fig)



            columns_of_interest = [
                'Openness-LLM-Answer',
                'Conscientiousness-LLM-Answer',
                'Extraversion-LLM-Answer',
                'Agreebleness-LLM-Answer',
                'Neuroticism-LLM-Answer'
            ]

            new_json_structure = {}  # Initialize a dictionary to hold the processed data

            for selected_candidate in selected_candidates:
                # Initialize the candidate's structure if not already present
                if selected_candidate not in new_json_structure:
                    new_json_structure[selected_candidate] = {}
                
                candidate_data = existing_data[existing_data['CandidateName'] == selected_candidate]
                
                if not candidate_data.empty:
                    selected_candidate_data = candidate_data.iloc[0]
                    
                    for column_name in columns_of_interest:
                        big5category = column_name.split('-')[0]
                        json_str = selected_candidate_data[column_name]
                        column_data = json.loads(json_str)
                        
                        criteria_list = []
                        
                        for criteria, details in column_data.items():
                            if criteria.lower() == 'answer':
                                continue
                            criteria_dict = {
                                "criteria": criteria,
                                "score": details['score'],
                            }
                            criteria_list.append(criteria_dict)
                        
                        # Here, we ensure each Big Five category under a candidate is correctly initialized
                        if big5category not in new_json_structure[selected_candidate]:
                            new_json_structure[selected_candidate][big5category] = []
                        
                        new_json_structure[selected_candidate][big5category].extend(criteria_list)
                        
            summed_scores = {candidate: {} for candidate in new_json_structure.keys()}

            for candidate, categories in new_json_structure.items():
                for category, criteria_list in categories.items():
                    total_score = sum(int(criteria['score']) for criteria in criteria_list)
                    summed_scores[candidate][category] = total_score
            df = pd.DataFrame(summed_scores).fillna(0)  # Ensure all missing values are filled with 0
            df = df.T

            # Preparing hover text for each candidate and category
            hover_info = {}
            for candidate, categories in new_json_structure.items():
                if candidate not in hover_info:
                    hover_info[candidate] = {}
                for category, details in categories.items():
                    # Calculate the sum of scores for the category
                    total_score = sum(int(detail['score']) for detail in details)
                    # Prepare hover text with criteria details
                    criteria_details = "<br>".join([f"{detail['criteria']}: {detail['score']}" for detail in details])
                    # Append the total score to the hover text
                    hover_text = f"{criteria_details}<br>Total Score: {total_score}"
                    hover_info[candidate][category] = hover_text
                    
            fig = go.Figure()

            for category in df.columns:
                custom_hover_texts = [hover_info[candidate].get(category, "Total Score: 0") for candidate in df.index]
                
                
                fig.add_trace(go.Bar(
                    x=df.index,
                    y=df[category],
                    name=category,
                    customdata=custom_hover_texts,
                    hovertemplate='%{customdata}<extra></extra>',  # Use customdata in hovertemplate, hide secondary info with <extra></extra>
                ))

            # Update layout for the stacked bar chart
            fig.update_layout(
                barmode='stack',
                title='Sum of Scores per Big Five Category for Each Candidate',
                xaxis_title='Candidate',
                yaxis_title='Sum of Scores',
                legend_title='Big Five Categories'
            )

            # Display the chart in Streamlit
            st.plotly_chart(fig)

            # Assuming st.write is a placeholder for displaying the structure, e.g., in Streamlit
            # st.write(new_json_structure)

            # At this point, new_json_structure contains the transformed data
                # You can now display this data using Streamlit or process it further as needed
                
                
                

                # st.write(new_json_structure)
                # st.write(selected_candidate_data)

                # Now all_scores_df contains all the data from selected candidates
                # Let the user select which TraitGroups to include in the chart
                    # Let the user select which TraitGroups to include in the chart


        
if __name__ == "__main__":
    main()
