# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title('My Parents New Healthy Diner')
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , my_dataframe
    , max_selections=5
    )
if ingredients_list:
    ingredients_string = ''
    if ingredients_list:
        for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '
    
    # This is where we define the button, outside of the if block
    time_to_insert = st.button('Submit Order')
    
    # Now, we use the button click as the primary condition
    if time_to_insert:
        # Check if a name and ingredients are selected before trying to insert
        if name_on_order and ingredients_list:
            # Correctly specify two columns: 'ingredients' and 'name_on_order'
            my_insert_stmt = f"""
                insert into smoothies.public.orders(ingredients, name_on_order)
                values ('{ingredients_string}', '{name_on_order}')
            """
            #st.write(my_insert_stmt) # You can uncomment this to debug the SQL statement
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        else:
            st.error("Please enter a name and select some ingredients before submitting.")
