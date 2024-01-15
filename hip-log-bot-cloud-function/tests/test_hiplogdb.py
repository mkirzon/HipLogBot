import os
import pytest
import firebase_admin
import utils
from firebase_admin import firestore
from services.hiplogdb import HipLogDB
from models.daily_log import DailyLog
from models.record import Activity, Symptom
from google.cloud.firestore_v1.collection import CollectionReference


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


@pytest.fixture
def db():
    return HipLogDB()


# A "meta" test to make sure the other tests here will work. I haven't figured out how
# to apply load_dotenv() yet to pytests (due to working directory funkyness). So
# instead we're using pytest-env. This is also good since it will help split out
# testing environment
def test_pytest_ini_loads():
    assert os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


def test_initialize_hiplogdb(conn):
    hiplogdb = HipLogDB()
    assert isinstance(hiplogdb._collection, CollectionReference)


def test_get_log(conn, db):
    # First initialize
    date = "1999-1-1"
    db._collection.document(utils.test_username).collection("DailyLogs").document(
        date
    ).set({"activities": {"Yoga": {"sets": [{"reps": 1}]}}})
    x = db.get_log(utils.test_username, date)
    assert isinstance(x, DailyLog) and x.date == date


def test_upload_log(conn, db):
    date = "2024-01-01"
    db.delete_log(utils.test_username, date)
    n1 = db.get_num_logs_by_user(utils.test_username)
    db.upload_log(
        utils.test_username, DailyLog(date=date, activities=[Activity(name="Yoga")])
    )
    n2 = db.get_num_logs_by_user(utils.test_username)
    assert n2 == n1 + 1


def test_get_num_logs_by_user(conn, db):
    # This test doesn't actually test accuracy but tests functionality. The test is
    # hard to run b/c other tests affect this count, so we'll use the implicit tests
    # for accuracy in the other test
    assert isinstance(db.get_num_logs_by_user(utils.test_username), int)


def test_existing_log_keeps_num(conn, db):
    db.upload_log(
        utils.test_username,
        DailyLog(date="2024-01-01", activities=[Activity(name="Yoga")]),
    )
    n1 = db.get_num_logs_by_user(utils.test_username)

    db.upload_log(
        utils.test_username,
        DailyLog(date="2024-01-01", activities=[Activity(name="Yoga")]),
    )
    n2 = db.get_num_logs_by_user(utils.test_username)

    assert n2 == n1


def test_get_log_needs_valid_date(conn, db):
    with pytest.raises(ValueError, match="Invalid date provided"):
        db.get_log(utils.test_username, "2023-11111-1")


def test_delete_log(conn, db):
    # Create a log
    date = "2024-01-01"
    user = utils.test_username
    db.upload_log(user, DailyLog(date=date, activities=[Activity(name="Yoga")]))
    status1 = db._get_user_log_ref(user, date).get().exists

    # Delete it
    db.delete_log(user, date)

    # Test that it doesn't exist
    status2 = db._collection.document(date).get().exists
    assert status1 != status2


@pytest.mark.skip(reason="TODO")
def test_delete_log_nonexistent(conn, db):
    pass


def test_get_activity_summary(conn, caplog, db):
    # For reference how to change logging (must use Run mode, not debug mode):
    # caplog.set_level(logging.DEBUG, logger="services.hiplogdb")

    name = "Tennis"
    user = utils.test_username
    for d in ["2023-01-01", "2023-01-02", "2023-01-03"]:
        db.upload_log(user, DailyLog(date=d, activities=[Activity(name)]))

    x = db.get_activity_summary(user, name)
    assert x["total_count"] == 3


def test_get_activity_list_by_user(conn, reset_testuser, db):
    # Initialize a few, in reverse chrono order to test for sorting
    log_data = [
        ("2023-01-01", "Tennis"),
        ("2023-01-02", "Yoga"),
        ("2023-01-06", "C"),
    ]

    for date, activity_name in log_data:
        db.upload_log(
            utils.test_username,
            DailyLog(date=date, activities=[Activity(activity_name)]),
        )

    assert set(db.get_activity_list_by_user(utils.test_username)) == {
        "C",
        "Tennis",
        "Yoga",
    }


def test_get_symptom_list_by_user(conn, reset_testuser, db):
    # Initialize a few

    # Case 1: activity+symptom
    db.upload_log(
        utils.test_username,
        DailyLog(
            date="2023-01-01",
            symptoms=[Symptom("headache", 1)],
            activities=[Activity("Yoga")],
        ),
    )
    # Case 2: symptom only
    db.upload_log(
        utils.test_username, DailyLog(date="2023-01-02", symptoms=[Symptom("groin", 2)])
    )
    # Case 3: activity only
    db.upload_log(
        utils.test_username, DailyLog(date="2023-01-03", activities=[Activity("Yoga")])
    )

    assert set(db.get_symptom_list_by_user(utils.test_username)) == {
        "headache",
        "groin",
    }


@pytest.mark.skip(reason="TODO")
def test_get_symptom_list_by_user_missing_symptom(conn, reset_testuser, db):
    # Upload an item directly that is missing 'symptoms' among its attributes.
    pass
