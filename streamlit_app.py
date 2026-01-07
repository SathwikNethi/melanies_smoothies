import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# --------------------------------------------------
# App Title
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# Snowflake Connection (Streamlit Cloud)
# --------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# Name Input
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# --------------------------------------------------
# Load Fruit Options (FRUIT_NAME + SEARCH_ON)
# --------------------------------------------------
sf_df = (
    session
    .table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert to Pandas for lookup
pd_df = sf_df.to_pandas()

# --------------------------------------------------
# Multiselect (Display FRUIT_NAME only)
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# --------------------------------------------------
# Nutrition Section
# --------------------------------------------------
if ingredients_list:

    st.subheader("🥝 SmoothieFruit Nutrition Information")

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value using Pandas
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} Nutrition Information")

        try:
            response = requests.get(
                f"https://my.smoothiefruit.com/api/fruit/{search_on}",
                timeout=10
            )

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning(f"No nutrition data found for {fruit_chosen}")

        except requests.exceptions.RequestException:
            st.warning(
                "⚠️ Unable to reach SmoothieFruit API on Streamlit Cloud "
                "(SSL restriction). This is expected."
            )

# --------------------------------------------------
# Submit Order
# --------------------------------------------------
if st.button("Submit Order") and name_on_order and ingredients_list:

    session.sql(f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string.strip()}')
    """).collect()

    st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")






