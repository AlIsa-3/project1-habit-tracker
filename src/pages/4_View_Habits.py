import streamlit as st

st.write("Most Recent Entry for Each Habit:")
st.session_state.data.display_habits()
