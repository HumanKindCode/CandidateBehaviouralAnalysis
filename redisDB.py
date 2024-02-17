import streamlit as st
import redis

# Initialize the Redis connection
r = redis.Redis(
    host='redis-18655.c53.west-us.azure.cloud.redislabs.com',
    port=18655,
    password='suNPb7j7UafWJrPCymWwolAhO9auOmux'
)

# Streamlit app
def main():
    st.title('Redis Data Storage App')

    # User input
    user_name = st.text_input('Enter your name:')
    user_data = st.text_input('Enter some data to store in Redis:')

    # When the button is pressed, store the data in Redis
    if st.button('Store Data'):
        if user_name and user_data:
            # Use the user name as the key to store the data
            r.set(user_name, user_data)
            st.success('Data stored successfully!')
        else:
            st.error('Please fill in both fields.')

    # Retrieving data
    st.subheader('Retrieve Data')
    search_name = st.text_input('Enter a name to retrieve data:', key='search')
    
    if st.button('Retrieve Data', key='retrieve'):
        # Use the name to retrieve the data from Redis
        data = r.get(search_name)
        if data:
            st.write(f'Data for {search_name}: {data.decode("utf-8")}')
        else:
            st.error(f'No data found for {search_name}.')

if __name__ == '__main__':
    main()
