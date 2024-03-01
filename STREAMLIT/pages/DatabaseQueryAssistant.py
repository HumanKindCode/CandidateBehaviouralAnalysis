import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from langchain.tools import Tool
from typing import List
import sqlite3
from pydantic.v1 import BaseModel
from langchain.tools import Tool
from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
import streamlit as st
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from dotenv import load_dotenv
load_dotenv()

chat = ChatOpenAI()


# Database connection
def get_connection():
    return psycopg2.connect(
        host="database-1.clm0wcc6k54c.ap-southeast-2.rds.amazonaws.com",
        database="CandidPersonaAnalysis",
        user="mike",
        password="HumanKind25"
    )

def list_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            rows = cur.fetchall()
    return "\n".join(row[0] for row in rows if row[0] is not None)

# Adjusted for PostgreSQL
def run_sql_query(query):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            try:
                cur.execute(query)
                return cur.fetchall()
            except psycopg2.Error as err:
                return f"The following error occurred: {str(err)}"

# Schema remains the same
class RunQueryArgsSchema(BaseModel):
    query: str

run_query_tool = Tool.from_function(
    name="run_sql_query",
    description="Run a SQL query.",
    func=run_sql_query,
    args_schema=RunQueryArgsSchema
)

# Adjusted for PostgreSQL
def describe_tables(table_names):
    with get_connection() as conn:
        with conn.cursor() as cur:
            tables = ', '.join("'" + table + "'" for table in table_names)
            cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name IN ({tables});")
            rows = cur.fetchall()
    return '\n'.join(f"Column: {row[0]}, Type: {row[1]}" for row in rows)

class DescribeTablesArgsSchema(BaseModel):
    tables_names: List[str]

describe_tables_tool = Tool.from_function(
    name="describe_tables",
    description="Returns the schema of specified tables",
    func=describe_tables,
    args_schema=DescribeTablesArgsSchema
)


tables = list_tables()
st.text('Tables Available In Database:')
st.text(tables)


st.title('Database Query Assistant')

prompt = ChatPromptTemplate(
    messages=[
        SystemMessage(content=(
            f"You are an AI that has access to a POSTGRESQL database.\n"
            f"The database has tables of: {tables}\n"
            "Do not make any assumptions about what tables exist "
            "or what columns exist. Instead, use the 'describe_tables' function"
        )),
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ]
)

tools = [run_query_tool, describe_tables_tool]

agent = OpenAIFunctionsAgent(
    llm=chat,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(
    agent = agent,
    verbose = True,
    tools=tools
)


user_input = st.text_input("Enter your input:")

# Add a button to the Streamlit interface
if st.button('Execute'):

    result = agent_executor(user_input)
    st.write(result)
