import streamlit as st
import requests
from snowflake.snowpark.functions import col

# --------------------------------------------------
# Page Title
# --------------------------------------------------
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# --------------------------------------------------
# Snowflake Connection
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

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# --------------------------------------------------
# Fruit Selection
# --------------------------------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# --------------------------------------------------
# Submit Order to Snowflake
# --------------------------------------------------
ingredients_string = " ".join(ingredients_list)

if st.button("Submit Order"):
    if name_on_order and ingredients_list:
        session.sql(
            f"""
            INSERT INTO smoothies.public.orders (name_on_order, ingredients)
            VALUES ('{name_on_order}', '{ingredients_string}')
            """
        ).collect()

        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
    else:
        st.warning("Please enter your name and select at least one ingredient.")

# --------------------------------------------------
# SmoothieFruit Nutrition Section
# --------------------------------------------------
if ingredients_list:
    st.markdown("## 🥝 SmoothieFruit Nutrition Information")

    for fruit_chosen in ingredients_list:
        st.subheader(f"{fruit_chosen} Nutrition Information")

        api_url = f"https://my.smoothiefruit.com/api/fruit/{fruit_chosen.lower()}"

        try:
            response = requests.get(api_url, timeout=10)

            if response.status_code == 200:
                st.dataframe(response.json(), use_container_width=True)
            else:
                st.warning(f"⚠️ {fruit_chosen} not found in SmoothieFruit database.")

        except requests.exceptions.SSLError:
            st.warning(
                "⚠️ Unable to connect to SmoothieFruit API due to SSL restrictions "
                "on Streamlit Community Cloud."
            )
        except Exception as e:
            st.error(f"Unexpected error for {fruit_chosen}: {e}")



