from utils import is_valid_date_format


def test_is_valid_date_format_detects_good():
    assert is_valid_date_format("2023-01-01") is True


def test_is_valid_date_format_detects_bad():
    assert is_valid_date_format("223-01-01") is False
    assert is_valid_date_format("2023-01-01T00:00:00") is False
    assert is_valid_date_format("2023-1-1") is False
