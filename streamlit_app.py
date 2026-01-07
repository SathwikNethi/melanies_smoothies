import streamlit as st

st.set_page_config(page_title="Melanie's Smoothies", page_icon="🥤")

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input("Name on Smoothie:")

if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# Fruit options (NO Snowflake)
fruit_options = [
    "Banana", "Apple", "Mango", "Strawberry",
    "Blueberry", "Orange", "Pineapple", "Kiwi"
]

# Multiselect (LIMIT TO 5)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Submit button
submit_order = st.button("Submit Order")

if submit_order and name_on_order and ingredients_list:
    st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")
    st.write("**Ingredients:**", ", ".join(ingredients_list))
