import streamlit as st
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
# Get Fruit Options from Snowflake
# --------------------------------------------------
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

# Convert Snowpark DataFrame → Python list
fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# --------------------------------------------------
# Ingredient Selection
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

ingredients_string = " ".join(ingredients_list)

# --------------------------------------------------
# Submit Order
# --------------------------------------------------
if st.button("Submit Order") and name_on_order and ingredients_list:
    session.sql(
        f"""
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
        """
    ).collect()

    st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

# --------------------------------------------------
# SmoothieFruit Nutrition API Section
# --------------------------------------------------
st.header("🥝 SmoothieFruit Nutrition Information")

try:
    smoothiefruit_response = requests.get(
        "https://my.smoothiefruit.com/api/fruit/watermelon",
        timeout=10
    )

    # Show response status (for learning)
    st.text(smoothiefruit_response)

    if smoothiefruit_response.status_code == 200:
        st.dataframe(
            data=smoothiefruit_response.json(),
            use_container_width=True
        )
    else:
        st.warning("⚠️ SmoothieFruit API returned a non-200 response.")

except requests.exceptions.SSLError:
    st.warning(
        "⚠️ Unable to connect to SmoothieFruit API due to SSL restrictions "
        "on Streamlit Community Cloud. This is a known limitation."
    )

except requests.exceptions.RequestException as e:
    st.error(f"❌ API request failed: {e}")

