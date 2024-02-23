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


def get_llm_response_openness(openness_text):
    # llm = ChatOpenAI(openai_api_key="your-openai-api-key")

    # Initialize the language model
    llm = ChatOpenAI(openai_api_key="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")

    # Define the criteria and their detailed evaluation instructions
    negative_criteria_details = {
        "Willingness to Learn": """Score 10: Demonstrates exceptional enthusiasm and proactive attitude towards learning new technologies, consistently seeks out and embraces new challenges.
                                    Score 9: Very eager to learn, often goes above and beyond to acquire new skills and knowledge.
                                    Score 8: Shows strong willingness and regularly engages in learning new technologies.
                                    Score 7: Generally open to learning, occasionally shows innovative approaches to new challenges.
                                    Score 6: Fairly open to learning but may require some encouragement or support.
                                    Score 5: Average willingness, shows interest but lacks consistency in seeking new knowledge.
                                    Score 4: Somewhat reluctant to learn new things, often needs persuasion and external motivation.
                                    Score 3: Rarely shows interest in learning, tends to avoid new challenges.
                                    Score 2: Demonstrates a clear disinterest in learning, resistant to adopting new methods.
                                    Score 1: Completely closed off to learning, unwilling to engage with new technologies or ideas.""",
                                    
        "Problem-Solving Skills": """Score 10: Exhibits exceptional problem-solving skills with innovative and practical solutions.
                                    Score 9: Very effective, often employs novel strategies with successful outcomes.
                                    Score 8: Consistently demonstrates good problem-solving abilities, effective under various scenarios.
                                    Score 7: Generally effective but may occasionally lack creative solutions.
                                    Score 6: Shows competency in familiar situations, but struggles with complex or novel problems.
                                    Score 5: Sometimes effective but often requires guidance and support.
                                    Score 4: Struggles with independent problem-solving, lacks practical strategies.
                                    Score 3: Has difficulty in addressing problems, often overlooks key aspects.
                                    Score 2: Shows poor problem-solving skills, often gives up easily.
                                    Score 1: Unable to effectively address problems, lacks both creativity and practicality.
                                    """,
        "Adaptability and Flexibility": """Score 10: Exhibits exceptional adaptability; seamlessly adjusts to new technologies and environments, and uses changes as an opportunity for innovative solutions.
                                    Score 9: Highly adaptable and flexible; quickly and effectively adjusts to new situations, demonstrating a positive attitude towards change.
                                    Score 8: Shows strong adaptability; often adjusts well to new technologies, displaying a readiness to embrace new challenges.
                                    Score 7: Generally adapts well to change; occasionally needs time but usually finds effective ways to work in new environments.
                                    Score 6: Displays a moderate level of adaptability; can adjust to new situations but may require support or additional time.
                                    Score 5: Shows average adaptability; struggles with unfamiliar environments but manages to cope with assistance.
                                    Score 4: Demonstrates limited adaptability; often resists change and struggles to adjust to new technologies or environments.
                                    Score 3: Has difficulty adapting; shows rigidity in thinking and a reluctance to depart from known methods.
                                    Score 2: Displays poor adaptability; frequently unable to adjust to new situations, often overwhelmed by changes.
                                    Score 1: Exhibits almost no adaptability; resists change at all costs, unable to function effectively in new or changing environments.
                                    """,
        "Resource Utilization": """Score 10: Exceptionally effective in utilizing available resources; consistently leverages colleagues' expertise, online forums, and professional networks to enhance outcomes.
                                    Score 9: Highly skilled in resource utilization; frequently taps into various resources for information, advice, and problem-solving.
                                    Score 8: Shows strong ability in using available resources; often seeks out and effectively uses external knowledge and support.
                                    Score 7: Generally good at utilizing resources; sometimes needs prompting but usually makes good use of external help.
                                    Score 6: Moderately effective in resource utilization; benefits from resources but not consistently proactive in seeking them out.
                                    Score 5: Average in using resources; occasionally leverages external help but often overlooks potential aids.
                                    Score 4: Limited in resource utilization; infrequently uses external resources and often relies solely on personal knowledge.
                                    Score 3: Struggles with effective resource utilization; rarely seeks out external assistance or fails to use it effectively.
                                    Score 2: Poor in using available resources; frequently overlooks or undervalues external help, often resulting in suboptimal outcomes.
                                    Score 1: Extremely poor in resource utilization; neglects available resources, consistently relies on limited personal knowledge, and fails to seek external assistance.
                                    """,
        "Collaboration and Teamwork": """Score 10: Demonstrates exceptional collaboration skills; actively engages with team members, excels in sharing knowledge, and consistently supports and enhances team efforts.
                                    Score 9: Highly effective in teamwork; regularly contributes valuable insights, works cooperatively, and frequently assists others in the team.
                                    Score 8: Very good at collaborating; often participates actively in team activities and is willing to help team members.
                                    Score 7: Generally collaborates well; participates in team efforts and occasionally takes the initiative to support others.
                                    Score 6: Shows average collaboration skills; participates in teamwork but may not actively seek opportunities to assist others.
                                    Score 5: Moderately effective in teamwork; cooperates with the team but rarely goes beyond basic expectations.
                                    Score 4: Limited collaboration; sometimes works with the team but often prefers to work independently, showing reluctance in sharing or seeking help.
                                    Score 3: Poor at teamwork; infrequently engages in collaborative efforts and rarely offers help to others, preferring to work alone.
                                    Score 2: Very poor collaboration skills; shows little interest in teamwork, often causing friction or disengagement within the team.
                                    Score 1: Extremely poor in teamwork; avoids collaboration, does not participate in team activities, and fails to support or contribute to team objectives.
                                    """,
        "Proactive Approach": """Score 10: Exemplifies outstanding proactivity; consistently anticipates challenges, seeks information in advance, and takes initiative to address issues before they arise.
                                    Score 9: Highly proactive; regularly prepares for potential obstacles and actively seeks opportunities for improvement and growth.
                                    Score 8: Very good at taking initiative; often anticipates future needs and acts ahead of time to address them.
                                    Score 7: Generally proactive; usually prepares in advance and is willing to take steps to mitigate potential issues.
                                    Score 6: Displays average proactivity; sometimes takes initiative but may not consistently plan or anticipate future challenges.
                                    Score 5: Moderately proactive; occasionally shows foresight but often reacts to situations as they occur rather than preparing in advance.
                                    Score 4: Shows limited proactivity; infrequently seeks information ahead of time and often responds to situations only after they arise.
                                    Score 3: Lacks a proactive approach; rarely anticipates challenges or seeks information in advance, often waiting for direction.
                                    Score 2: Very poor in taking initiative; mostly reactive, tends to wait for issues to occur before addressing them.
                                    Score 1: Extremely lacking in proactivity; does not seek information, fails to anticipate challenges, and shows no initiative in addressing potential problems.
                                    """,
        "Risk Management and Critical Thinking": """Score 10: Demonstrates exceptional skill in identifying potential risks and devising comprehensive strategies to mitigate them. Shows outstanding critical thinking in analyzing and solving complex problems.
                                    Score 9: Highly proficient in risk management; regularly anticipates potential issues and develops effective contingency plans. Exhibits strong critical thinking skills.
                                    Score 8: Very good at identifying risks and developing strategies to address them. Often uses critical thinking to analyze and approach problems effectively.
                                    Score 7: Generally effective in risk management; usually identifies significant risks and thinks critically to resolve issues, though may miss finer details.
                                    Score 6: Displays average ability in identifying risks and using critical thinking. Sometimes overlooks potential issues but can manage commonly encountered problems.
                                    Score 5: Moderately effective in risk management; recognizes obvious risks but struggles with complex risk assessment and critical problem-solving.
                                    Score 4: Limited in risk management skills; occasionally identifies risks but often fails to develop effective strategies. Shows basic critical thinking ability.
                                    Score 3: Poor in assessing risks; rarely identifies potential pitfalls and struggles to think critically about complex issues.
                                    Score 2: Very poor in risk management; overlooks key risks and lacks the ability to think critically about solutions.
                                    Score 1: Extremely poor in both risk management and critical thinking; fails to recognize risks and cannot effectively analyze or solve problems.
                                    """,
        "Creativity and Innovation": """Score 10: Displays exceptional creativity and innovation; consistently offers unique and forward-thinking ideas, and sees unconventional but practical applications of technology.
                                    Score 9: Highly creative; regularly contributes innovative solutions and demonstrates a keen understanding of how to apply new technologies in novel ways.
                                    Score 8: Very good at generating creative ideas; often proposes innovative approaches and sees beyond conventional uses of technology.
                                    Score 7: Generally demonstrates creativity; shows the ability to think outside the box and occasionally comes up with original ideas.
                                    Score 6: Displays average creativity; sometimes suggests new ideas but tends to stick to conventional approaches.
                                    Score 5: Moderately creative; capable of innovation but often relies on existing ideas and standard applications.
                                    Score 4: Limited creativity; infrequently suggests new ideas and lacks a forward-thinking approach.
                                    Score 3: Lacks creativity; rarely proposes innovative solutions and struggles to see beyond traditional uses of technology.
                                    Score 2: Very poor in creativity and innovation; shows little to no original thinking and fails to see potential in applying technology in new ways.
                                    Score 1: Completely lacking in creativity and innovation; offers no original ideas and is unable to think beyond established methods and applications.
                                    """,
        "Resilience and Persistence": """Score 10: Demonstrates exceptional resilience; faces challenges head-on with a positive attitude, quickly rebounds from setbacks, and persistently pursues goals despite obstacles.
                                    Score 9: Highly resilient; consistently shows determination in difficult situations and maintains a positive outlook, overcoming challenges effectively.
                                    Score 8: Very good at persisting; regularly tackles obstacles with a constructive attitude and rarely gives up, even under tough circumstances.
                                    Score 7: Generally resilient; usually maintains focus and effort in the face of difficulties, though may occasionally need encouragement.
                                    Score 6: Displays average resilience; sometimes struggles with setbacks but manages to continue in most cases.
                                    Score 5: Moderately resilient; capable of persistence but often needs support to overcome challenges and maintain motivation.
                                    Score 4: Limited resilience; tends to get discouraged by difficulties and may give up if not supported.
                                    Score 3: Lacks resilience; often gives up in the face of challenges and struggles to maintain a positive attitude during tough times.
                                    Score 2: Very poor resilience; frequently avoids challenges, quickly loses motivation, and often exhibits a negative attitude when faced with difficulties.
                                    Score 1: Extremely poor in both resilience and persistence; almost always gives up when faced with obstacles, lacks the ability to cope with setbacks, and maintains a consistently negative outlook.
                                    """,
        "Communication Skills": """Score 10: Exhibits exceptional communication skills; articulates ideas clearly and effectively, effortlessly simplifies complex concepts, and engages the audience with compelling and coherent strategies.
                                    Score 9: Highly skilled in communication; consistently clear and effective, makes complex topics easily understandable, and presents ideas in a well-structured and engaging manner.
                                    Score 8: Very good communicator; regularly expresses ideas clearly, effectively breaks down complex ideas, and conveys strategies coherently.
                                    Score 7: Generally communicates well; usually clear and effective, but may occasionally struggle with complex concepts or lack engagement in presentation.
                                    Score 6: Displays average communication skills; sometimes expresses ideas clearly but may struggle with complexity or lack consistency in clarity and effectiveness.
                                    Score 5: Moderately effective in communication; capable of articulating ideas but often lacks clarity or struggles to simplify complex topics.
                                    Score 4: Limited communication skills; frequently struggles to express ideas clearly, often fails to break down complex concepts, and lacks coherence in conveying strategies.
                                    Score 3: Poor communicator; regularly unclear and ineffective, struggles significantly with complexity, and often fails to present ideas in a coherent manner.
                                    Score 2: Very poor communication skills; consistently unclear, fails to simplify complex ideas, and lacks structure and relevance in communication.
                                    Score 1: Extremely poor in communication; almost always fails to convey ideas clearly, shows no ability to handle complex topics, and lacks any coherent or engaging communication strategy.
                                    """,
        "Overall Assessment": """10 - Exceptional Leader: Demonstrates outstanding leadership qualities across all criteria. Exhibits a superior balance of skills, including adaptability, problem-solving, team dynamics management, and motivational ability. Fits exceptionally well with organizational culture and shows exceptional potential for future leadership roles.
                                    9 - Highly Effective Leader: Shows strong leadership abilities in nearly all aspects. Minor areas for improvement may exist, but overall, the candidate demonstrates a high level of competence and a strong fit with the organizational culture.
                                    8 - Very Good Leader: Consistently exhibits good leadership qualities. There are some areas for improvement, but the candidate shows a solid understanding of effective leadership and aligns well with the team and organizational culture.
                                    7 - Good Leader: Generally effective in leadership roles. Demonstrates competency in most areas but may lack depth in some aspects of leadership. Good cultural fit with potential for further development.
                                    6 - Competent Leader: Shows adequate leadership skills. Effective in familiar settings, but may struggle with more complex leadership challenges. Reasonable fit with organizational culture with some areas for growth.
                                    5 - Moderate Leader: Demonstrates some leadership abilities but is inconsistent. Needs guidance and development in several areas. Moderate fit with the culture and needs improvement to realize full potential.
                                    4 - Below Average Leader: Exhibits basic leadership skills but lacks consistency and effectiveness in several areas. Cultural fit is uncertain and requires significant development.
                                    3 - Limited Leadership Ability: Struggles in various aspects of leadership. Shows limited understanding and application of effective leadership principles. Cultural fit is questionable.
                                    2 - Poor Leader: Demonstrates poor leadership skills across most areas. Rarely effective in a leadership role and does not align well with organizational culture.
                                    1 - Ineffective Leader: Lacks essential leadership qualities. Fails to demonstrate effective leadership in any of the evaluated areas and is a poor fit for the organizational culture.
                                    """
    }

    # Define a strict and rational evaluation prompt with detailed criteria
    evaluation_prompt_template = """
    Consider the candidate's response to the question: 'Imagine you are offered an opportunity to work on a project that involves new and unfamiliar technology. How would you approach this situation?'

    Candidate's Response: {openness_text}

    Please evaluate the candidate's answer on a scale from 1 to 10 for its adherence to the criterion of '{criterion}'. Refer to the following scoring guidelines:

    {details}

    Based on these guidelines, provide a score and a detailed explanation for the score given.

    Detailed Evaluation for '{criterion}':
    """
    
    return llm, negative_criteria_details, evaluation_prompt_template

