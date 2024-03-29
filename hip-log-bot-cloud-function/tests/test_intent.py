import logging
import pytest
from models.intent import Intent
from datetime import date


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
        "LogActivity_with_sets": {
            "queryResult": {
                "intent": {
                    "displayName": "LogActivity",
                },
                "parameters": {
                    "activity": "curls",
                    "date": "today",
                    "reps": [3, 10],
                    "weight": [
                        {"amount": 12, "unit": "kg"},
                        {"amount": 10, "unit": "kg"},
                    ],
                    "duration": [],
                },
            },
        },
        "LogActivity_with_sets_and_new_attribute": {
            "queryResult": {
                "intent": {
                    "displayName": "LogActivity",
                },
                "parameters": {
                    "activity": "curls",
                    "date": "today",
                    "reps": [8.0, 8.0],
                    "weight": [
                        {"amount": 45.0, "unit": "kg"},
                        {"amount": 20.0, "unit": "kg"},
                    ],
                    "NEWATTRIBUTE": [2.0],
                    "duration": [],
                },
            },
        },
        "LogActivity_with_weight": {
            "queryResult": {
                "queryText": "yesterday",
                "parameters": {
                    "activity": "Hip Adductions",
                    "weight": [{"amount": 10, "unit": "kg"}],
                    "date": "2023-08-30T12:00:00+01:00",
                    "duration": [""],
                    "reps": ["1"],
                },
                "intent": {"displayName": "LogActivity"},
            }
        },
        "LogSymptom_1": {
            "queryResult": {
                "parameters": {
                    "severity": "2",
                    "symptom": "Left hip",
                    "date": "2023-08-31T12:00:00+01:00",
                },
                "intent": {
                    "displayName": "LogSymptom",
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
        "GetActivitySummary_1": {
            "queryResult": {
                "parameters": {"activity": "Yoga"},
                "intent": {
                    "name": "projects/hip-log-bot/agent/intents/0a2df690-4073-45f6-8a55-6111a98bda0d",  # noqa
                    "displayName": "GetActivitySummary",
                },
            }
        },
        "GetSymptomList_1": {
            "queryResult": {
                "parameters": {},
                "intent": {
                    "displayName": "GetSymptomList",
                },
            }
        },
        "GetActivityList_1": {
            "queryResult": {
                "parameters": {},
                "intent": {
                    "displayName": "GetActivityList",
                },
            }
        },
    }

    return x


# Tests for DailyLog class
def test_intent_init_for_activity_name_only(sample_requests):
    intent = Intent(sample_requests["LogActivity_1"])
    assert intent._type == "LogActivity"
    assert intent._raw_entity == {
        "date": "2023-07-24T12:00:00+01:00",
        "activity": "Yoga",
    }
    assert intent._log_input == {"name": "yoga", "sets": [{"reps": 1}]}
    assert intent._date == "2023-07-24"
    assert intent._user == "23970740102517391"


def test_intent_init_for_activity_with_sets(sample_requests):
    intent = Intent(sample_requests["LogActivity_with_sets"])
    assert intent._log_input == {
        "name": "curls",
        "sets": [
            {"reps": 3, "weight": {"amount": 12, "unit": "kg"}},
            {"reps": 10, "weight": {"amount": 10, "unit": "kg"}},
        ],
    }


def test_intent_init_for_activity_with_sets_and_new_attr(sample_requests):
    intent = Intent(sample_requests["LogActivity_with_sets_and_new_attribute"])
    assert len(intent._log_input["sets"]) > 0


def test_intent_init_for_activity_with_badsets(sample_requests):
    req = {
        "queryResult": {
            "intent": {
                "displayName": "LogActivity",
            },
            "parameters": {
                "activity": "curls",
                "date": "today",
                "reps": [3, 10, 12],
                "weight": [
                    {"amount": 12, "unit": "kg"},
                    {"amount": 10, "unit": "kg"},
                ],
                "duration": "",
            },
        },
    }

    with pytest.raises(ValueError, match="Mismatched number of reps/weights/durations"):
        Intent(req)


def test_intent_init_originalDetectIntentRequest_missing(caplog):
    caplog.set_level(logging.DEBUG, logger="models.intent")

    req = {
        "queryResult": {
            "parameters": {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"},
            "intent": {
                "displayName": "LogActivity",
            },
        },
    }

    intent = Intent(req)
    assert intent._user == "MarkTheTester"
    assert "originalDetectIntentRequest not found" in caplog.text  # noqa


def test_intent_init_user_info_missing():
    req = {
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
                    "senderNAME2": {"id": "23970740102517391"},
                }
            },
        },
    }

    with pytest.raises(
        ValueError,
        match="User info not found as expected in originalDetectIntentRequest from Dialogflow",  # noqa
    ):
        Intent(req)


def test_intent_init_with_weight(sample_requests):
    intent = Intent(sample_requests["LogActivity_with_weight"])
    assert intent.log_input == {
        "name": "hip adductions",
        "sets": [{"reps": 1, "weight": {"amount": 10, "unit": "kg"}, "duration": ""}],
    }


def test_intent_init_for_Symptom(sample_requests):
    intent = Intent(sample_requests["LogSymptom_1"])
    assert intent._date == "2023-08-31"
    assert intent._log_input == {"name": "left hip", "severity": 2}


def test_intent_init_for_get_daily_log(sample_requests):
    intent = Intent(sample_requests["GetDailyLog_1"])
    assert intent.type == "GetDailyLog"
    assert intent.date == "2023-09-05"


def test_intent_init_for_get_activity_summary(sample_requests):
    intent = Intent(sample_requests["GetActivitySummary_1"])
    assert intent.type == "GetActivitySummary"


def test_intent_init_for_get_symptom_list(sample_requests):
    intent = Intent(sample_requests["GetSymptomList_1"])
    assert intent.type == "GetSymptomList"


def test_intent_init_for_get_activity_list(sample_requests):
    intent = Intent(sample_requests["GetActivityList_1"])
    assert intent.type == "GetActivityList"


def test_intent_init_for_get_num_logs():
    req = {
        "queryResult": {
            "parameters": {"date": "2023-07-24T12:00:00+01:00", "activity": "Yoga"},
            "intent": {
                "displayName": "GetNumLogs",
            },
        }
    }

    intent = Intent(req)
    assert intent.type == "GetNumLogs" and not intent.log_input


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
    assert intent.log_input == {"name": "yoga", "sets": [{"reps": 1}]}
    assert intent.date == "2023-07-24"


def test_extract_date():
    assert Intent.extract_date("2023-07-24T12:00:00+01:00") == "2023-07-24"


def test_date_as_today():
    assert Intent.extract_date("today") == str(date.today())


# TODO: test that empty attributes are removed (tbd if this should live here or record)
def test_missing_attributes_skipped():
    pass


# TODO
def test_new_attributes_are_tbd():
    # What happens at the intent level if eg an activity has some new parameter we didn't expect (eg location=park) # noqa
    pass
