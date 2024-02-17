import streamlit as st
from pymongo import MongoClient
from pymongo.server_api import ServerApi

username = 'humankindau'
password = '1B0mB9GKxyBHYBnk'
cluster_hostname = 'cluster0.n9wsfyk.mongodb.net'
database_name = 'CandidateAnswers'

# MongoDB connection
uri = f'mongodb+srv://{username}:{password}@cluster0.pye7uj8.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['streamlit_app']  # Use your database name
collection = db['user_data']  # Use your collection name

# Streamlit app
def main():
    st.title('MongoDB Data Storage App')

    # User input
    user_name = st.text_input('Enter your name:')
    user_data = st.text_area('Enter some data to store in MongoDB:')

    # When the button is pressed, store the data in MongoDB
    if st.button('Store Data'):
        if user_name and user_data:
            # Insert data into MongoDB
            document = {'name': user_name, 'data': user_data}
            collection.insert_one(document)
            st.success('Data stored successfully in MongoDB!')
        else:
            st.error('Please fill in both fields.')

    # Retrieving data
    st.subheader('Retrieve Data')
    search_name = st.text_input('Enter a name to retrieve data from MongoDB:', key='search')
    
    if st.button('Retrieve Data', key='retrieve'):
        # Use the name to retrieve the data from MongoDB
        document = collection.find_one({'name': search_name})
        if document:
            st.write(f'Data for {search_name}: {document["data"]}')
        else:
            st.error(f'No data found for {search_name} in MongoDB.')

if __name__ == '__main__':
    main()