def get_llm_response_conscientiousness(conscientiousness_text):
    # llm = ChatOpenAI(openai_api_key="your-openai-api-key")

    # Initialize the language model
    llm = ChatOpenAI(openai_api_key="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")
    # Define the criteria and their detailed evaluation instructions

    negative_criteria_details = {
        "Leadership Style": """10 - Exceptional: The candidate demonstrates an exceptional understanding and application of various leadership styles. This is evident through clear and varied examples that showcase their adaptability to different situations.
                                9 - Strong: The candidate shows a strong grasp of leadership styles with several adaptability examples. Minor gaps may be present in their application.
                                8 - Good: There is a good understanding of leadership styles, but the examples provided are somewhat limited or lack variety.
                                7 - Adequate: The understanding is adequate, with basic examples. However, some key leadership styles are not addressed.
                                6 - Moderate: The candidate has a moderate understanding, but the examples provided lack depth or specificity.
                                5 - Basic: The understanding is basic, with limited or generic examples that do not fully demonstrate their grasp of leadership styles.
                                4 - Minimal: There is minimal understanding, and the examples provided are vague or irrelevant to the context of leadership.
                                3 - Poor: The candidate shows poor understanding with little to no relevant examples to substantiate their knowledge of leadership styles.
                                2 - Very Limited: Understanding is very limited, with no relevant examples provided.
                                1 - None: There is no evidence of understanding leadership styles, with no examples or relevant insights offered.""",
                                    
        "Understanding Team Dynamics": """10 - Exceptional Insight: Demonstrates exceptional problem-solving skills with innovative and practical solutions, showing a deep understanding of team dynamics and effectively leveraging them.
                                            9 - Very Effective: Regularly employs novel strategies with successful outcomes, showing a strong grasp of team dynamics and their effective management.
                                            8 - Consistently Good: Consistently demonstrates good problem-solving abilities in various scenarios, effectively understanding and managing team dynamics.
                                            7 - Generally Effective: Generally effective but may occasionally lack creative solutions in managing team dynamics.
                                            6 - Competent in Familiar Settings: Shows competency in familiar situations but struggles with complex dynamics or novel team challenges.
                                            5 - Moderately Effective: Sometimes effective but often requires guidance and support in understanding and managing team dynamics.
                                            4 - Struggles with Independence: Struggles with independent problem-solving in team settings, lacks practical strategies for managing dynamics.
                                            3 - Difficulty in Problem-Solving: Has difficulty in addressing problems in team dynamics, often overlooks key aspects.
                                            2 - Poor Problem-Solving Skills: Shows poor problem-solving skills in team settings, often gives up easily or fails to engage effectively with team dynamics.
                                            1 - Ineffective: Unable to effectively address problems in team dynamics, lacks both creativity and practicality in understanding and managing these dynamics.""",
       

        "Goal Setting": """10 - Exceptional Goal Setter: Demonstrates an outstanding ability to set and communicate clear, strategic, and achievable goals. Shows evidence of aligning goals with organizational objectives and individual team members' strengths, leading to high engagement and successful outcomes.
                            9 - Highly Effective: Sets clear and effective goals that are well-communicated and aligned with team capabilities and organizational needs. Shows adaptability in goal setting to meet changing circumstances.
                            8 - Very Good: Consistently sets and communicates clear goals. There may be minor gaps in aligning these goals with broader objectives or individual strengths.
                            7 - Good: Sets reasonable goals that are generally clear and achievable. Demonstrates a basic alignment with team and organizational needs, but may lack some detail or adaptability.
                            6 - Competent: Shows competency in setting goals that are mostly clear and achievable. However, struggles with more complex goal-setting scenarios or in fully engaging the team with these goals.
                            5 - Moderately Effective: Sets goals that are occasionally unclear or not fully aligned with team capabilities. Inconsistency in communicating and driving these goals may be evident.
                            4 - Inconsistent: Demonstrates a basic understanding of goal setting but lacks consistency and effectiveness. Goals may be too vague, unachievable, or poorly communicated.
                            3 - Limited Effectiveness: Shows limited effectiveness in setting and communicating goals. Goals often lack clarity, alignment with team strengths, or are not compelling.
                            2 - Poor: Struggles significantly with setting effective goals. Goals set are often unclear, unrealistic, or irrelevant to team and organizational objectives.
                            1 - Ineffective Goal Setter: Displays a lack of understanding and ability in setting and communicating goals. Fails to establish meaningful or achievable goals, leading to confusion and disengagement in the team.""",
        
        "Delegation Skills": """10 - Exceptional Delegator: Demonstrates superior delegation skills. Allocates tasks based on a deep understanding of individual team members' strengths, skills, and development needs. Ensures a balanced workload while maximizing team efficiency and individual growth.
                                9 - Highly Effective: Shows strong delegation abilities. Tasks are well-matched to team members' capabilities and promote their development. There is minor room for improvement in balancing workload or team development.
                                8 - Very Good: Consistently delegates effectively. Tasks are generally aligned with team members' skills, but there may be occasional mismatches or less consideration for personal development.
                                7 - Good: Delegates tasks appropriately most of the time. Shows understanding of team members' capabilities but may lack finesse in optimizing task allocation for personal growth or team efficiency.
                                6 - Competent: Competently delegates tasks, but effectiveness is limited to familiar scenarios. Struggles with delegation in complex situations or with less familiar team members.
                                5 - Moderately Effective: Shows some ability to delegate, but inconsistencies are evident. Tasks are not always well-suited to individuals, leading to inefficiencies or missed development opportunities.
                                4 - Inconsistent: Demonstrates basic delegation skills but lacks consistency. Some tasks are appropriately assigned, while others are poorly matched to team members' skills.
                                3 - Limited Effectiveness: Struggles with effective delegation. Task assignments often fail to consider individual strengths or team dynamics, leading to suboptimal outcomes.
                                2 - Poor: Shows poor delegation skills. Frequently assigns tasks inappropriately, leading to inefficiency, frustration among team members, or hindered team progress.
                                1 - Ineffective Delegator: Lacks delegation skills entirely. Assignments are consistently mismatched, leading to widespread inefficiencies and demotivation in the team.""",
        
        "Problem-Solving and Decision-Making": """10 - Exceptional Problem-Solving and Decision-Making: Demonstrates superior problem-solving skills with innovative, effective solutions. Makes decisions that are well-informed, timely, and demonstrate a deep understanding of complex situations. Shows exceptional analytical and critical thinking skills.
                                                    9 - Highly Effective: Exhibits strong problem-solving abilities with creative and practical solutions. Decisions are well-considered and generally effective, with minor areas for improvement in complex scenarios.
                                                    8 - Very Good: Consistently shows good problem-solving skills. Makes sound decisions but may occasionally miss finer details or more creative solutions in complex situations.
                                                    7 - Good: Generally effective in solving problems and making decisions. Shows competency but may lack depth in analysis or creativity in more challenging scenarios.
                                                    6 - Competent: Demonstrates adequate problem-solving skills in familiar situations. Decisions are reasonable but may struggle with complexity or under pressure.
                                                    5 - Moderately Effective: Shows some ability in problem-solving and decision-making but often requires guidance. Struggles with more complex problems or under high-pressure situations.
                                                    4 - Inconsistent: Demonstrates basic skills but lacks consistency. Problem-solving and decisions are often simplistic and may not consider all aspects of a situation.
                                                    3 - Limited Effectiveness: Has limited problem-solving abilities. Decisions are often poorly informed or delayed, leading to suboptimal outcomes.
                                                    2 - Poor: Struggles significantly with problem-solving and decision-making. Rarely arrives at effective solutions or makes timely decisions.
                                                    1 - Ineffective: Displays a lack of problem-solving and decision-making skills. Unable to effectively address problems or make informed decisions, often leading to negative outcomes.""",
                                                    
        "Monitoring and Feedback": """10 - Exceptional Monitoring and Feedback: Demonstrates outstanding skills in monitoring team progress and providing constructive feedback. Employs comprehensive and effective strategies that foster individual growth and team development, leading to enhanced performance and goal attainment.
                                        9 - Highly Effective: Shows strong ability in monitoring and effective feedback delivery. Strategies are well-implemented, with minor areas for improvement in ensuring continuous development and engagement.
                                        8 - Very Good: Consistently effective in monitoring team progress and providing feedback. There may be occasional gaps in tracking or feedback specificity.
                                        7 - Good: Generally effective in monitoring and feedback. Capable of maintaining team progress, but may lack depth or frequency in feedback to maximize development opportunities.
                                        6 - Competent: Demonstrates adequate skills in monitoring and providing feedback. Effective in familiar settings but may struggle with adapting strategies to different team members or complex projects.
                                        5 - Moderately Effective: Shows some ability in monitoring and feedback, but inconsistencies are evident. Feedback may be too general or infrequent to significantly aid in development.
                                        4 - Inconsistent: Demonstrates basic skills but lacks consistency in effective monitoring and feedback. Some aspects of team progress may be overlooked, and feedback may not be fully effective.
                                        3 - Limited Effectiveness: Has limited success in monitoring team progress and providing feedback. Often misses important developments and fails to provide timely or constructive feedback.
                                        2 - Poor: Struggles significantly with monitoring and feedback. Rarely identifies or addresses key team issues, leading to poor development and goal achievement.
                                        1 - Ineffective: Displays a lack of skills in monitoring and feedback. Fails to track team progress effectively and provides little to no constructive feedback, hindering team development and performance.""",
                                    
        "Conflict Resolution": """10 - Exceptional Conflict Resolver: Demonstrates outstanding conflict resolution skills. Skillfully navigates complex conflicts, finding solutions that are fair, effective, and preserve team harmony. Exhibits exceptional empathy, communication, and negotiation skills.
                                        9 - Highly Effective: Shows strong conflict resolution abilities. Effectively mediates disputes, with minor areas for improvement in handling more intricate or emotionally charged conflicts.
                                        8 - Very Good: Consistently resolves conflicts effectively. May occasionally miss more subtle emotional undercurrents or complex aspects of conflicts.
                                        7 - Good: Generally effective in resolving conflicts. Capable of mediating disputes but may lack depth in understanding all parties' perspectives in more complex situations.
                                        6 - Competent: Demonstrates adequate conflict resolution skills in familiar situations. Struggles with resolving more complex or intense conflicts.
                                        5 - Moderately Effective: Shows some ability in resolving conflicts but often requires additional support or guidance. Inconsistencies in handling complex situations.
                                        4 - Inconsistent: Demonstrates basic conflict resolution skills but lacks consistency. Some conflicts are resolved effectively, while others are mishandled or escalate.
                                        3 - Limited Effectiveness: Has limited success in resolving conflicts. Often fails to address the root causes of conflicts or to find sustainable solutions.
                                        2 - Poor: Struggles significantly with conflict resolution. Rarely manages to resolve conflicts effectively, leading to ongoing issues or team discord.
                                        1 - Ineffective Conflict Resolver: Displays a lack of conflict resolution skills. Unable to effectively manage disputes, often resulting in unresolved issues or detrimental impacts on team dynamics.""",

        "Overall Assessment": """10 - Exceptional Monitoring and Feedback: Demonstrates outstanding skills in monitoring team progress and providing constructive feedback. Employs comprehensive and effective strategies that foster individual growth and team development, leading to enhanced performance and goal attainment.
                                    9 - Highly Effective: Shows strong ability in monitoring and effective feedback delivery. Strategies are well-implemented, with minor areas for improvement in ensuring continuous development and engagement.
                                    8 - Very Good: Consistently effective in monitoring team progress and providing feedback. There may be occasional gaps in tracking or feedback specificity.
                                    7 - Good: Generally effective in monitoring and feedback. Capable of maintaining team progress, but may lack depth or frequency in feedback to maximize development opportunities.
                                    6 - Competent: Demonstrates adequate skills in monitoring and providing feedback. Effective in familiar settings but may struggle with adapting strategies to different team members or complex projects.
                                    5 - Moderately Effective: Shows some ability in monitoring and feedback, but inconsistencies are evident. Feedback may be too general or infrequent to significantly aid in development.
                                    4 - Inconsistent: Demonstrates basic skills but lacks consistency in effective monitoring and feedback. Some aspects of team progress may be overlooked, and feedback may not be fully effective.
                                    3 - Limited Effectiveness: Has limited success in monitoring team progress and providing feedback. Often misses important developments and fails to provide timely or constructive feedback.
                                    2 - Poor: Struggles significantly with monitoring and feedback. Rarely identifies or addresses key team issues, leading to poor development and goal achievement.
                                    1 - Ineffective: Displays a lack of skills in monitoring and feedback. Fails to track team progress effectively and provides little to no constructive feedback, hindering team development and performance.
                                    """
    }

    # Define a strict and rational evaluation prompt with detailed criteria
    evaluation_prompt_template = """
    Consider the candidate's response to the question: 'Describe how you would handle a situation where you have multiple deadlines approaching simultaneously?'

    Candidate's Response: {conscientiousness_text}

    Please evaluate the candidate's answer on a scale from 1 to 10 for its adherence to the criterion of '{criterion}'. Refer to the following scoring guidelines:

    {details}

    Based on these guidelines, provide a score and a detailed explanation for the score given.

    Detailed Evaluation for '{criterion}':
    """
    
    return llm, negative_criteria_details, evaluation_prompt_template

