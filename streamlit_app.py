# -------------------- IMPORTS --------------------
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# -------------------- PAGE SETUP --------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# -------------------- SNOWFLAKE CONNECTION --------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -------------------- NAME INPUT --------------------
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# -------------------- LOAD FRUIT OPTIONS --------------------
my_dataframe = (
    session
    .table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

# Convert Snowpark → Pandas
pd_df = my_dataframe.to_pandas()

# -------------------- MULTISELECT --------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# -------------------- PROCESS SELECTION --------------------
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Get SEARCH_ON value using Pandas loc
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.write(f"🔍 The search value for **{fruit_chosen}** is **{search_on}**")

        st.subheader(f"{fruit_chosen} Nutrition Information")

        # -------------------- API CALL --------------------
        try:
            api_url = f"https://my.smoothiefruit.com/api/fruit/{search_on}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning("⚠️ Fruit not found in SmoothieFruit database.")

        except requests.exceptions.SSLError:
            st.warning(
                "⚠️ Unable to connect to SmoothieFruit API due to SSL restrictions "
                "on Streamlit Community Cloud."
            )
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# -------------------- SUBMIT ORDER --------------------
if st.button("Submit Order") and name_on_order and ingredients_list:
    session.sql(
        f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
        """
    ).collect()

    st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")





