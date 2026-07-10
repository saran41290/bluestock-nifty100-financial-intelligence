from src.etl.normaliser import normalize_ticker


def test_uppercase():
    assert normalize_ticker("tcs") == "TCS"


def test_strip_spaces():
    assert normalize_ticker(" INFY ") == "INFY"


def test_none():
    assert normalize_ticker(None) == ""