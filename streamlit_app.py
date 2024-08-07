import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd
import numpy as np

# Write directly to the app
st.title("Customise Your Smoothie :cup_with_straw:")
st.write("""Choose the fruits you want in your custom Smoothie!""")

# Add name and instruction
title = st.text_input("Name on Smoothie: ", "")
st.write("The name on your smoothie will be:", title)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Create dataframe for use in ingredients list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert Snowpark dataframe to pandas dataframe for loc function
pd_df = my_dataframe.to_pandas()

max_selection = 5

def get_valid_fruit_names():
    """Fetches fruit names from Fruityvice API and filters based on SQL database"""
    try:
        # Fetch fruit names from Fruityvice API
        url = "https://fruityvice.com/api/fruit/all"
        response = requests.get(url)
        response.raise_for_status()
        api_fruit_names = [fruit["name"] for fruit in response.json()]
        
        # Fetch fruit names from SQL database
        sql_fruit_names = pd_df['SEARCH_ON'].tolist()
        
        # Find the intersection of both lists
        valid_fruit_names = list(set(api_fruit_names) & set(sql_fruit_names))
        return valid_fruit_names
    except requests.RequestException as e:
        st.error(f"Error fetching fruit data: {e}")
        return []

# Get valid fruit names
valid_fruits = get_valid_fruit_names()

# Sort the valid fruits (optional)
valid_fruits.sort()

# Create ingredients list
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:", 
    valid_fruits, 
    max_selections=max_selection
)

# Create conditional loop for sending requests to database
if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        
        st.subheader(f"{fruit_chosen} Nutritional Information")
        
        try:
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fruityvice_response.raise_for_status()
            fv_df = pd.json_normalize(fruityvice_response.json())
            st.dataframe(fv_df)
        except requests.RequestException as e:
            st.error(f"Error fetching data for {fruit_chosen}: {e}")

# Create variable for inserting data into orders table if not null
if ingredients_list and title:
    my_insert_stmt = f"""
    INSERT INTO smoothies.public.orders (ingredients, name_on_order)
    VALUES ('{ingredients_string}', '{title}')
    """
    
    # Create variable for submit button
    time_to_insert = st.button("Submit to order")
    
    # Submit order with insert statement to database when button is not null / selected
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your smoothie is ordered! {title}", icon="✅")
        except Exception as e:
            st.error(f"Error placing order: {e}")
else:
    if not title:
        st.warning("Please enter a name for your smoothie.")
