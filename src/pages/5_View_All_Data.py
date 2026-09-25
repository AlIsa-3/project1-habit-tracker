import streamlit as st

st.write("All Habit Data Stored:")
st.dataframe(st.session_state.data)