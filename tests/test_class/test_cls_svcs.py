from cls_svcs import HabitTracker
import pandas as pd

habit = "Bowling"
sample_data = HabitTracker(
    data={
        "date": pd.to_datetime(
            [
                "2026-05-03 19:00:00",
                "2026-05-04 01:00:00",
                "2026-05-05 22:00:00",
                "2026-05-06 22:00:00",
                "2026-05-07 22:00:00",
                "2026-05-08 15:00:00",
                "2026-05-09 04:00:00",
            ]
        ),
        "habit": [
            "Bowling",
            "Swimming",
            "Bowling",
            "Bowling",
            "Bowling",
            "Bowling",
            "Bowling",
        ],
        "complete": [True, True, True, True, True, False, True],
    }
)


def test_calc_streaks():
    assert (
        sample_data._calc_streaks(habit)
        == pd.Series({0: 1, 2: 1, 3: 2, 4: 3, 5: 1, 6: 1})
    ).all()


def test_get_current_streak():
    assert sample_data.get_current_streak(habit) == 1


def test_get_best_streak():
    assert sample_data.get_best_streak(habit) == 3


def test_calc_completion_rates():
    assert (
        sample_data.calc_completion_rates()
        == pd.Series({"Bowling": 5 / 6, "Swimming": 1})
    ).all()


def test_calc_completion_time_ranges():
    assert sample_data.calc_completion_time_ranges(n=1, hour_range=4) == {
        "Bowling": "20 - 24",
        "Swimming": "0 - 4",
    }
