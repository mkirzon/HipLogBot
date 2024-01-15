import logging
import pytest
import os
import re
import firebase_admin
import utils
from firebase_admin import firestore
from services.executor import Executor


@pytest.fixture(scope="module")
def conn():
    # Open firebase
    try:
        fb_app = firebase_admin.get_app()
    except ValueError:
        fb_app = firebase_admin.initialize_app()

    # Keep open until end of tests
    yield fb_app

    # Delete all docs in the test collection
    print("Starting Cleanup")
    db = firestore.client()
    collection_ref = (
        db.collection(os.environ["FIRESTORE_COLLECTION_NAME"])
        .document(utils.test_username)
        .collection("DailyLogs")
    )
    docs = collection_ref.stream()
    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.to_dict()}")
        doc.reference.delete()

    # Close fireabse
    try:
        firebase_admin.delete_app(fb_app)
    except ValueError:
        pass


# def test_executor_get_log_doesnt_upload(conn, db, caplog):
#     req = {
#         "queryResult": {
#             "queryText": "What have I done today?",
#             "parameters": {"date": "2023-09-05T12:00:00+01:00"},
#             "intent": {
#                 "displayName": "GetDailyLog",
#             },
#         }
#     }

#     caplog.set_level(logging.DEBUG, logger="services.executor")

#     intent = Intent(req)
#     executor = Executor(intent, db)
#     executor.run()

#     assert "Uploading" not in caplog.text


def test_executor_get_log(conn):
    request = {
        "queryResult": {
            "queryText": "What have I done today?",
            "parameters": {"date": "today"},
            "intent": {
                "displayName": "GetDailyLog",
            },
        }
    }

    executor = Executor(request)
    res = executor.run()
    assert re.search("Log", res)


def test_two_uploads(conn):
    request = {
        "queryResult": {
            "parameters": {
                "activity": "Handstands",
                "duration": [],
                "reps": [3],
                "date": "2023-11-03T12:00:00+01:00",
                "weight": [],
            },
            "intent": {
                "displayName": "LogActivity",
                "id": "3f813326-a34e-4845-875d-5803cf3c3cc2",
            },
        }
    }

    # NOTE: don't forget to delete in the db directly if running adhoc .

    # First run
    executor = Executor(request)
    executor.run()

    # Tweak the request and rerun
    request["queryResult"]["parameters"]["reps"][0] = 5
    executor = Executor(request)
    r2 = executor.run()

    assert (
        r2
        == """Nov. 3, 2023 Log:

1x activities:
* Handstands 2 sets: 3x, 5x

0x symptom records:"""
    )


def test_get_commands(conn):
    request = {
        "queryResult": {
            "parameters": {},
            "intent": {
                "displayName": "GetCommandList",
            },
        }
    }

    executor = Executor(request)
    res = executor.run()
    assert re.search(".*Log an activity.*", res)


def test_get_num_logs(conn):
    request = {
        "queryResult": {
            "parameters": {},
            "intent": {
                "displayName": "GetNumLogs",
            },
        }
    }

    executor = Executor(request)
    res = executor.run()
    assert re.search("There are \\d+ logs", res)


def test_multiple_multisets(conn):
    request = {
        "queryResult": {
            "parameters": {
                "activity": "Pullups",
                "duration": [],
                "reps": [1, 2, 3],
                "date": "2023-11-01T12:00:00+01:00",
                "weight": [],
            },
            "intent": {
                "displayName": "LogActivity",
            },
        }
    }

    # NOTE: don't forget to delete in the db directly if running adhoc .

    # First run
    executor = Executor(request)
    executor.run()

    # Tweak the request and rerun
    request["queryResult"]["parameters"]["reps"] = [4, 5, 6]
    executor = Executor(request)
    r2 = executor.run()

    assert (
        r2
        == """Nov. 1, 2023 Log:

1x activities:
* Pullups 6 sets: 1x, 2x, 3x, 4x, 5x, 6x

0x symptom records:"""
    )


def test_simple_symptom_log(conn):
    request = {
        "queryResult": {
            "parameters": {
                "symptom": "left ankle",
                "severity": "1",
                "date": "2023-11-06T12:00:00Z",
            },
            "intent": {"displayName": "LogSymptom"},
        }
    }

    executor = Executor(request)
    res = executor.run()

    assert re.search("1x symptom records", res)


def test_get_activity_summary(conn):
    request = {
        "queryResult": {
            "parameters": {"activity": "Yoga"},
            "intent": {
                "displayName": "GetActivitySummary",
            },
        }
    }

    executor = Executor(request)
    res = executor.run()

    assert "Summary Stats" in res


def test_catch_mismatch_error_on_run(conn, caplog):
    request = {
        "queryResult": {
            "intent": {
                "displayName": "LogActivity",
            },
            "parameters": {
                "duration": [],
                "reps": ["1"],
                "weight": [
                    {"amount": "45.0", "unit": "kg"},
                    {"amount": "20.0", "unit": "kg"},
                ],
                "activity": "Hip Adductions",
                "date": "2024-01-10T12:00:00+01:00",
            },
        }
    }

    caplog.set_level(logging.DEBUG, logger="services.executor")

    res = Executor(request).run()
    # Test that it's both in logs and the response
    assert "Mismatched number of reps/weights/durations" in caplog.text
    assert "Setting response" in caplog.text
    assert re.search("It looks like you provided", res)
