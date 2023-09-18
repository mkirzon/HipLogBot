import pytest

from models.intent import Intent


@pytest.fixture
def sample_requests():
    x = {
        "LogActivity_1": {
            "queryResult": {
                "parameters": {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"},
                "intent": {
                    "displayName": "LogActivity",
                },
            },
            "originalDetectIntentRequest": {
                "source": "facebook",
                "payload": {
                    "data": {
                        "sender": {"id": "23970740102517391"},
                    }
                },
            },
        },
        "LogActivity_with_weight": {
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
        "LogPain_1": {
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
        "GetDailyLog_1": {
            "queryResult": {
                "queryText": "What have I done today?",
                "parameters": {"date": "2023-09-05T12:00:00+01:00"},
                "intent": {
                    "displayName": "GetDailyLog",
                },
            }
        },
        "get_activity_summary": {
            "queryResult": {
                "parameters": {"activity": "Yoga"},
                "intent": {
                    "name": "projects/hip-log-bot/agent/intents/0a2df690-4073-45f6-8a55-6111a98bda0d",  # noqa
                    "displayName": "GetActivitySummary",
                },
            }
        },
    }

    return x


# Tests for DailyLog class
def test_intent_initialization_for_activity(sample_requests):
    intent = Intent(sample_requests["LogActivity_1"])
    assert intent._type == "LogActivity"
    assert intent._raw_entity == {
        "date": "2023-07-24T12:00:00+01:00",
        "activity": "Yoga",
    }
    assert intent._date == "2023-07-24"
    assert intent.user == "23970740102517391"


def test_intent_initialization_with_weight(sample_requests):
    intent = Intent(sample_requests["LogActivity_with_weight"])
    assert intent.log_input == {
        "name": "Hip Adductions",
        "weight": {"amount": 10, "unit": "kg"},
    }


def test_intent_initialization_for_pain(sample_requests):
    intent = Intent(sample_requests["LogPain_1"])
    assert intent._date == "2023-08-31"
    assert intent._log_input == {"name": "Left Hip", "level": 2}


def test_intent_initialization_for_get_daily_log(sample_requests):
    intent = Intent(sample_requests["GetDailyLog_1"])
    assert intent.type == "GetDailyLog"
    assert intent.date == "2023-09-05"
    assert intent.name == "mark"


def test_intent_initialization_for_get_activity_summary(sample_requests):
    intent = Intent(sample_requests["get_activity_summary"])
    assert intent.type == "GetActivitySummary"


def test_invalid_intent_type():
    req = {
        "queryResult": {
            "parameters": {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"},
            "intent": {
                "displayName": "LogNewThing",
            },
        }
    }
    with pytest.raises(ValueError, match="Unsupported intent passed"):
        Intent(req)


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
    intent = Intent(sample_requests["LogActivity_1"])
    assert intent.type == "LogActivity"
    assert intent.entity == {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"}
    assert intent.log_input == {"name": "Yoga"}
    assert intent.date == "2023-07-24"


def test_extract_date():
    assert Intent.extract_date("2023-07-24T12:00:00+01:00") == "2023-07-24"


# TODO: test that empty attributes are removed (tbd if this should live here or record)
def test_missing_attributes_skipped():
    pass


# TODO
def test_new_attributes_are_tbd():
    # What happens at the intent level if eg an activity has some new parameter we didn't expect (eg location=park) # noqa
    pass