def get_llm_response_extraversion(extraversion_text):
    # llm = ChatOpenAI(openai_api_key="your-openai-api-key")

    # Initialize the language model
    llm = ChatOpenAI(openai_api_key="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")

    negative_criteria_details = {
        "Understanding of Effective Leadership": """10 - Exceptional Understanding: Demonstrates an outstanding grasp of effective leadership, particularly in areas influenced by extraversion. Exhibits a natural ability to energize, inspire, and lead teams with charisma. Their leadership style is adaptive, inclusive, and highly motivating.
                                                    9 - Highly Effective Understanding: Shows a strong understanding of leadership, with a clear ability to use extraverted qualities to engage and lead teams effectively. Minor areas for improvement in balancing assertiveness with empathy.
                                                    8 - Very Good Understanding: Consistently displays a good understanding of leadership. Utilizes extraverted traits effectively but may occasionally overlook the need for more reflective or inclusive approaches.
                                                    7 - Good Understanding: Generally understands effective leadership and makes good use of extraverted qualities. However, may lack depth in integrating these qualities into a diverse leadership style.
                                                    6 - Competent Understanding: Demonstrates a competent understanding of leadership. Shows some ability to use extraverted traits in leadership but struggles with complexity or in quieter team dynamics.
                                                    5 - Moderate Understanding: Displays a moderate understanding of leadership. Extraverted traits are evident but not always effectively channeled into leadership practices. Often needs guidance to balance different leadership aspects.
                                                    4 - Inconsistent Understanding: Has a basic understanding of leadership, but application of extraverted qualities is inconsistent. Struggles to effectively integrate these traits into a cohesive leadership approach.
                                                    3 - Limited Understanding: Shows limited understanding of how to use extraversion in effective leadership. Tends to be one-dimensional, lacking adaptability or sensitivity to different team needs.
                                                    2 - Poor Understanding: Demonstrates a poor grasp of how extraversion impacts leadership. Fails to use extraverted traits effectively, often leading to imbalanced or ineffective leadership.
                                                    1 - Lacks Understanding: Displays almost no understanding of effective leadership, particularly in the context of extraversion. Leadership approach is significantly lacking in energy, inspiration, or assertiveness.
                                                    """,
                                    
        "Motivational Strategies": """10 - Exceptionally Motivating: Demonstrates an outstanding understanding and application of motivational strategies. Employs a wide range of innovative and highly effective techniques tailored to individual team members' needs, resulting in high engagement and performance.
                                        9 - Highly Motivating: Shows strong abilities in motivating teams. Uses diverse and effective strategies, with minor areas for improvement in adapting to unique team member needs or varying situations.
                                        8 - Very Effective: Consistently applies effective motivational strategies. While there is good variety, the methods used may lack some adaptability to different team dynamics or individual preferences.
                                        7 - Generally Effective: Demonstrates a good understanding of standard motivational techniques. Effective in common situations but may lack customization for individual team members or unique scenarios.
                                        6 - Competently Motivating: Shows competency in using basic motivational strategies. Effective in familiar settings but struggles to adapt to new or challenging environments.
                                        5 - Moderately Effective: Displays some understanding of motivational methods but is inconsistent in their application. Success is variable and may depend heavily on external factors or specific circumstances.
                                        4 - Limited Effectiveness: Has a basic grasp of motivational strategies but struggles to implement them effectively. Techniques used are often generic and not well-suited to team or individual needs.
                                        3 - Minimal Impact: Demonstrates minimal understanding of how to effectively motivate a team. Efforts are sporadic and poorly executed, leading to limited impact on team engagement and performance.
                                        2 - Ineffective: Shows poor understanding and application of motivational strategies. Techniques are rarely used effectively or fail to resonate with team members.
                                        1 - Lacks Motivational Skills: Displays a lack of understanding and ability to effectively motivate team members. No effective strategies are evident, leading to low morale and poor team engagement.
                                    """,
       
        "Empathy and Emotional Intelligence": """10 - Exceptionally Empathic and Emotionally Intelligent: Demonstrates outstanding empathy and emotional intelligence. Exhibits a deep understanding of others' feelings and perspectives, and skillfully manages emotions in a way that enhances team relationships and performance.
                                                9 - Highly Empathic: Shows strong emotional intelligence and empathy. Effectively understands and responds to team members' emotions, with minor areas for improvement in complex or highly charged emotional situations.
                                                8 - Very Good: Consistently displays good emotional intelligence. Understands and reacts appropriately to others' emotions but may occasionally miss subtler emotional cues or complex emotional dynamics.
                                                7 - Good: Generally effective in empathizing and managing emotions. Capable of recognizing and responding to basic emotional states but may lack depth in handling more nuanced emotional scenarios.
                                                6 - Competent: Demonstrates adequate empathy and emotional intelligence. Handles familiar emotional situations effectively but struggles with more complex emotional dynamics or under stress.
                                                5 - Moderately Effective: Shows some understanding of empathy and emotional intelligence but is inconsistent in application. Success varies depending on the situation and the clarity of emotional cues.
                                                4 - Inconsistent: Demonstrates basic empathy and emotional intelligence but lacks consistency. Some emotional states are well-handled, while others are misinterpreted or poorly managed.
                                                3 - Limited Effectiveness: Struggles with effective empathy and emotional intelligence. Often fails to recognize or appropriately respond to others' emotions, leading to misunderstandings or conflicts.
                                                2 - Poor: Shows poor emotional intelligence and empathy. Rarely understands or responds effectively to emotional cues, negatively impacting team interactions and morale.
                                                1 - Lacks Empathy and Emotional Intelligence: Displays a significant lack of empathy and emotional intelligence. Fails to recognize or respond to others' emotions, resulting in frequent misunderstandings, conflicts, or disengagement.
                                                """,
        "Adaptability and Innovation": """10 - Exceptionally Adaptive and Innovative: Demonstrates outstanding adaptability and innovation, leveraging extraversion to drive collaborative innovation and effectively embrace change. Engages energetically with challenges, leading to creative solutions and dynamic adaptation.
                                            9 - Highly Adaptive and Innovative: Shows strong adaptability and innovative thinking, using their extraversion to facilitate open idea exchange and rapidly adjust to new circumstances. Occasionally, there might be room for even more creative or quicker adaptation.
                                            8 - Very Good: Consistently displays good adaptability and innovative capacity. Extraverted traits contribute to effective team brainstorming and change management, though there may be rare instances of missed opportunities for innovation.
                                            7 - Good: Generally effective in both adaptability and innovation. Extraversion aids in generating ideas and embracing change, but there might be a lack of depth in innovative solutions or slight delays in adaptation.
                                            6 - Competent: Demonstrates adequate adaptability and innovation. Relies on extraversion to engage with others and adapt, but struggles with complex innovations or rapid changes.
                                            5 - Moderately Effective: Shows some capability in being adaptable and innovative. Extraversion helps in collaborative settings, yet effectiveness varies with situation complexity and speed of change.
                                            4 - Inconsistent: Exhibits basic levels of adaptability and innovation. Extraverted qualities are evident but inconsistently applied to effectively foster innovation or adapt to change.
                                            3 - Limited Effectiveness: Struggles with effective adaptability and innovation. Extraversion does not consistently translate into positive outcomes in these areas, leading to missed opportunities.
                                            2 - Poor: Demonstrates poor adaptability and innovation. Rarely uses extraversion effectively to adapt or innovate, resulting in stagnant or ineffective responses to new situations.
                                            1 - Lacks Adaptability and Innovation: Displays a significant lack of both adaptability and innovation. Extraversion does not aid in overcoming challenges or generating new ideas, leading to ineffective handling of change and creativity.
                                        """,
        
        "Vision and Goal Setting": """10 - Exceptional Goal Setter: Demonstrates an outstanding ability to set and communicate clear, strategic, and achievable goals. Shows evidence of aligning goals with organizational objectives and individual team members' strengths, leading to high engagement and successful outcomes.
                            9 - Highly Effective: Sets clear and effective goals that are well-communicated and aligned with team capabilities and organizational needs. Shows adaptability in goal setting to meet changing circumstances.
                            8 - Very Good: Consistently sets and communicates clear goals. There may be minor gaps in aligning these goals with broader objectives or individual strengths.
                            7 - Good: Sets reasonable goals that are generally clear and achievable. Demonstrates a basic alignment with team and organizational needs, but may lack some detail or adaptability.
                            6 - Competent: Shows competency in setting goals that are mostly clear and achievable. However, struggles with more complex goal-setting scenarios or in fully engaging the team with these goals.
                            5 - Moderately Effective: Sets goals that are occasionally unclear or not fully aligned with team capabilities. Inconsistency in communicating and driving these goals may be evident.
                            4 - Inconsistent: Demonstrates a basic understanding of goal setting but lacks consistency and effectiveness. Goals may be too vague, unachievable, or poorly communicated.
                            3 - Limited Effectiveness: Shows limited effectiveness in setting and communicating goals. Goals often lack clarity, alignment with team strengths, or are not compelling.
                            2 - Poor: Struggles significantly with setting effective goals. Goals set are often unclear, unrealistic, or irrelevant to team and organizational objectives.
                            1 - Ineffective Goal Setter: Displays a lack of understanding and ability in setting and communicating goals. Fails to establish meaningful or achievable goals, leading to confusion and disengagement in the team.""",
        
        "Cultural Fit and Company Values": """10 - Exceptional Delegator: Demonstrates outstanding delegation skills. Allocates tasks based on a profound understanding of individual team members' strengths, skills, and development needs. Ensures an optimal balance of workload and actively contributes to team efficiency and individual growth.
                                9 - Highly Effective: Exhibits strong delegation abilities. Tasks are well-matched to team members' capabilities and foster their professional development. Minor improvements might be needed in ensuring a balanced workload distribution.
                                8 - Very Good: Consistently delegates tasks effectively. Generally aligns tasks with team members' skills and development goals but may have occasional mismatches or less consideration for workload balance.
                                7 - Good: Usually delegates tasks appropriately, showing an understanding of team members' capabilities. However, may lack refinement in optimizing task allocation for personal growth or in challenging situations.
                                6 - Competent: Demonstrates adequate delegation skills in familiar scenarios but struggles with more complex or novel situations. Task assignments are reasonable but may not fully capitalize on individual strengths or team dynamics.
                                5 - Moderately Effective: Displays some ability in delegation but lacks consistency. Some tasks are well-assigned, while others do not align well with team members' skills or fail to enhance team productivity.
                                4 - Inconsistent: Has basic delegation skills but lacks consistency and effectiveness. Some aspects of task assignments are suitable, but many are poorly aligned with individual strengths or team needs.
                                3 - Limited Effectiveness: Struggles with effective task delegation. Often fails to consider individual skills or team dynamics, leading to inefficient task distribution.
                                2 - Poor: Demonstrates poor delegation skills. Frequently misassigns tasks, resulting in inefficiencies and potential team discontent.
                                1 - Ineffective Delegator: Lacks effective delegation skills entirely. Assignments are consistently inappropriate, leading to significant inefficiencies and demotivation within the team.""",
    }

    # Define a strict and rational evaluation prompt with detailed criteria
    evaluation_prompt_template = """
    Consider the candidate's response to the question: 'Describe how you would handle a situation where you have multiple deadlines approaching simultaneously?'

    Candidate's Response: {extraversion_text}

    Please evaluate the candidate's answer on a scale from 1 to 10 for its adherence to the criterion of '{criterion}'. Refer to the following scoring guidelines:

    {details}

    Based on these guidelines, provide a score and a detailed explanation for the score given.

    Detailed Evaluation for '{criterion}':
    """

    return llm, negative_criteria_details, evaluation_prompt_template

