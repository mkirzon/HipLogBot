import os
import pytest
import firebase_admin

from firebase_admin import firestore
from services.hiplogdb import HipLogDB
from models.daily_log import DailyLog
from models.record import Activity
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
    db = firestore.client()
    collection_ref = db.collection(os.environ["FIRESTORE_COLLECTION_NAME"])
    docs = collection_ref.stream()
    # for doc in docs:
    #     print(f"Deleting doc {doc.id} => {doc.to_dict()}")
    #     doc.reference.delete()

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
    x = db.get_log("mark", "2023-09-15")
    assert isinstance(x, DailyLog) and x.date == "2023-09-15"


def test_upload_log(conn, db):
    user = "mark"
    date = "2024-01-01"
    db.delete_log(user, date)
    n1 = db._get_num_logs_by_user(user)
    db.upload_log(user, DailyLog(date=date, activities=[Activity(name="Yoga")]))
    n2 = db._get_num_logs_by_user(user)
    assert n2 == n1 + 1


def test_existing_log_keeps_num(conn, db):
    user = "mark"
    db.upload_log(user, DailyLog(date="2024-01-01", activities=[Activity(name="Yoga")]))
    n1 = db._get_num_logs_by_user("mark")

    db.upload_log(user, DailyLog(date="2024-01-01", activities=[Activity(name="Yoga")]))
    n2 = db._get_num_logs_by_user("mark")

    assert n2 == n1


def test_get_log_needs_valid_date(conn, db):
    with pytest.raises(ValueError, match="Invalid date provided"):
        db.get_log("mark", "2023-11111-1")


def test_delete_log(conn, db):
    # Create a log
    date = "2024-01-01"
    user = "mark"
    db.upload_log(user, DailyLog(date=date, activities=[Activity(name="Yoga")]))
    status1 = db._get_user_log_ref(user, date).get().exists

    # Delete it
    db.delete_log(user, date)

    # Test that it doesn't exist
    status2 = db._collection.document(date).get().exists
    assert status1 != status2


# def test_get_activity_summary(conn):
def test_get_activity_summary(conn, caplog, db):
    # For reference how to change logging (must use Run mode, not debug mode):
    # caplog.set_level(logging.DEBUG, logger="services.hiplogdb")

    name = "Tennis"
    user = "mark"
    for d in ["2023-01-01", "2023-01-02", "2023-01-03"]:
        db.upload_log(user, DailyLog(date=d, activities=[Activity(name)]))

    x = db.get_activity_summary(user, name)
    assert x["total_count"] == 3
