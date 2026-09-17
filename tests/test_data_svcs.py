from __future__ import annotations
import data_svcs as data
import pytest


def test_parse_data_exception():
    with pytest.raises(ValueError):
        data.DataParsing.parse_date("ABCD")


def test_parse_integer_exception():
    with pytest.raises(ValueError):
        data.DataParsing.parse_integer("Hello")