def get_llm_response_agreeableness(agreeableness_text):
    # llm = ChatOpenAI(openai_api_key="your-openai-api-key")

    # Initialize the language model
    llm = ChatOpenAI(openai_api_key="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")

    # Define the criteria and their detailed evaluation instructions
    criteria_details = {
        "Willingness to Learn": "How does the candidate show his openness to learn new technologies and utilize his abilities both technical and networking abilities to learn the technology and identify the appropriate solution to the situation. Evaluate the presence of enthusiasm for viewing challenges as opportunities. Look for clear indications in the response where the candidate demonstrates a proactive attitude towards learning.",
        "Problem-Solving Skills": "Evaluate the response for specific steps or strategies mentioned for understanding and working with new technology. The score should reflect the depth and practicality of the strategies described.",
        "Adaptability and Flexibility": "Determine how well the response illustrates the candidate's ability to adapt to new technologies or environments. The score should be based on concrete examples or a clear expression of a flexible mindset.",
        "Resource Utilization": "Identify specific mentions in the response of leveraging existing resources such as colleagues' expertise, online forums, training materials, or professional networks.",
        "Collaboration and Teamwork": "Look for direct references to collaborating with team members, asking for help, or sharing knowledge, and score based on how explicitly these are addressed.",
        "Proactive Approach": "Evaluate for examples in the response where the candidate proactively seeks information, anticipates challenges, or prepares in advance.",
        "Risk Management and Critical Thinking": "Assess the response for thoughts on identifying potential pitfalls with new technology and strategies to mitigate them.",
        "Creativity and Innovation": "Look for innovative ideas or unique perspectives on technology's potential benefits and uses in the response.",
        "Resilience and Persistence": "Evaluate the response for indications of persistence in the face of difficulties and maintaining a positive attitude during challenging times.",
        "Communication Skills": "Assess the clarity and effectiveness in expressing their approach to the project and the ability to articulate complex ideas simply.",
        "Overall Assessment": "Provide an overall evaluation of the candidate's response, considering the balance of skills demonstrated, cultural fit, and potential for growth. Highlight key strengths and areas for improvement, based on the detailed analysis of each criterion."
    }

    negative_criteria_details = {
        "Teamwork and Responsibility": """10 - Exceptional Team Player and Responsible: Demonstrates outstanding teamwork and responsibility in conflict resolution. Takes proactive steps to understand the colleague's perspective, seeks collaborative solutions, and takes full responsibility for resolving the disagreement, thereby strengthening team cohesion.
                                            9 - Highly Effective in Teamwork and Responsibility: Shows strong teamwork and assumes responsibility effectively. Actively works towards resolution, maintaining a positive team dynamic. Minor improvements could be in ensuring all team perspectives are considered.
                                            8 - Very Good Team Player: Consistently good at teamwork and taking responsibility. Engages in constructive dialogue and works towards mutual understanding, with occasional lapses in fully integrating team perspectives or sharing responsibility.
                                            7 - Good at Teamwork: Generally effective in promoting teamwork and assuming responsibility. Resolves disagreements through cooperation, though may lack some initiative in taking responsibility or in considering all team dynamics.
                                            6 - Competent in Teamwork and Responsibility: Demonstrates adequate teamwork and takes responsibility for resolving conflicts. Effective in familiar situations but struggles with complex team dynamics or when higher levels of responsibility are required.
                                            5 - Moderately Effective: Shows some capability in teamwork and taking responsibility but is inconsistent. Resolution is achieved in simpler conflicts; effectiveness varies with the complexity of the disagreement and the need for responsibility.
                                            4 - Inconsistent Teamwork: Exhibits basic teamwork skills with inconsistency in taking responsibility. Some conflicts are managed well, while others are mishandled due to inadequate collaboration or reluctance to assume responsibility.
                                            3 - Limited Effectiveness in Teamwork: Struggles with effective teamwork and taking responsibility. Often fails to collaborate effectively or to take adequate responsibility for conflict resolution, impacting team harmony.
                                            2 - Poor Teamwork and Responsibility: Demonstrates poor teamwork and rarely assumes responsibility for resolving disagreements. Often contributes to prolonged conflicts or negative team dynamics due to lack of cooperation.
                                            1 - Lacks Teamwork and Avoids Responsibility: Displays a significant lack of teamwork and avoids taking responsibility in conflicts. Inability to work collaboratively or to assume responsibility leads to unresolved issues and deteriorates team cohesion.
                                        """,
                                    
        "Conflict Resolution and Adaptability": """10 - Exceptional Conflict Resolver and Highly Adaptable: Demonstrates outstanding ability in resolving conflicts with a high degree of adaptability. Skillfully navigates disagreements, showing a deep understanding of the colleague's perspective and employing flexible, creative solutions that respect all parties' views.
                                                    9 - Highly Effective Conflict Resolution: Shows strong conflict resolution skills and adaptability. Effectively manages disagreements through empathetic understanding and flexible problem-solving, with minor areas for improvement in addressing deeper conflict nuances.
                                                    8 - Very Good at Conflict Resolution: Consistently good in resolving conflicts and showing adaptability. Balances different perspectives and adapts strategies as needed, though there may be occasional challenges in fully satisfying all parties involved.
                                                    7 - Good Conflict Resolver: Generally effective in conflict resolution and demonstrates good adaptability. Works towards resolution with a willingness to adjust approaches, but may lack depth in creative problem-solving or in completely addressing all concerns.
                                                    6 - Competent in Conflict Resolution: Demonstrates adequate skills in conflict resolution and adaptability. Resolves standard conflicts through negotiation and compromise but struggles with more complex or emotionally charged disagreements.
                                                    5 - Moderately Effective: Shows some ability in resolving conflicts and being adaptable but lacks consistency. Achieves resolution in simpler conflicts; however, effectiveness varies with complexity and emotional intensity.
                                                    4 - Inconsistent Conflict Resolution: Exhibits basic conflict resolution skills with inconsistent adaptability. Some aspects of disagreements are addressed appropriately, while others are mishandled due to rigid or ineffective approaches.
                                                    3 - Limited Effectiveness in Conflict Resolution: Struggles with effective conflict resolution and adaptability. Often fails to adequately understand or address the colleague's viewpoint or to adapt strategies, leading to unresolved or poorly resolved conflicts.
                                                    2 - Poor Conflict Resolver: Demonstrates poor conflict resolution skills and low adaptability. Rarely manages to resolve conflicts effectively, often misunderstanding the issues or failing to adjust approaches as needed.
                                                    1 - Ineffective in Conflict Resolution: Lacks effective conflict resolution skills and adaptability entirely. Unable to navigate disagreements constructively, leading to unresolved conflicts and potential deterioration of relationships.
                                            """,
       
        "Alignment with Company Values": """10 - Exceptional Alignment: Demonstrates outstanding alignment with company values during conflict resolution. Actions and decisions reflect a deep commitment to the company's ethical standards, fostering a positive and respectful resolution that upholds the organization's principles.
                                                9 - Highly Aligned: Shows strong alignment with company values. Effectively resolves conflicts in a manner that respects and promotes the company's core values, with minor areas for improvement in fully embodying these values in all aspects of resolution.
                                                8 - Very Good Alignment: Consistently aligns actions with company values during disagreements. There may be occasional challenges in balancing personal conflict resolution approaches with the company's ethical standards.
                                                7 - Good Alignment: Generally maintains alignment with company values while resolving conflicts. Demonstrates a good understanding of the importance of these values, though may lack some depth in integrating them into conflict resolution strategies.
                                                6 - Competent Alignment: Demonstrates adequate alignment with company values. Resolves standard conflicts in ways that do not contradict company principles but struggles with more complex situations that require nuanced application of these values.
                                                5 - Moderately Aligned: Shows some alignment with company values but lacks consistency. Efforts to resolve conflicts in line with company standards vary in effectiveness, particularly in complex or emotionally charged situations.
                                                4 - Inconsistent Alignment: Exhibits basic alignment with company values in conflict resolution but lacks consistency. Some actions may not fully reflect the company's ethical standards, leading to questions about commitment to these values.
                                                3 - Limited Alignment: Struggles with aligning conflict resolution approaches with company values. Often fails to adequately consider or apply these principles, leading to resolutions that may not fully support company ethics.
                                                2 - Poor Alignment: Demonstrates poor alignment with company values. Rarely manages to resolve conflicts in ways that uphold the organization's principles, often overlooking the importance of these values.
                                                1 - No Alignment: Lacks alignment with company values in conflict resolution entirely. Actions and decisions during disagreements contradict or ignore the company's ethical standards, undermining the organization's values.
                                                """
    }

    # Define a strict and rational evaluation prompt with detailed criteria
    evaluation_prompt_template = """
    Consider the candidate's response to the question: 'Describe how you would handle a situation where you have multiple deadlines approaching simultaneously?'

    Candidate's Response: {agreeableness_text}

    Please evaluate the candidate's answer on a scale from 1 to 10 for its adherence to the criterion of '{criterion}'. Refer to the following scoring guidelines:

    {details}

    Based on these guidelines, provide a score and a detailed explanation for the score given.

    Detailed Evaluation for '{criterion}':
    """

    return llm, negative_criteria_details, evaluation_prompt_template

