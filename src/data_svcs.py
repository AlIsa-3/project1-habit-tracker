from __future__ import annotations
import pathlib
import pandas as pd

# Habits stored as: Habit | Frequency | Target Goal | Category | Date Entered | Date Completed | Date Started | due_date | complete [True/False] | status (enabled or not) [True/False]


def read_csv_data(
    csv_filename: str | pathlib.Path = pathlib.Path("habit_data.csv"),
) -> pd.DataFrame:
    return pd.read_csv(
        csv_filename,
        parse_dates=["start_date", "completion_date", "due_date", "entry_date"],
    )


class DataParsing:
    @classmethod
    def parse_date(cls, date: str) -> pd.Timestamp:
        try:
            return pd.to_datetime(date, utc=True)
        except Exception as e:
            print("Failed to parse date", e)
            raise ValueError

    @classmethod
    def format_str_input(cls, user_input: str) -> str:
        """
        When given a pandas series object containing str, remove leading and trailing whitespace
        and change input to lower case.
        Args:
            user_input: pandas series object containing str data
        Returns:
            mutated input with leading and trailing whitespace removed, changed to lower case
        Raises:
            None
        """
        return user_input.strip().lower()

    @classmethod
    def parse_integer(cls, value: str) -> int:
        try:
            return int(value)
        except ValueError as e:
            raise ValueError(f"Invalid value {value}", e)
