from __future__ import annotations
import pandas as pd

import data_svcs as data


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
            self.groupby([self["date"].dt.hour // hour_range, "habit"])["complete"]
            .aggregate(["mean", "sum"])
            .sort_values(by=["mean", "sum"], ascending=False)
            .groupby(["habit"])
            .head(n)
        )

        return {
            habit: f"{time_range*hour_range} - {(time_range+1) * hour_range}"
            for time_range, habit in ranges.index
        }

    # Data IO:

    def add_new_habit(self, entry_date=None) -> None:
        """
        Add a new habit to track

        Args:
            entry_date: an optional argument that allows you to specify an entry date.
                        default is the current time.
        """
        habit_name = data.DataParsing.format_str_input(input("Enter the habit name: "))
        frequency = data.DataParsing.format_str_input(
            input("Enter the frequency in the form X[D/M/Y]: ")
        )
        category = data.DataParsing.format_str_input(
            input("Enter the habit category: ")
        )
        target_goal = data.DataParsing.parse_integer(
            input("Enter the target number of repetitions: ")
        )
        start_date = data.DataParsing.format_str_input(
            input("Enter the start date as YYYY/MM/DD: ")
        )
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
            else pd.Timestamp.now(tz="utc").strftime("%Y%m%d %H%M%S"),
            "start_date": pd.to_datetime(start_date),
            "due_date": pd.to_datetime(due_date),
            "completion_date": pd.to_datetime(date_completed),
            "complete": complete,
            "enabled": enabled,
        }

        self.loc[len(self)] = habit_dict

    def log_completion(
        self,
        habit: str | None = None,
        completion_date: str | None = None,
        max_display: int = 10,
    ) -> None:
        """
        Log completion of a habit and create the record for its next due date.

        Args:
            habit: optional argument to specify the habit to log, otherwise the option to select is given.
            completion_date: optional argument to specify the completion date, default is the time of logging.
            max_display: the maximum number of records to show for selection, default is 10.
        """
        # First get all records that are marked as incomplete
        if habit:
            print(
                self[(self["habit"] == habit) & (self["complete"] == False)].head(
                    max_display
                )
            )

        else:
            print(self[(self["complete"] == False)].head(max_display))
        id = int(input("Select record id: "))
        completion_date = (
            pd.to_datetime(completion_date)
            if completion_date
            else pd.Timestamp.now(tz="utc").strftime("%Y%m%d %H%M%S")
        )
        self.loc[id, ["completion_date", "complete"]] = [completion_date, True]

        if not habit:
            habit = self.loc[id, "habit"]

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
        new_row["complete"] = False

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

    def display_stats(self):
        """
        Displays streak and completion rate stats for all habits
        """
        print("Habit Streak and Completion Stats")
        for habit in self["habit"].unique():
            output_string = str(
                f"Habit: {habit} Current Streak = {self.get_current_streak(habit)} Best Streak = {self.get_best_streak(habit)}"
                + f" Completion Rate = {self.calc_completion_rates().loc[habit]:.2%}"
            )

            print(output_string)

    def display_habits(self):
        """Displays most fields for one record of each unique habit"""
        habits = self.groupby(["habit"])[
            [
                "habit",
                "frequency",
                "target_goal",
                "category",
                "entry_date",
                "start_date",
                "enabled",
            ]
        ].head(1)
        print(habits)