def get_llm_response_neuroticism(neuroticism_text):
    # llm = ChatOpenAI(openai_api_key="your-openai-api-key")

    # Initialize the language model
    llm = ChatOpenAI(openai_api_key="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")

    # Define the criteria and their detailed evaluation instructions
    criteria_details = {
        "Willingness to Learn": "How does the candidate show his openness to learn new technologies and utilize his abilities both technical and networking abilities to learn the technology and identify the appropriate solution to the situation. Evaluate the presence of enthusiasm for viewing challenges as opportunities. Look for clear indications in the response where the candidate demonstrates a proactive attitude towards learning.",
        "Problem-Solving Skills": "Evaluate the response for specific steps or strategies mentioned for understanding and working with new technology. The score should reflect the depth and practicality of the strategies described.",
        "Adaptability and Flexibility": "Determine how well the response illustrates the candidate's ability to adapt to new technologies or environments. The score should be based on concrete examples or a clear expression of a flexible mindset.",
        "Resource Utilization": "Identify specific mentions in the response of leveraging existing resources such as colleagues' expertise, online forums, training materials, or professional networks.",
        "Collaboration and Teamwork": "Look for direct references to collaborating with team members, asking for help, or sharing knowledge, and score based on how explicitly these are addressed.",
        "Proactive Approach": "Evaluate for examples in the response where the candidate proactively seeks information, anticipates challenges, or prepares in advance.",
        "Risk Management and Critical Thinking": "Assess the response for thoughts on identifying potential pitfalls with new technology and strategies to mitigate them.",
        "Creativity and Innovation": "Look for innovative ideas or unique perspectives on technology's potential benefits and uses in the response.",
        "Resilience and Persistence": "Evaluate the response for indications of persistence in the face of difficulties and maintaining a positive attitude during challenging times.",
        "Communication Skills": "Assess the clarity and effectiveness in expressing their approach to the project and the ability to articulate complex ideas simply.",
        "Overall Assessment": "Provide an overall evaluation of the candidate's response, considering the balance of skills demonstrated, cultural fit, and potential for growth. Highlight key strengths and areas for improvement, based on the detailed analysis of each criterion."
    }

    negative_criteria_details = {
        "Stress Management and Resilience": """10 - Exceptionally Resilient: Demonstrates outstanding resilience and stress management. Exhibits high emotional stability, effectively uses advanced coping mechanisms, and maintains productivity and positivity even in highly stressful situations.
                                                9 - Highly Resilient: Shows strong resilience and effective stress management. Employs a variety of coping strategies efficiently, with minor areas for improvement in handling extreme stress.
                                                8 - Very Good Resilience: Consistently manages stress well and shows good resilience. Adapts to stress with effective strategies, though may occasionally face challenges in the most demanding situations.
                                                7 - Good Stress Management: Generally effective in managing stress and demonstrating resilience. Uses appropriate coping mechanisms, but may lack some sophistication or consistency in the most challenging scenarios.
                                                6 - Competent Resilience: Demonstrates adequate ability to manage stress and maintain resilience. Effective in familiar stress scenarios but struggles with unique or intensified stressors.
                                                5 - Moderately Resilient: Shows some resilience and ability to manage stress but is inconsistent. Achieves moderate success with basic coping strategies; effectiveness varies with the situation's complexity.
                                                4 - Inconsistent Stress Management: Exhibits basic resilience and stress management capabilities with inconsistency. Some stressors are managed adequately, while others lead to decreased performance or well-being.
                                                3 - Limited Resilience: Struggles with effective stress management and resilience. Often overwhelmed by stress, with coping strategies that are ineffective or poorly applied in more demanding situations.
                                                2 - Poor Stress Management: Demonstrates poor resilience and stress management. Rarely copes effectively with stress, frequently experiencing significant impacts on performance and emotional well-being.
                                                1 - Lacks Resilience: Displays almost no effective stress management or resilience. Is unable to cope with stress, leading to profound negative impacts on work performance and personal health.
                                                    """,
       
        "Support Seeking and Self-Care": """10 - Exceptionally Proactive: Demonstrates outstanding proactive behavior in seeking support and engaging in self-care. Regularly utilizes a broad network for support and employs a comprehensive range of self-care strategies to maintain well-being and performance under stress.
                                            9 - Highly Proactive in Support Seeking: Shows strong initiative in seeking support and practicing self-care. Effectively uses both professional and personal networks for support, with minor areas for improvement in diversifying self-care practices.
                                            8 - Very Good at Seeking Support: Consistently seeks support and engages in self-care effectively. May rely more on certain types of support or self-care activities, with occasional opportunities for broader application.
                                            7 - Good with Support and Self-Care: Generally effective in seeking support and practicing self-care. Utilizes known sources of support and engages in common self-care activities but may lack consistency or variety in practices.
                                            6 - Competent in Seeking Support: Demonstrates adequate ability to seek support and engage in self-care. Effective in familiar stress scenarios but struggles to identify or utilize additional support resources or self-care strategies in new situations.
                                            5 - Moderately Effective: Shows some effectiveness in seeking support and self-care but is inconsistent. Sometimes utilizes support networks and self-care practices; effectiveness varies with stress levels and situations.
                                            4 - Inconsistent in Seeking Support: Exhibits basic support-seeking behavior and self-care practices with inconsistency. Some stressors are managed with support and self-care, while others are not addressed as effectively.
                                            3 - Limited in Seeking Support: Struggles with effectively seeking support and engaging in self-care. Often overlooks the importance of support networks and self-care activities, leading to ineffective stress management.
                                            2 - Poor at Seeking Support: Demonstrates poor behavior in seeking support and self-care. Rarely utilizes support networks effectively and seldom engages in self-care practices, negatively impacting stress management and well-being.
                                            1 - Lacks Initiative in Support and Self-Care: Displays almost no initiative in seeking support or engaging in self-care. Fails to recognize the value of support networks and self-care in managing stress, leading to significant challenges in coping with work-related stress.
                                            """,

        "Growth Mindset": """10 - Exceptionally Growth-Oriented: Demonstrates an outstanding growth mindset. Actively learns from every stressful situation, consistently uses challenges as opportunities for personal and professional development, and exhibits remarkable resilience and adaptability.
                                9 - Highly Growth-Focused: Shows a strong commitment to learning and development. Effectively uses stressful situations as learning opportunities, with minor areas for improvement in applying lessons learned to new challenges.
                                8 - Very Good Growth Mindset: Consistently displays a growth mindset. Responds to stress by seeking learning opportunities, though may occasionally miss deeper insights or broader applications of these lessons.
                                7 - Good at Learning from Challenges: Generally effective in adopting a growth mindset. Learns from most stressful situations and applies these lessons to similar future scenarios but may lack consistency in applying learning across different contexts.
                                6 - Competent Growth Mindset: Demonstrates a competent growth mindset. Shows resilience and learns from challenges but may struggle with applying these learnings in a broader range of situations or under higher stress levels.
                                5 - Moderately Growth-Oriented: Exhibits some aspects of a growth mindset but is inconsistent. Engages in learning from stressful experiences occasionally; effectiveness varies with the nature of the stressor and personal engagement.
                                4 - Inconsistent Growth Mindset: Shows basic signs of a growth mindset with inconsistency. Some stressful situations lead to learning and development, while others are missed opportunities for growth due to avoidance or fixed mindset tendencies.
                                3 - Limited Growth Focus: Struggles to maintain a growth mindset under stress. Rarely identifies learning opportunities in stressful situations, often reacting defensively or with a fixed mindset.
                                2 - Poor Growth Orientation: Demonstrates poor engagement with learning and development in the face of stress. Stressful situations are often seen as threats rather than opportunities for growth, leading to minimal personal development.
                                1 - Lacks Growth Mindset: Displays almost no growth mindset qualities. Fails to learn from stressful experiences, consistently viewing challenges negatively and missing opportunities for development.
                            """
    }

    # Define a strict and rational evaluation prompt with detailed criteria
    evaluation_prompt_template = """
    Consider the candidate's response to the question: 'Describe how you would handle a situation where you have multiple deadlines approaching simultaneously?'

    Candidate's Response: {neuroticism_text}

    Please evaluate the candidate's answer on a scale from 1 to 10 for its adherence to the criterion of '{criterion}'. Refer to the following scoring guidelines:

    {details}

    Based on these guidelines, provide a score and a detailed explanation for the score given.

    Detailed Evaluation for '{criterion}':
    """

    return llm, negative_criteria_details, evaluation_prompt_template


