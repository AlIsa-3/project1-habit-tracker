from __future__ import annotations
import pandas as pd
import stats_svcs as stats

habit = "Bowling"
sample_data = pd.DataFrame(
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
        stats.streaks._calc_streaks(sample_data, habit)
        == pd.Series({0: 1, 2: 1, 3: 2, 4: 3, 5: 1, 6: 1})
    ).all()


def test_get_current_streak():
    assert stats.streaks.get_current_streak(sample_data, habit) == 1


def test_get_best_streak():
    assert stats.streaks.get_best_streak(sample_data, habit) == 3


def test_calc_completion_rates():
    assert (
        stats.calc_completion_rates(sample_data)
        == pd.Series({"Bowling": 5 / 6, "Swimming": 1})
    ).all()


def test_calc_completion_time_ranges():
    assert stats.calc_completion_time_ranges(sample_data, n=1, hour_range=4) == {
        "Bowling": "20 - 24",
        "Swimming": "0 - 4",
    }
