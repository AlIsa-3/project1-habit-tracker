import streamlit as st

st.write("Habits Currently Available to be Completed:")

st.write(
    st.session_state.data[
        (st.session_state.data["complete"] != True)
        & st.session_state.data["enabled"]
        == True
    ][['habit','frequency','category','target_goal','start_date','due_date']].head(10)
)
with st.form("log_habit_form",clear_on_submit=True):
    id = st.text_input("Select record ID: ")
    submitted = st.form_submit_button("Submit")
if submitted:
    st.session_state["data"].log_completion(int(id))
    st.rerun()