def create_and_run_seq_chain(type, candidate_response, llm, negative_criteria_details, evaluation_prompt_template):
    chains = []
    status_message = st.empty()

    for criterion, details in negative_criteria_details.items():
        # Update the status message for the current processing criterion
        status_message.text(f"Processing: {criterion}")
        # Simulate processing time
           # Adjust sleep time based on actual processing time
        if type == "openness":
            final_prompt = evaluation_prompt_template.format(openness_text=candidate_response, criterion=criterion, details=details)
        elif type == "conscientiousness":
            final_prompt = evaluation_prompt_template.format(conscientiousness_text=candidate_response, criterion=criterion, details=details)
        elif type == "extraversion":
            final_prompt = evaluation_prompt_template.format(extraversion_text=candidate_response, criterion=criterion, details=details)
        elif type == "agreebleness":
            final_prompt = evaluation_prompt_template.format(agreeableness_text=candidate_response, criterion=criterion, details=details)
        elif type == "neuroticism":
            final_prompt = evaluation_prompt_template.format(neuroticism_text=candidate_response, criterion=criterion, details=details)
                
        prompt = ChatPromptTemplate.from_template(final_prompt)
        chain = LLMChain(llm=llm, prompt=prompt, output_key=f'score_{criterion}')
        chains.append(chain)
        
        # Optionally, you can update the status message to indicate completion of the current task
        # This step is optional and can be adjusted based on your preference
        status_message.text(f"Finished processing: {criterion}")

    # Clear the status message after all processing is complete
    status_message.text("Processing complete.")

    
    # Create the SequentialChain
    seq_chain = SequentialChain(chains=chains, 
                                input_variables=['answer'], 
                                output_variables=[f'score_{criterion}' for criterion in negative_criteria_details], 
                                verbose=True)
    
    return seq_chain

def plot_radar_chart(scores):
    labels=np.array(list(scores.keys()))
    stats=np.array(list(scores.values()))

    angles=np.linspace(0, 2*np.pi, len(labels), endpoint=False).tolist()
    stats=np.concatenate((stats,[stats[0]]))
    angles+=angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='blue', alpha=0.25)
    ax.plot(angles, stats, color='blue', linewidth=2)  
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    return fig
# e_subplots


def plot_pyplot_radar_chart(scores):
    labels = list(scores.keys())
    values = list(scores.values())

    # Create a subplot with type 'polar'
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'polar'}]])

    # Add a trace for the scores
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself'
    ))

    # Set up the radar chart layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]  # Set the range of the radial axis to be constant from 0 to 10
            )
        ),
        showlegend=False
    )

    return fig

def save_processed_scores_to_sheet(client, spreadsheet_id, worksheet_name, candidate_name, processed_scores):
    # Open the spreadsheet and the worksheet
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    
    # Convert processed_scores to a format suitable for Google Sheets
    scores_list = [processed_scores[key] for key in sorted(processed_scores)]
    
    # Find the row of the candidate to update
    # Assuming the first column of the worksheet contains the candidate names
    candidate_list = sheet.col_values(1)
    if candidate_name in candidate_list:
        row_number = candidate_list.index(candidate_name) + 1  # +1 because list indexes start at 0 but Google Sheets rows start at 1
        # Update the row with new scores. Adjust the range according to your sheet's structure
        cell_range = f'B{row_number}:K{row_number}'  # Assuming scores start from column B to K for each candidate
        sheet.update(cell_range, [scores_list])
    else:
        # If the candidate is not found, append a new row with the candidate name and scores
        new_row = [candidate_name] + scores_list
        sheet.append_row(new_row)

def extract_score(result_text):
    # Define a regex pattern that matches your score format
    # This pattern assumes the score is always a number possibly followed by "out of 10"
    # Adjust the pattern as needed based on your actual result text format
    pattern = r"(\d+)"
    match = re.search(pattern, result_text)
    if match:
        return match.group(1)  # Return the first capturing group (the score number)
    else:
        return ""  # Return a placeholder if the score is not found
    

def save_scores_to_google_sheets(client, spreadsheet_id, worksheet_name, candidate_name, column_name, openness_llm_answer):
    # Convert the dictionary to a JSON string
    openness_llm_answer_json = json.dumps(openness_llm_answer, ensure_ascii=False)
    
    # Continue with your existing code to save to Google Sheets...
    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    cell = sheet.find(candidate_name)
    if not cell:
        print(f"Candidate {candidate_name} not found.")
        return False
    
    headers = sheet.row_values(1)
    try:
        openness_column_index = headers.index(column_name) + 1
    except ValueError:
        print("'Openness-LLM-Answer' column not found.")
        return False
    
    # Update the cell with the serialized JSON string
    sheet.update_cell(cell.row, openness_column_index, openness_llm_answer_json)
    print(f"Successfully updated Openness score for {candidate_name}.")
    return True

def plot_pyplot_radar_chart2(scores):
    # Filter out the 'answer' key and any entries without a score
    filtered_scores = {k: v for k, v in scores.items() if k != 'answer' and v['score']}
    
    labels = list(filtered_scores.keys())
    # Convert scores to floats, defaulting to 0.0 for any empty scores
    values = [float(v['score']) if v['score'] else 0.0 for v in filtered_scores.values()]

    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'polar'}]])
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=labels,
        fill='toself'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False
    )

    return fig

def fetch_and_parse_data(candidate_name):
    client = init_gspread_connection()
    spreadsheet_id = "1Ou0ZXVcLPkhdARBPnhfrp8cGq-zG2hPMnezQI8SZp2I"
    worksheet_name = "Sheet1"

    existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
    # Ensure candidate_row is a single row by using .iloc[0]
    candidate_row = existing_data[existing_data['CandidateName'] == candidate_name].iloc[0]

    llm_data = {}
    columns = ['Openness-LLM-Answer', 'Conscientiousness-LLM-Answer', 'Extraversion-LLM-Answer', 'Agreebleness-LLM-Answer', 'Neuroticism-LLM-Answer']
    for column in columns:
        # Directly access the cell's value; it's now guaranteed to be a single value, not a Series
        json_data = candidate_row[column]
        # No need for the pd.isnull check here since we're dealing with a single value
        parsed_data = json.loads(json_data) if pd.notnull(json_data) else {}
        llm_data[column.replace('-LLM-Answer', '')] = parsed_data
    # st.write(llm_data)
    return llm_data


