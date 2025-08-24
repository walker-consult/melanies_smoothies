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

# Select both FRUIT_NAME and SEARCH_ON...
my_data_rows = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()
# ...and explicitly convert the data into a list of Python dictionaries
my_dataframe = [row.as_dict() for row in my_data_rows]

# Let's check what the data looks like before passing it to multiselect
st.write(my_dataframe)

# Allow the user to select up to 5 ingredients
# This part now works perfectly because my_dataframe is a standard list of dicts
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
    , format_func=lambda x: x['FRUIT_NAME']
)

# This is where the code to fetch and display the API data should be placed
# Corrected block to fetch and display API data
if ingredients_list:
    # We don't need the ingredients_string here, it's created later for the SQL insert
    
    # Loop through each dictionary object in the list of selected ingredients
    for fruit_chosen in ingredients_list:
        
        # Use the 'FRUIT_NAME' key for display purposes
        st.subheader(fruit_chosen['FRUIT_NAME'] + ' Nutrition Information')
        
        # Use the 'SEARCH_ON' key to build the API request URL
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen['SEARCH_ON']}")
        
        # Display the JSON response as a dataframe
        st.dataframe(data=fruityvice_response.json(), use_container_width=True)

# Button to submit the order. It's placed outside any 'if' block to avoid errors.
time_to_insert = st.button('Submit Order', key='submit_order_button')

# Process the order if the button is clicked and all fields are valid
if time_to_insert:
    # Check if a name was entered and at least one ingredient was selected
    if name_on_order and ingredients_list:
        # Now we create a list of strings from the dictionaries for concatenation
        # This is the correct code for your lab
        ingredients_string = ','.join([item['FRUIT_NAME'] for item in ingredients_list])
        
        # Create the SQL insert statement
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order, order_filled)
            VALUES ('{ingredients_string}', '{name_on_order}', FALSE);
        """
        
        # Execute the SQL statement in Snowflake
        session.sql(my_insert_stmt).collect()
        
        # Show a success message to the user
        st.success(f'Your Smoothie is ordered, {name_on_order}! ✅')
    else:
        # Show an error if a name or ingredients are missing
        st.error("Please enter a name and select some ingredients before submitting.")
