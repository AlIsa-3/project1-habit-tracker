import streamlit as st
import pandas as pd

import data_svcs

from cls_svcs import HabitTracker


# Load data -- if not found then initialize without values
def startup():
    try:
        data = HabitTracker(data_svcs.read_csv_data())
    except FileNotFoundError:
        columns = [
            "habit",
            "frequency",
            "category",
            "target_goal",
            "entry_date",
            "start_date",
            "due_date",
            "completion_date",
            "complete",
            "enabled",
        ]
        types = [
            "str",
            "str",
            "str",
            "int",
            "datetime64[s]",
            "datetime64[s]",
            "datetime64[s]",
            "datetime64[s]",
            "bool",
            "bool",
        ]
        data = HabitTracker(
            {
                column: pd.Series(dtype=data_type)
                for column, data_type in zip(columns, types)
            }
        )

    return data


st.title("Habit Tracker App")
st.write("⟵ Select an option on the left")

if "data" not in st.session_state:
    st.session_state["data"] = None

if st.session_state["data"] is None:
    st.session_state["data"] = startup()