def prepare_data_for_plotting(llm_data):
    # Initialize containers for traits and their scores
    traits = []
    scores = []
    
    # Iterate through each trait's data
    for trait, trait_data in llm_data.items():
        # Iterate through each detail for the trait
        for criterion, detail in trait_data.items():
            if criterion != "answer":  # Skip the 'answer' entry if not needed for plotting
                score_str = detail.get("score", "0")  # Default to "0" if no score
                try:
                    score = float(score_str) if score_str else 0.0  # Convert to float, handling empty strings
                except ValueError:
                    score = 0.0  # Default to 0.0 for non-numeric strings
                traits.append(f"{trait}-{criterion}")  # Combine trait and criterion for label
                scores.append(score)
    
    return traits, scores



def plot_llm_scores(df):
    # Ensure the DataFrame has the columns we expect
    if not all(column in df.columns for column in ['Candidate', 'Trait and Criterion', 'Score']):
        raise ValueError("DataFrame must contain 'Candidate', 'Trait and Criterion', and 'Score' columns")

    # Split 'Trait and Criterion' into separate 'Traits' and 'Criteria' columns for coloring
    df['Traits'] = df['Trait and Criterion'].apply(lambda x: x.split('-')[0])
    df['Criteria'] = df['Trait and Criterion'].apply(lambda x: '-'.join(x.split('-')[1:]))

    # Use Plotly Express to create the stacked bar chart
    fig = px.bar(df, x='Traits', y='Score', color='Criteria', facet_col='Candidate',
                 title="LLM Analysis Scores for Each Criterion",
                 labels={'Score': 'Score', 'Traits': 'Trait', 'Criteria': 'Criterion', 'Candidate': 'Candidate'},
                 hover_data=['Trait and Criterion', 'Score'],  # Show detailed info on hover
                 barmode='stack')

    # Update layout if necessary to better fit the facet columns
    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="LightSteelBlue",
    )

    return fig

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


