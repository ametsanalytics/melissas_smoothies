# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd
import numpy as np



# Write directly to the app
st.title("Customise Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

#add name and instruction
title = st.text_input("Name on Smoothie: ", "")
st.write("The name on your smoothie will be:", title)

# connect
cnx = st.connection("snowflake")
session = cnx.session()

# create dataframe for to use in ingredients list
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))


# convert Snowpark datafram to pandas dataframe for loc function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)

    
max_selections = 5

# create ingredients list
ingredients_list = st.multiselect(
    "choose up to 5 ingredients: "
    , my_dataframe
    , max_selections=max_selections
)

# create conditional loop for sending requests to database
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '

            search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
         
            st.subheader(fruit_chosen + ' Nutritional Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width = True)

# create variable for inserting data into orders table if not null

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + title + """')"""
    
# create variable for submit button
    time_to_insert = st.button("Submit to order")

# submit order with insert staement to database when button is not null / selected

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie is ordered! '+ title, icon="✅")
