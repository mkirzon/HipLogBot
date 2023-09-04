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
        },
        "activity_with_weight": {
            "queryResult": {
                "queryText": "yesterday",
                "parameters": {
                    "activity": "Hip Adductions",
                    "weight": {"amount": 10, "unit": "kg"},
                    "date": "2023-08-30T12:00:00+01:00",
                    "duration": "",
                    "reps": "",
                },
                "intent": {"displayName": "LogActivity"},
            }
        },
        "pain_basic": {
            "queryResult": {
                "parameters": {
                    "pain_level": "2",
                    "body_part": "Left hip",
                    "date": "2023-08-31T12:00:00+01:00",
                },
                "intent": {
                    "displayName": "LogPain",
                },
            }
        },
    }

    return x


# Tests for DailyLog class
def test_intent_initialization_for_activity(sample_requests):
    intent = Intent(sample_requests["activity_basic"])
    assert intent._type == "LogActivity"
    assert intent._raw_entity == {
        "date": "2023-07-24T12:00:00+01:00",
        "activity": "Yoga",
    }
    assert intent._date == "2023-07-24"


def test_intent_initialization_with_weight(sample_requests):
    intent = Intent(sample_requests["activity_with_weight"])
    assert intent.log_input == {
        "name": "Hip Adductions",
        "weight": {"amount": 10, "unit": "kg"},
    }


def test_intent_initialization_for_pain(sample_requests):
    intent = Intent(sample_requests["pain_basic"])
    assert intent._date == "2023-08-31"
    assert intent._log_input == {"name": "Left Hip", "level": 2}


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
