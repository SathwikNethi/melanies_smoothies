# =========================
# Imports (ALL at the top)
# =========================
import streamlit as st
import requests
from snowflake.snowpark.functions import col

# =========================
# App Title & Description
# =========================
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# =========================
# Snowflake Connection
# =========================
cnx = st.connection("snowflake")
session = cnx.session()

# =========================
# Name Input
# =========================
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# =========================
# Get Fruit Options from Snowflake
# =========================
fruit_df = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
    .select(col("FRUIT_NAME"))
)

fruit_list = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# =========================
# Ingredient Selection (Max 5)
# =========================
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# =========================
# Submit Order
# =========================
if st.button("Submit Order") and name_on_order and ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    session.sql(
        """
        INSERT INTO smoothies.public.orders (name_on_order, ingredients)
        VALUES (%s, %s)
        """,
        params=[name_on_order, ingredients_string],
    ).collect()

    st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")

# =========================
# SmoothieFruit Nutrition Section
# =========================
st.markdown("## 🥝 SmoothieFruit Nutrition Information")

if ingredients_list:
    try:
        nutrition_rows = []

        for fruit_chosen in ingredients_list:
            response = requests.get(
                f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}",
                timeout=5
            )

            if response.status_code == 200:
                fruit_json = response.json()

                for nutrient, value in fruit_json["nutritions"].items():
                    nutrition_rows.append({
                        "fruit": fruit_json["name"],
                        "family": fruit_json["family"],
                        "genus": fruit_json["genus"],
                        "order": fruit_json["order"],
                        "nutrient": nutrient,
                        "value": value
                    })

        if nutrition_rows:
            st.dataframe(nutrition_rows, use_container_width=True)

    except requests.exceptions.SSLError:
        st.warning(
            "⚠️ Unable to connect to SmoothieFruit API due to SSL restrictions on "
            "Streamlit Community Cloud. This is a known limitation."
        )

    except Exception as e:
        st.error(f"Unexpected error: {e}")


