"""
Unit tests for ETL normalization functions.
"""
import pytest
from src.etl.normaliser import normalize_ticker, normalize_year


def test_normalize_ticker_lowercase():
    assert normalize_ticker("tcs") == "TCS"


def test_normalize_ticker_spaces():
    assert normalize_ticker("  infy  ") == "INFY"


def test_normalize_ticker_none():
    assert normalize_ticker(None) == ""


def test_normalize_ticker_hyphen():
    assert normalize_ticker("bajaj-auto") == "BAJAJ-AUTO"


def test_normalize_ticker_ampersand():
    assert normalize_ticker("m&m") == "M&M"


def test_normalize_year_mar23():
    assert normalize_year("Mar-23") == "2023-03"


def test_normalize_year_mar_space_23():
    assert normalize_year("Mar 23") == "2023-03"


def test_normalize_year_march_2023():
    assert normalize_year("March-2023") == "2023-03"


def test_normalize_year_integer_string():
    assert normalize_year("2023") == "2023-03"


def test_normalize_year_fy23():
    assert normalize_year("FY23") == "2023-03"


def test_normalize_year_fy2024():
    assert normalize_year("FY2024") == "2024-03"


def test_normalize_year_dec22():
    assert normalize_year("Dec-22") == "2022-12"


def test_normalize_year_jun23():
    assert normalize_year("Jun-23") == "2023-06"


def test_normalize_year_already_normalized():
    assert normalize_year("2023-03") == "2023-03"


def test_normalize_year_garbage():
    assert normalize_year("garbage") == "PARSE_ERROR"


def test_normalize_year_xyz():
    assert normalize_year("xyz") == "PARSE_ERROR"


def test_normalize_year_empty():
    assert normalize_year("") == ""


def test_normalize_year_none():
    assert normalize_year(None) == ""


def test_normalize_year_sep21():
    assert normalize_year("Sep-21") == "2021-09"


def test_normalize_year_nov1995():
    assert normalize_year("Nov-95") == "1995-11"
