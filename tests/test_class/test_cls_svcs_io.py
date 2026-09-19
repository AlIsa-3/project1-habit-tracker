from cls_svcs import HabitTracker
import pandas as pd
import pandas.testing as pd_test
import pytest


@pytest.fixture
def sample_df():
    return HabitTracker(
        [
            {
                "habit": "habit1",
                "frequency": "1w",
                "category": "habits",
                "target_goal": 3,
                "entry_date": pd.to_datetime("2022/04/03"),
                "start_date": pd.to_datetime("2022/04/05"),
                "due_date": pd.to_datetime("2022/04/05"),
                "completion_date": pd.to_datetime("2022/04/06"),
                "complete": True,
                "enabled": True,
            },
            {
                "habit": "habit1",
                "frequency": "1w",
                "category": "habits",
                "target_goal": 3,
                "entry_date": pd.to_datetime("2022/04/03"),
                "start_date": pd.to_datetime("2022/04/05"),
                "due_date": pd.to_datetime("2022/06/05"),
                "completion_date": pd.NaT,
                "complete": False,
                "enabled": True,
            },
        ]
    )


expected_output = {
    "habit": "bowling",
    "frequency": "6m",
    "category": "entertainment",
    "target_goal": 2,
    "entry_date": pd.to_datetime("2025/05/06"),
    "start_date": pd.to_datetime("2026/03/03"),
    "due_date": pd.to_datetime("2026/03/03"),
    "completion_date": pd.NaT,
    "complete": False,
    "enabled": True,
}

simulated_input = {
    "habit": "Bowling",
    "frequency": "6M",
    "category": "Entertainment",
    "target_goal": 2,
    "start_date": "2026/03/03",
}

sim_entry_date = "2025/05/06"

inputs = iter(simulated_input.values())


def test_add_new_habit(monkeypatch, sample_df):
    monkeypatch.setattr("builtins.input", lambda *args: next(inputs))
    sample_df.add_new_habit(entry_date=sim_entry_date)
    print(sample_df.iloc[-1])
    print(pd.Series(expected_output))
    pd_test.assert_series_equal(
        sample_df.iloc[-1].rename(None), pd.Series(expected_output)
    )


def test_log_completion(monkeypatch, sample_df):
    monkeypatch.setattr("builtins.input", lambda *args: 1)
    completion_date = pd.to_datetime("2020/09/08")
    sample_df.log_completion("habit1", completion_date=completion_date)
    assert sample_df.loc[1, ["completion_date", "complete"]].to_dict() == {
        "completion_date": completion_date,
        "complete": True,
    }


def test_parse_frequency(sample_df):
    assert sample_df._parse_frequency("2d") == pd.DateOffset(days=2)


expected_output_next_due = {
    "habit": "habit1",
    "frequency": "1w",
    "category": "habits",
    "target_goal": 3,
    "entry_date": pd.to_datetime("2022/04/03"),
    "start_date": pd.to_datetime("2022/04/05"),
    "due_date": pd.to_datetime("2022/04/13"),
    "completion_date": pd.NaT,
    "complete": False,
    "enabled": True,
}


def test_create_next_due(sample_df):
    sample_df._create_next_due("habit1")
    print(sample_df.iloc[-1].rename(None))
    pd_test.assert_series_equal(
        sample_df.iloc[-1].rename(None), pd.Series(expected_output_next_due)
    )
