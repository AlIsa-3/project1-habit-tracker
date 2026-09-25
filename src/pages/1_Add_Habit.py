import streamlit as st
import pandas as pd
import time
from cls_svcs import HabitTracker

    
if 'new_habit_submitted' not in st.session_state:
    st.session_state['new_habit_submitted'] = False

# User input for habit addition
with st.form("new_habit",clear_on_submit=True):
    habit_name = st.text_input("Enter the habit name: ")
    frequency = st.text_input("Enter the frequency in the form X[D/W/M/Y] e.g. 3W is once every 3 weeks: ")
    category = st.text_input("Enter the habit category: ")
    target_goal = st.text_input("Enter the target number of repetitions, e.g. 5 means the habit will happen 5 times total: ")
    start_date = st.text_input("Enter the start date as YYYY/MM/DD: ") 
    # Pandas will silently correct an improper input that has a standard form e.g. DD/MM/YYYY will work 
    submitted = st.form_submit_button("Submit")

if submitted:
    # Habit Name Required
    if not habit_name:
        st.error("Habit Name is Required")
    elif (not frequency[0].isalnum()) or frequency[-1] not in ['D','M','W','Y','d','m','w','y']:
        st.error("Frequency Field has Invalid Input")
    elif not category:
        st.error("Habit Category is Required")
    elif int(target_goal) < 1:
        st.error("Target goal must be an integer greater than 0")
    else:
        st.session_state['new_habit_submitted'] = True
        st.session_state.new_row = st.session_state["data"].add_new_habit(
            habit_name, frequency, category, target_goal, start_date
        )

        st.session_state["data"] = HabitTracker(
            pd.concat(
                [st.session_state["data"], st.session_state["new_row"]], ignore_index=True
            )
        )

        st.session_state["new_row"] = None


if st.session_state['new_habit_submitted']:
    success = st.success("Habit Added to Current Session Data Successfully. To save changes, navigate to the 'Edit Data' Tab.")
    st.session_state['new_habit_submitted'] = False
    time.sleep(3)
    success.empty()