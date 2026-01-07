import streamlit as st
import requests
from snowflake.snowpark.functions import col

# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# SNOWFLAKE CONNECTION
# --------------------------------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# --------------------------------------------------
# USER INPUT
# --------------------------------------------------
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# --------------------------------------------------
# LOAD FRUIT OPTIONS (DISPLAY + SEARCH VALUE)
# --------------------------------------------------
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)

fruit_rows = fruit_df.collect()

fruit_display = [row["FRUIT_NAME"] for row in fruit_rows]

fruit_lookup = {
    row["FRUIT_NAME"]: row["SEARCH_ON"]
    for row in fruit_rows
}

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_display,
    max_selections=5
)

# --------------------------------------------------
# SUBMIT ORDER
# --------------------------------------------------
ingredients_string = " ".join(ingredients_list)

if st.button("Submit Order") and name_on_order and ingredients_list:
    session.sql(
        """
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES (?, ?)
        """,
        params=[name_on_order, ingredients_string]
    ).collect()

    st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

# --------------------------------------------------
# SMOOTHIEFRUIT NUTRITION INFO
# --------------------------------------------------
if ingredients_list:
    st.header("🥝 SmoothieFruit Nutrition Information")

    for fruit in ingredients_list:
        search_term = fruit_lookup.get(fruit)

        st.subheader(f"{fruit} Nutrition Information")

        try:
            response = requests.get(
                f"https://my.smoothiefruit.com/api/fruit/{search_term}",
                timeout=10
            )

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning("⚠️ Nutrition data not found for this fruit.")

        except requests.exceptions.RequestException:
            st.warning(
                "⚠️ Unable to connect to SmoothieFruit API due to SSL restrictions on Streamlit Community Cloud."
            )




