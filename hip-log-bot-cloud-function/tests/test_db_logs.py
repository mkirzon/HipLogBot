import os
import pytest
import firebase_admin

from firebase_admin import firestore
from services.db_logs import DBLogs
from models.daily_log import DailyLog
from models.record import Activity


@pytest.fixture(scope="module")
def db():
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
    for doc in docs:
        print(f"Deleting doc {doc.id} => {doc.to_dict()}")
        doc.reference.delete()

    # Close fireabse
    try:
        firebase_admin.delete_app(fb_app)
    except ValueError:
        pass


# A "meta" test to make sure the other tests here will work. I haven't figured out how to apply load_dotenv() yet to
# pytests (due to working directory funkyness). So instead we're using pytest-env. This is also good since it will
# help split out testing environment
def test_pytest_ini_loads():
    assert os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


def test_get_log(db):
    db_log = DBLogs()
    assert isinstance(db_log.num_logs, int)


def test_new_log_updates_num(db):
    db_log = DBLogs()
    n1 = db_log.num_logs
    db_log.upload_log(
        DailyLog(date="2024-01-01", activites={"Yoga": Activity(name="Yoga")})
    )
    n2 = db_log.num_logs
    assert n2 == n1 + 1


def test_existing_log_keeps_num(db):
    db_log = DBLogs()

    db_log.upload_log(
        DailyLog(date="2024-01-01", activites={"Yoga": Activity(name="Yoga")})
    )
    n1 = db_log.num_logs

    db_log.upload_log(
        DailyLog(date="2024-01-01", activites={"Handstand": Activity(name="Yoga")})
    )
    n2 = db_log.num_logs

    assert n2 == n1


# TODO: test valid input date for get_log
def test_get_log_needs_valid_date(db):
    db_log = DBLogs()
    with pytest.raises(ValueError, match="Invalid date provided"):
        db_log.get_log("2023-11111-1")
