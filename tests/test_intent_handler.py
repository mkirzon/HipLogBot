import pytest
from src.services.intent_handler import Intent


@pytest.fixture
def sample_requests():
    x = {
        "activity_basic": {
            "queryResult": {
                "parameters": {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"},
                "intent": {
                    "displayName": "LogActivity",
                },
            }
        }
    }

    return x


# Tests for DailyLog class
def test_intent_initialization(sample_requests):
    intent = Intent(sample_requests["activity_basic"])
    assert intent._type == "LogActivity"
    assert intent._raw_entity == {
        "date": "2023-07-24T12:00:00+01:00",
        "activity": "Yoga",
    }
    assert intent._date == "2023-07-24"


def test_invalid_intent_type():
    req = {
        "queryResult": {
            "parameters": {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"},
            "intent": {
                "displayName": "LogNewThing",
            },
        }
    }
    with pytest.raises(ValueError):
        Intent(req)


# TODO: logactivity and logpain require date in their entity
def test_missing_date_for_activity():
    req = {
        "queryResult": {
            "parameters": {"activity": "Yoga"},
            "intent": {
                "displayName": "LogActivity",
            },
        }
    }

    with pytest.raises(ValueError, match="missing a date"):
        Intent(req)


def test_intent_properties(sample_requests):
    intent = Intent(sample_requests["activity_basic"])
    assert intent.type == "LogActivity"
    assert intent.entity == {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"}
    assert intent.log_input == {"name": "Yoga"}
    assert intent.date == "2023-07-24"


def test_extract_date():
    assert Intent.extract_date("2023-07-24T12:00:00+01:00") == "2023-07-24"
