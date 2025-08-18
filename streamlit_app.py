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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Allow the user to select up to 5 ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
)

# Fetch a URL to simulate an API call
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# st.text(smoothiefroot_response.json())
sf_df = st.dataframe(data=smoothiefoot_response.json(), use_container_width=True)

# Button to submit the order. It's placed outside any 'if' block to avoid errors.
time_to_insert = st.button('Submit Order')

# Process the order if the button is clicked and all fields are valid
if time_to_insert:
    # Check if a name was entered and at least one ingredient was selected
    if name_on_order and ingredients_list:
        # Join the list of ingredients into a single string
        ingredients_string = ', '.join(ingredients_list)
        
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
