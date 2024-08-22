# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
from snowflake.snowpark.functions import when_matched

# Write directly to the app
st.title("Smoothie Orders to Complete :cook:")
st.write(
    """See the orders below and tick when complete!
    """
)

# Get the current credentials
session = get_active_session()
my_dataframe = session.table("smoothies.public.orders").filter(col('order_filled') == 0).to_pandas()

# st.dataframe(data=my_dataframe, use_container_width=True)

if not my_dataframe.empty:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')
    if submitted:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df, schema=my_dataframe.dtypes.to_dict())

        try:
            og_dataset.merge(
                edited_dataset,
                (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID']),
                [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
            ) 
            st.success("Order Updated", icon='👍')
        except Exception as e:
            st.write('Something went wrong:', e)
else:
    st.success('There are no pending orders right now')
