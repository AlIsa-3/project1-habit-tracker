import streamlit as st
import os

from cls_svcs import HabitTracker

st.write(
    "Edit Session Data (In order to save: 'Save Data' on the left must be clicked)"
)
with st.form("data_editor"):
    edited_data = st.data_editor(st.session_state.data)

    submitted = st.form_submit_button("Save Changes")

    if submitted:
        if edited_data is not None:
            st.session_state.data = HabitTracker(edited_data)
if "delete_button_clicked" not in st.session_state:
    st.session_state["delete_button_clicked"] = False

if st.sidebar.button("Delete All Data"):
    st.session_state["delete_button_clicked"] = True

if st.session_state["delete_button_clicked"]:
    if st.checkbox("This action is permanent and cannot be undone: "):
        os.remove("habit_data.csv")
        st.session_state["delete_button_clicked"] = False
        st.session_state["data"] = None


if st.sidebar.button("Save Data"):
    st.session_state.data.to_csv("habit_data.csv")
