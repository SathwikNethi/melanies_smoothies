# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Connect to Snowflake (SniS way)
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# Get fruit options
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
    .collect()
)

# Convert Snowflake rows to list
fruit_list = [row["FRUIT_NAME"] for row in fruit_df]

# Multiselect (LIMIT TO 5)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Submit button
submit_order = st.button("Submit Order")

if submit_order and name_on_order and ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    insert_stmt = f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
    """
    session.sql(insert_stmt).collect()

    st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
