from __future__ import annotations
import pandas as pd


class streaks:
    """
    Contains methods related to streak calculations
    """

    @classmethod
    def _calc_streaks(cls, df: pd.DataFrame, habit: str) -> pd.Series[int]:
        """
        Returns pandas Series of streaks as consecutive 'number of completions'
        It is assumed that the task is completed when it is due, so incomplete tasks, as well as isolated ones
        are treated as having a streak of '1'

        Args:
            habit_status: pandas Series object containing the streaks
        """

        habit_df = df[df["habit"] == habit]
        condition = habit_df["complete"].ne(habit_df["complete"].shift()).cumsum()
        return habit_df.groupby(condition).cumcount().clip(1)

    @classmethod
    def get_current_streak(cls, df: pd.DataFrame, habit: str) -> int:
        """
        Calculates and returns the latest streak value for the given habit

        Args:
            df - pandas dataframe containing habits and completion states. At minimum expects fields ['complete','habit']
            habit - string representation of the habit, expected to be in df
        Returns:
            The current completion streak for a given habit
        """
        return cls._calc_streaks(df, habit).iloc[-1]

    @classmethod
    def get_best_streak(cls, df: pd.DataFrame, habit: str) -> int:
        """
        Returns the highest streak for the given habit

        Args:
            df - pandas dataframe containing habits and completion states At minimum expects fields ['complete','habit']
            habit - string representation of the habit, expected to be in df'
        Returns:
            highest streak found, regardless of whether it is current or not
        """
        return cls._calc_streaks(df, habit).sort_values(ascending=False).iloc[0]


def calc_completion_rates(df: pd.DataFrame) -> pd.Series[float]:
    """
    Calculates completion rate for every habit in the data
    Args:
        df - pandas dataframe containing habits and completion states At minimum expects fields ['complete','habit']
    """
    return df.groupby(["habit"])["complete"].mean()


def calc_completion_time_ranges(
    df: pd.DataFrame, n: int, hour_range: int = 6
) -> dict[str, str]:
    """
    Returns the top 'n' time ranges for habit completion. Orders them based on mean completion rates and total completions.

    Args:
        df - pandas dataframe containing habits and completion states At minimum expects fields ['complete','habit','date']
        n: integer representing the number of results for each habit returned. e.g. n = 1 will return the top 1 for each habit
        hour_range: integer representing the range of hours to aggregate. e.g. hour_range = 4 will split the day into 4 hour intervals

    Returns:
        dictionary containing the habits and their n most successful completion times. e.g. {'Habit1':'12 - 16','Habit2': '0 - 4'}
    """
    ranges = (
        df.groupby([df["date"].dt.hour // hour_range, "habit"])["complete"]
        .aggregate(["mean", "sum"])
        .sort_values(by=["mean", "sum"], ascending=False)
        .groupby(["habit"])
        .head(n)
    )

    return {
        habit: f"{time_range*hour_range} - {(time_range+1) * hour_range}"
        for time_range, habit in ranges.index
    }
