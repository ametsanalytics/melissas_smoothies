# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(fruityvice_response)

# Write directly to the app
st.title("Customise Your Smoothie :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

#add name

title = st.text_input("Name on Smoothie: ", "")
st.write("The name on your smoothie will be:", title)

# connect
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

ingredients_list = st.multiselect(
    "choose up to 5 ingredients: "
    , my_dataframe
    , max_selections=5
)
if ingredients_list:
   # st.write(ingredients_list)
   # st.text(ingredients_list)

    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

   # st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" + title + """')"""
    
    # st.write(my_insert_stmt)
    time_to_insert = st.button("Submit to order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie is ordered! '+ title, icon="✅")
