# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Set page title and a descriptive write block
st.title('My Parents New Healthy Diner')
st.write("Choose the fruits you want in your custom Smoothie!")

# Get the name for the order from the user
name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake using Streamlit's secrets management
cnx = st.connection("snowflake")
session = cnx.session()
# Select both FRUIT_NAME and SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()

# Allow the user to select up to 5 ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
    , format_func=lambda x: x['FRUIT_NAME']
)

# This is where the code to fetch and display the API data should be placed
if ingredients_list:
    # Loop through the selected items
    for fruit_item in ingredients_list:
        search_term = fruit_item['SEARCH_ON']
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_term}")
        
        try:
            data = fruityvice_response.json()
            # Check if the API returned an error dictionary
            if isinstance(data, dict) and 'error' in data:
                st.subheader("Nutrition Information")
                st.write(data['error'])
            else:
                st.subheader(f"{fruit_item['FRUIT_NAME']} Nutrition Information")
                st.dataframe(data=data, use_container_width=True)
        except requests.exceptions.JSONDecodeError:
            st.subheader(f"{fruit_item['FRUIT_NAME']} Nutrition Information")
            st.write("No nutrition data found.")
        
# Button to submit the order. It's placed outside any 'if' block to avoid errors.
time_to_insert = st.button('Submit Order', key='submit_order_button')

# Process the order if the button is clicked and all fields are valid
if time_to_insert:
    # Check if a name was entered and at least one ingredient was selected
    if name_on_order and ingredients_list:
        # Now we create a list of strings from the dictionaries for concatenation
        ingredients_string = ', '.join([item['FRUIT_NAME'] for item in ingredients_list])
        
        # Create the SQL insert statement
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}');
            """
        
        # Execute the SQL statement in Snowflake
        session.sql(my_insert_stmt).collect()

    # Show a success message to the user
    st.success(f'Your Smoothie is ordered, {name_on_order}! ✅')
else:
    # Show an error if a name or ingredients are missing
    st.error("Please enter a name and select some ingredients before submitting.")
