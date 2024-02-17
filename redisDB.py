import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB setup
uri = "mongodb+srv://humankindau:akhbq7UC8R8On1pw@cluster0.8gp5zlf.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'), serverSelectionTimeoutMS=30000)

db = client['CandidateResponses']  # Specify your database name
collection = db['CandidateAnswers']  # Specify your collection name

# Streamlit app
def main():
    st.title('MongoDB Data Insertion App')

    # User input fields
    data_title = st.text_input('Data Title:', '')
    data_content = st.text_area('Data Content:', '')

    # Insert data into MongoDB
    if st.button('Insert Data'):
        if data_title and data_content:
            document = {'title': data_title, 'content': data_content}
            collection.insert_one(document)
            st.success('Data inserted successfully!')
        else:
            st.error('Please fill in all fields.')

if __name__ == '__main__':
    main()
