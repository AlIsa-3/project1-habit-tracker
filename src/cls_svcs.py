from __future__ import annotations
import pandas as pd
import streamlit as st

import data_svcs as data
import api_svc as api


class HabitTracker(pd.DataFrame):
    def _calc_streaks(self, habit: str) -> pd.Series[int]:
        """Calculates the streaks for a given habit

        Args:
            habit: the habit to calculate streaks for
        Returns:
            pandas series object containing all the streaks for the given habit
        """
        habit_df = self[self["habit"] == habit]
        condition = habit_df["complete"].ne(habit_df["complete"].shift()).cumsum()
        return habit_df.groupby(condition).cumcount().clip(1)

    def get_current_streak(self, habit: str) -> int:
        """
        Calculates and returns the latest streak value for the given habit

        Args:
            habit: the habit to find the latest streak for

        Returns:
            an integer representing the current streak for the given habit
        """
        return self._calc_streaks(habit).iloc[-1]

    def get_best_streak(self, habit: str) -> int:
        """Returns the highest streak for the given habit

        Args:
            habit: the habit to find the highest streak for

        Returns:
            the integer representing the highest streak for the given habit
        """
        return self._calc_streaks(habit).sort_values(ascending=False).iloc[0]

    def calc_completion_rates(self) -> pd.Series[float]:
        """
        Calculates completion rate for every habit in the data

        Args:
            None
        Returns:
            returns a pandas series object containing the completion rates for each habit in the data
        """
        return self.groupby(["habit"])["complete"].mean()

    def calc_completion_time_ranges(
        self, n: int = 1, hour_range: int = 6
    ) -> dict[str, str]:
        """
        Returns the top 'n' time ranges for habit completion

        Args:
            n: an integer representing the top 'n' time ranges for habit completion to return
            hour_range: split the 24 hour day into ranges of hours of length hour_range. e.g. 0 - 6, 6 - 12, 12 - 18.
        Returns:
            dictionary of habits and their optimal time ranges for completion
        """
        ranges = (
            self.groupby(
                [
                    pd.to_datetime(self["completion_date"]).dt.hour // hour_range,
                    "habit",
                    "category",
                ]
            )["complete"]
            .aggregate(["mean", "sum"])
            .sort_values(by=["mean", "sum"], ascending=False)
            .groupby(["habit", "category"])
            .head(n)
        )

        return {
            "+".join(
                [habit, category]
            ): f"{time_range*hour_range} - {(time_range+1) * hour_range}"
            for time_range, habit, category in ranges.index
        }

    # Data IO:

    def add_new_habit(
        self,
        habit_name: str,
        frequency: str,
        category: str,
        target_goal: int,
        start_date: str,
        entry_date=None,
    ) -> pd.DataFrame:
        """
        Add a new habit to track

        Args:
            entry_date: an optional argument that allows you to specify an entry date.
                        default is the current time.
        """
        habit_name = data.DataParsing.format_str_input(habit_name)
        frequency = data.DataParsing.format_str_input(frequency)
        category = data.DataParsing.format_str_input(category)
        target_goal = data.DataParsing.parse_integer(target_goal)
        start_date = data.DataParsing.format_str_input(start_date)

        enabled = True
        complete = False
        date_completed = pd.NaT
        due_date = start_date

        habit_dict = {
            "habit": habit_name,
            "frequency": frequency,
            "category": category,
            "target_goal": target_goal,
            "entry_date": pd.to_datetime(entry_date)
            if entry_date
            else pd.Timestamp.now(tz="utc").strftime("%Y-%m-%d %H:%M:%S"),
            "start_date": pd.to_datetime(start_date),
            "due_date": pd.to_datetime(due_date),
            "completion_date": pd.to_datetime(date_completed),
            "complete": complete,
            "enabled": enabled,
        }
        return pd.DataFrame([habit_dict])

    def log_completion(
        self,
        id: int,
        habit: str | None = None,
        completion_date: str | None = None,
    ) -> None:
        """
        Log completion of a habit and create the record for its next due date.

        Args:
            habit: optional argument to specify the habit to log, otherwise the option to select is given.
            completion_date: optional argument to specify the completion date, default is the time of logging.
            max_display: the maximum number of records to show for selection, default is 10.
        """
        completion_date = (
            pd.to_datetime(completion_date)
            if completion_date
            else pd.Timestamp.now(tz="utc").strftime("%Y:%m:%d %H:%M:%S")
        )
        self.loc[id, ["completion_date", "complete"]] = [
            pd.to_datetime(completion_date),
            True,
        ]

        if not habit:
            habit = self.loc[id, "habit"]

        # Display Streak Rewards
        self._streak_reward(habit)

        # Create record for the next due date
        self._create_next_due(habit)

    def _create_next_due(self, habit):
        """
        Creates the next record for a habit, including its new due date.
        Args:
            habit: the habit for which to create the record for.
        """
        most_recent = self[(self["habit"] == habit) & (self["complete"] == True)].iloc[
            -1
        ]
        prev_completion_date = most_recent["completion_date"]
        new_due_date = prev_completion_date + self._parse_frequency(
            most_recent["frequency"]
        )
        new_row = most_recent.to_dict()
        new_row["due_date"] = new_due_date
        new_row["completion_date"] = pd.NaT
        new_row["complete"] = None

        self.loc[len(self)] = new_row

    def _parse_frequency(self, frequency_str: str) -> pd.DateOffset:
        """
        Using the frequency set for habit, determines when the next due date for that habit is.

        Args:
            frequency_str: the string value stored in the data for a habit which specifies its frequency
        """
        unit = frequency_str[1]
        count = int(frequency_str[0])

        match unit:
            case "y":
                return pd.DateOffset(years=count)
            case "m":
                return pd.DateOffset(months=count)
            case "w":
                return pd.DateOffset(weeks=count)
            case "d":
                return pd.DateOffset(days=count)
            case _:
                return pd.DateOffset(days=0)

    # Display

    def display_stats(self) -> None:
        """
        Displays streak and completion rate stats for all habits
        """
        st.write("Habit Streak and Completion Stats\n\n")
        for habit, category in self[["habit", "category"]].drop_duplicates().values:
            output_string = str(
                f"Habit: {habit} Category: {category}\n\nCurrent Streak = {self.get_current_streak(habit)} Best Streak = {self.get_best_streak(habit)}"
                + f" Completion Rate = {self.calc_completion_rates().loc[habit]:.2%}"
            )

            st.write(output_string)
            time_ranges = self.calc_completion_time_ranges()
            try:
                st.write(
                    f"Most Successful Completion Time Range: {time_ranges[f"{habit}+{category}"]} hrs"
                )
                # Sometimes there is a KeyError pass if it occurs
            except KeyError:
                pass

    def display_habits(self) -> None:
        """Displays most fields for one record of each unique habit"""
        habits = self.groupby(["habit", "category"])[
            [
                "habit",
                "frequency",
                "target_goal",
                "category",
                "entry_date",
                "start_date",
                "enabled",
            ]
        ].tail(1)
        st.write(habits)

    def _streak_reward(self, habit: str) -> None:
        """
        Display message depending on the current streak for the given habit
        Args:
            habit:str the current habit which is being logged
        """
        current_streak = self.get_current_streak(habit)

        if current_streak == 1:
            st.toast("Congratulations!")
        elif current_streak == 2:
            st.toast("This is your second day!")
        elif current_streak == 3:
            st.toast("Well done!")
        elif current_streak >= 4:
            # Display a quote otherwise
            quote, author = api._get_quote(api._get_response())
            st.toast(f"{quote} \n - {author} \n\n Quotes provides by ZenQuotes API")
        else:
            pass
