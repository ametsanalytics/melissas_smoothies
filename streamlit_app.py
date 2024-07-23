# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests



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
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# create ingredients list
ingredients_list = st.multiselect(
    "choose up to 5 ingredients: "
    , my_dataframe
    , max_selections=5
)

# create conditional loop for sending requests to database
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
            ingredients_string += fruit_chosen + ' '
            st.subheader(fruit_chosen + 'Nutritional Information')
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
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

