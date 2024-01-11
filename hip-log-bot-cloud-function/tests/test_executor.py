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

0x pain records:"""
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

0x pain records:"""
    )


def test_simple_pain_log(conn):
    request = {
        "queryResult": {
            "parameters": {
                "body_part": "Left hip",
                "pain_level": "1",
                "date": "2023-11-06T12:00:00Z",
            },
            "intent": {"displayName": "LogPain"},
        }
    }

    executor = Executor(request)
    res = executor.run()

    assert (
        res
        == """Nov. 6, 2023 Log:

0x activities:

1x pain records:
* Left Hip: 1"""
    )


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


def test_error_on_executor_init(conn):
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
                "number": [],
            },
        }
    }

    res = Executor(request).run()
    assert res == "FAILED"