def main():
    # Streamlit app layout setup
    st.header("Individual Candidate Analysis")
    processed_scores = {}
    processed_scores_conscientiousness = {}
    processed_scores_extraversion = {}
    processed_scores_agreebleness = {}
    processed_scores_neuroticism = {}
    
    display_criterion_openness = []
    openness_results_dict = {}
    conscientiousness_results_dict = {}
    extraversion_results_dict = {}
    agreebleness_results_dict = {}
    neuroticism_results_dict = {}
    
    # Load candidate names from the Google Sheets data
    client = init_gspread_connection()
    spreadsheet_id = "1Ou0ZXVcLPkhdARBPnhfrp8cGq-zG2hPMnezQI8SZp2I"
    worksheet_name = "Sheet1"
    existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
    candidate_names = existing_data['CandidateName'].unique()
    selected_candidate = st.selectbox("Select a Candidate:", candidate_names)
    
    
    # Dropdown for candidate selection
    

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Candidate Answers", "Openness", "Conscientiousness", "Extraversion", "Agreebleness", "Neuroticism"])
    
    client = init_gspread_connection()
    spreadsheet_id = "1Ou0ZXVcLPkhdARBPnhfrp8cGq-zG2hPMnezQI8SZp2I"
    worksheet_name = "Sheet1"
    candidate_name = selected_candidate 
    
    with tab1:
        
        if selected_candidate:
            # Fetch and display candidate details
            candidate_data = existing_data[existing_data['CandidateName'] == selected_candidate].iloc[0]
            formatted_data = format_candidate_data(candidate_data)

            st.write("#### Candidate Answers")
                    
            # Use an expander for each candidate detail
            for detail, value in formatted_data.items():
                if detail != "Candidate Name":
                    with st.expander(detail):
                        st.write(value)
        
        
        big_five_scores = {trait: 0 for trait in trait_questions}

        # Calculate scores for each trait
        for trait, questions in trait_questions.items():
            total_score = 0
            for question in questions:
                # Extract the question number from the question column name to find the correct mapping
                question_num = question.replace('ANSWER', '')
                question_type = f"QUESTION{question_num}_TYPES"
                # question_type = f"QUESTION{question[-1]}_TYPES"
                answer_text = candidate_data[question]
                # Use the mapping to get the numeric score
                score = answer_mappings[question_type].get(answer_text, 0)  # Default to 0 if not found
                total_score += score
            # Calculate average score for the trait
            big_five_scores[trait] = int(total_score / len(questions))
            
        # st.write(big_five_scores)
        
        data = [{'Trait': trait, 'Score': score} for trait, score in big_five_scores.items()]
        df = pd.DataFrame(data)

        # Create a bar chart
        fig = px.bar(df, x='Trait', y='Score', text='Score',
                    title="Big Five Personality Traits Scores",
                    labels={'Score': 'Score', 'Trait': 'Personality Trait'},
                    color='Trait',  # Color code by personality trait
                    color_continuous_scale=px.colors.sequential.Viridis)  # Optional: use a color scale

        # Make the text appear on the bars
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

        # Adjust layout for a nicer look
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',
                        yaxis=dict(title='Score', range=[0, 5]),
                        xaxis=dict(title='Personality Trait'))

        # Display the plot in Streamlit
        st.plotly_chart(fig)

    with tab2:

        existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
        candidate_row = existing_data[existing_data['CandidateName'] == candidate_name]

        if not candidate_row.empty:
            column_name = "Openness-LLM-Answer"
            openness_data = candidate_row.iloc[0][column_name]  # Adjust based on actual column name
            
            
            st.warning('🔍 Searching Candidate Data...')
              # Simulate the delay of searching

            # Conditionally show the result messages
            
            if openness_data:  # Assuming 'openness_data' is defined and indicates if data was found
                #  
                st.success('✅ Data found for the selected candidate.')
                st.balloons()
                try:
                    processed_scores = json.loads(openness_data)

                    # Plot the radar chart
                    fig = plot_pyplot_radar_chart2(processed_scores)
                    st.plotly_chart(fig)
                    
                    for criterion, details in processed_scores.items():
                        score = details.get('score', 'No score provided')
                        result_text = details.get('result_text', 'No details provided')
                        
                        # Use the criterion as the label for the expander. Show the score in the expander's label as well.
                        with st.expander(f"{criterion} - Score: {score}"):
                            # Inside the expander, display the detailed feedback text.
                            st.write(result_text)
                    
                except json.JSONDecodeError:
                    st.error("Error parsing the candidate's data. Please check the format.")
            else:
                #  
                st.error('⚠️ You need to analyse the candidate data.')
                if st.button("Analyze Openness", key="start_openness"):
                    # Initialize the language model and prepare for evaluation
                    llm, negative_criteria_details, evaluation_prompt_template = get_llm_response_openness(candidate_data['OPENNESS'])

                    # Assuming OPENNESS text is directly used or you have a specific field from candidate_data
                    openness_text = candidate_data['OPENNESS']

                    # Create and run sequential chain for the selected candidate
                    seq_chain = create_and_run_seq_chain("openness",openness_text, llm, negative_criteria_details, evaluation_prompt_template)

                    openness_results = seq_chain({'answer': openness_text})
                    
                    for criterion in negative_criteria_details:
                        evaluation_text = openness_results[f'score_{criterion}']
                        score = extract_score_from_text(evaluation_text)  # Utilize the previously defined function
                        if score is not None:
                            processed_scores[criterion] = score
                            
                    fig = plot_pyplot_radar_chart(processed_scores)
                    st.plotly_chart(fig)
                    for criterion, result in openness_results.items():
                        score = extract_score(result)
                        display_criterion_openness = criterion.replace("score_", "")
                        with st.expander(f"{display_criterion_openness} - Score: {score}"):
                            st.write(result)
                        
                        openness_results_dict[display_criterion_openness] = {
                            "score": score,
                            "result_text": result
                        }
                    
                    success = save_scores_to_google_sheets(client, spreadsheet_id, worksheet_name, candidate_name, "Openness-LLM-Answer", openness_results_dict)

                    if success:
                        st.toast('The Openness score was successfully updated in Google Sheets.', icon='😍')
                    else:
                        print("There was an issue updating the Openness score in Google Sheets.")




    with tab3:

        existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
        candidate_row = existing_data[existing_data['CandidateName'] == candidate_name]

        if not candidate_row.empty:
            column_name = "Conscientiousness-LLM-Answer"
            conscientiousness_data = candidate_row.iloc[0][column_name]  # Adjust based on actual column name
            
            
            st.warning('🔍 Searching Candidate Data...')
              # Simulate the delay of searching

        # Conditionally show the result messages
        
            if conscientiousness_data:  # Assuming 'openness_data' is defined and indicates if data was found
                st.success('✅ Data found for the selected candidate.')
                st.balloons()
                try:
                    processed_scores = json.loads(conscientiousness_data)
                    

                    #  
                    # st.success("✅ Data found for the selected candidate.")
                    # Plot the radar chart
                    fig = plot_pyplot_radar_chart2(processed_scores)
                    st.plotly_chart(fig)
                    
                    for criterion, details in processed_scores.items():
                        score = details.get('score', 'No score provided')
                        result_text = details.get('result_text', 'No details provided')
                        
                        # Use the criterion as the label for the expander. Show the score in the expander's label as well.
                        with st.expander(f"{criterion} - Score: {score}"):
                            # Inside the expander, display the detailed feedback text.
                            st.write(result_text)
                        

                
                except json.JSONDecodeError:
                    st.error("Error parsing the candidate's data. Please check the format.")
            else:
                st.error('⚠️ You need to analyse the candidate data.')
                if st.button("Analyze Conscientiousness", key="start_conscientiousness"):  # Unique key for this button
                    # Initialize the language model and prepare for evaluation
                    llm, negative_criteria_details, evaluation_prompt_template = get_llm_response_conscientiousness(candidate_data['CONSCIENTIOUSNESS'])

                    # Assuming OPENNESS text is directly used or you have a specific field from candidate_data
                    conscientiousness_text = candidate_data['CONSCIENTIOUSNESS']

                    # Create and run sequential chain for the selected candidate
                    seq_chain = create_and_run_seq_chain("conscientiousness",conscientiousness_text, llm, negative_criteria_details, evaluation_prompt_template)

                    conscientiousness_results = seq_chain({'answer': conscientiousness_text})
                    
                    for criterion in negative_criteria_details:
                        evaluation_text_conscientiousness = conscientiousness_results[f'score_{criterion}']
                        score_conscientiousness = extract_score_from_text(evaluation_text_conscientiousness)  # Utilize the previously defined function
                        if score_conscientiousness is not None:
                            processed_scores_conscientiousness[criterion] = score_conscientiousness
                            
                    fig = plot_pyplot_radar_chart(processed_scores_conscientiousness)
                    st.plotly_chart(fig)
                    for criterion, result in conscientiousness_results.items():
                        score = extract_score(result)
                        display_criterion_conscientiousness = criterion.replace("score_", "")
                        with st.expander(f"{display_criterion_conscientiousness} - Score: {score}"):
                            st.write(result)
                            
                        conscientiousness_results_dict[display_criterion_conscientiousness] = {
                                "score": score,
                                "result_text": result
                            }
 
                    success = save_scores_to_google_sheets(client, spreadsheet_id, worksheet_name, candidate_name, "Conscientiousness-LLM-Answer",conscientiousness_results_dict)

                    if success:
                        st.toast('The Conscientiousness score was successfully updated in Google Sheets.', icon='😍')
                    else:
                        print("There was an issue updating the Openness score in Google Sheets.")
        
    with tab4:

        existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
        candidate_row = existing_data[existing_data['CandidateName'] == candidate_name]
        # st.write(candidate_row)
        if not candidate_row.empty:
            column_name = "Extraversion-LLM-Answer"
            extraversion_data = candidate_row.iloc[0][column_name]  # Adjust based on actual column name
            
            
            st.warning('🔍 Searching Candidate Data...')
               # Simulate the delay of searching

            # Conditionally show the result messages
            
            if extraversion_data:  # Assuming 'openness_data' is defined and indicates if data was found
                st.success('✅ Data found for the selected candidate.')
                st.balloons()
                try:
                    processed_scores = json.loads(extraversion_data)
                    

                    #  
                    # st.success("✅ Data found for the selected candidate.")
                    # Plot the radar chart
                    fig = plot_pyplot_radar_chart2(processed_scores)
                    st.plotly_chart(fig)
                    
                    for criterion, details in processed_scores.items():
                        score = details.get('score', 'No score provided')
                        result_text = details.get('result_text', 'No details provided')
                        
                        # Use the criterion as the label for the expander. Show the score in the expander's label as well.
                        with st.expander(f"{criterion} - Score: {score}"):
                            # Inside the expander, display the detailed feedback text.
                            st.write(result_text)
                        

                    
                except json.JSONDecodeError:
                    st.error("Error parsing the candidate's data. Please check the format.")
                        
            else:
                st.error('⚠️ You need to analyse the candidate data.')
                if st.button("Analyze Extraversion", key="start_extraversion"):                # Initialize the language model and prepare for evaluation
                    llm, negative_criteria_details, evaluation_prompt_template = get_llm_response_extraversion(candidate_data['EXTRAVERSION'])

                    # Assuming OPENNESS text is directly used or you have a specific field from candidate_data
                    extraversion_text = candidate_data['EXTRAVERSION']

                    # Create and run sequential chain for the selected candidate
                    seq_chain = create_and_run_seq_chain("extraversion",extraversion_text, llm, negative_criteria_details, evaluation_prompt_template)

                    extraversion_results = seq_chain({'answer': extraversion_text})
                    
                    for criterion in negative_criteria_details:
                        evaluation_text_extraversion = extraversion_results[f'score_{criterion}']
                        score_extraversion = extract_score_from_text(evaluation_text_extraversion)  # Utilize the previously defined function
                        if score_extraversion is not None:
                            processed_scores_extraversion[criterion] = score_extraversion
                            
                    fig = plot_pyplot_radar_chart(processed_scores_extraversion)
                    st.plotly_chart(fig)
                    for criterion, result in extraversion_results.items():
                        score = extract_score(result)
                        display_criterion_extraversion = criterion.replace("score_", "")
                        with st.expander(f"{display_criterion_extraversion} - Score: {score}"):
                            st.write(result)
                            
                        extraversion_results_dict[display_criterion_extraversion] = {
                                "score": score,
                                "result_text": result
                            }
                        

                    success = save_scores_to_google_sheets(client, spreadsheet_id, worksheet_name, candidate_name, "Extraversion-LLM-Answer",extraversion_results_dict)

                    if success:
                        st.toast('The Extraversion score was successfully updated in Google Sheets.', icon='😍')
                    else:
                        print("There was an issue updating the Openness score in Google Sheets.")

    with tab5:

        # Attempt to find existing data
        existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
        candidate_row = existing_data[existing_data['CandidateName'] == candidate_name]

        if not candidate_row.empty:
            column_name = "Agreebleness-LLM-Answer"
            agreebleness_data = candidate_row.iloc[0][column_name]  # Adjust based on actual column name
            
            
            st.warning('🔍 Searching Candidate Data...')
               # Simulate the delay of searching

            # Conditionally show the result messages
            
            if agreebleness_data:  # Assuming 'openness_data' is defined and indicates if data was found
                st.success('✅ Data found for the selected candidate.')
                st.balloons()
                try:
                    processed_scores = json.loads(agreebleness_data)
                    

                    #  
                    # st.success("✅ Data found for the selected candidate.")
                    # Plot the radar chart
                    fig = plot_pyplot_radar_chart2(processed_scores)
                    st.plotly_chart(fig)
                    
                    for criterion, details in processed_scores.items():
                        score = details.get('score', 'No score provided')
                        result_text = details.get('result_text', 'No details provided')
                        
                        # Use the criterion as the label for the expander. Show the score in the expander's label as well.
                        with st.expander(f"{criterion} - Score: {score}"):
                            # Inside the expander, display the detailed feedback text.
                            st.write(result_text)
                        

                    
                except json.JSONDecodeError:
                    st.error("Error parsing the candidate's data. Please check the format.")
            else:
                st.error('⚠️ You need to analyse the candidate data.')
                if st.button("Analyze Agreeableness", key="start_agreeableness"):  # Unique key for this button
                    # Initialize the language model and prepare for evaluation
                    llm, negative_criteria_details, evaluation_prompt_template = get_llm_response_agreeableness(candidate_data['AGREEABLENESS'])

                    # Assuming OPENNESS text is directly used or you have a specific field from candidate_data
                    agreeableness_text = candidate_data['AGREEABLENESS']

                    # Create and run sequential chain for the selected candidate
                    seq_chain = create_and_run_seq_chain("agreebleness",agreeableness_text, llm, negative_criteria_details, evaluation_prompt_template)

                    agreebleness_results = seq_chain({'answer': agreeableness_text})
                    
                    for criterion in negative_criteria_details:
                        evaluation_text_agreebleness = agreebleness_results[f'score_{criterion}']
                        score_agreebleness = extract_score_from_text(evaluation_text_agreebleness)  # Utilize the previously defined function
                        if score_agreebleness is not None:
                            processed_scores_agreebleness[criterion] = score_agreebleness
                            
                    fig = plot_pyplot_radar_chart(processed_scores_agreebleness)
                    st.plotly_chart(fig)
                    for criterion, result in agreebleness_results.items():
                        score = extract_score(result)
                        display_criterion_agreebleness = criterion.replace("score_", "")
                        with st.expander(f"{display_criterion_agreebleness} - Score: {score}"):
                            st.write(result)
                            
                        agreebleness_results_dict[display_criterion_agreebleness] = {
                                "score": score,
                                "result_text": result
                            }
                        
                    success = save_scores_to_google_sheets(client, spreadsheet_id, worksheet_name, candidate_name, "Agreebleness-LLM-Answer",agreebleness_results_dict)

                    if success:
                        st.toast('The Agreebleness score was successfully updated in Google Sheets.', icon='😍')
                    else:
                        print("There was an issue updating the Openness score in Google Sheets.")
                        pass


                    
    with tab6:

        # Attempt to find existing data
        existing_data = get_sheet_data(client, spreadsheet_id, worksheet_name)
        candidate_row = existing_data[existing_data['CandidateName'] == candidate_name]

        if not candidate_row.empty:
            column_name = "Neuroticism-LLM-Answer"
            neuroticism_data = candidate_row.iloc[0][column_name]  # Adjust based on actual column name
            
            
        st.warning('🔍 Searching Candidate Data...')
           # Simulate the delay of searching

        # Conditionally show the result messages
        
        if neuroticism_data:  # Assuming 'openness_data' is defined and indicates if data was found
            st.success('✅ Data found for the selected candidate.')
            st.balloons()
        else:
            st.error('⚠️ You need to analyse the candidate data.')

        

                
        if neuroticism_data:
            try:
                processed_scores = json.loads(neuroticism_data)
                

                #  
                # st.success("✅ Data found for the selected candidate.")
                # Plot the radar chart
                fig = plot_pyplot_radar_chart2(processed_scores)
                st.plotly_chart(fig)
                
                for criterion, details in processed_scores.items():
                    score = details.get('score', 'No score provided')
                    result_text = details.get('result_text', 'No details provided')
                    
                    # Use the criterion as the label for the expander. Show the score in the expander's label as well.
                    with st.expander(f"{criterion} - Score: {score}"):
                        # Inside the expander, display the detailed feedback text.
                        st.write(result_text)
                    

                
            except json.JSONDecodeError:
                st.error("Error parsing the candidate's data. Please check the format.")
                

        else:

            if st.button("Analyze Neuroticism", key="start_neuroticism"):  # Unique key for this button
                # Initialize the language model and prepare for evaluation
                llm, negative_criteria_details, evaluation_prompt_template = get_llm_response_neuroticism(candidate_data['NEUROTICISM'])

                # Assuming OPENNESS text is directly used or you have a specific field from candidate_data
                neuroticism_text = candidate_data['NEUROTICISM']

                # Create and run sequential chain for the selected candidate
                seq_chain = create_and_run_seq_chain("neuroticism",neuroticism_text, llm, negative_criteria_details, evaluation_prompt_template)

                neuroticism_results = seq_chain({'answer': neuroticism_text})
                
                for criterion in negative_criteria_details:
                    evaluation_text_neuroticism = neuroticism_results[f'score_{criterion}']
                    score_neuroticism = extract_score_from_text(evaluation_text_neuroticism)  # Utilize the previously defined function
                    if score_neuroticism is not None:
                        processed_scores_neuroticism[criterion] = score_neuroticism
                        
                fig = plot_pyplot_radar_chart(processed_scores_neuroticism)
                st.plotly_chart(fig)
                for criterion, result in neuroticism_results.items():
                    score = extract_score(result)
                    display_criterion_neuroticism = criterion.replace("score_", "")
                    with st.expander(f"{display_criterion_neuroticism} - Score: {score}"):
                        st.write(result)
                        
                    neuroticism_results_dict[display_criterion_neuroticism] = {
                            "score": score,
                            "result_text": result
                        }

                success = save_scores_to_google_sheets(client, spreadsheet_id, worksheet_name, candidate_name, "Neuroticism-LLM-Answer",neuroticism_results_dict)

                if success:
                    st.toast('The Neuroticism score was successfully updated in Google Sheets.', icon='😍')
                else:
                    print("There was an issue updating the Openness score in Google Sheets.")
                    
    

        
# This checks if the script is being run directly (as the main program) and not being imported as a module
if __name__ == "__main__":
    main()
