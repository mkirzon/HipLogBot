import os
import pytest
import firebase_admin

from firebase_admin import firestore
from services.hiplogdb import HipLogDB
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


@pytest.fixture
def sample_db():
    return HipLogDB()


# A "meta" test to make sure the other tests here will work. I haven't figured out how
# to apply load_dotenv() yet to pytests (due to working directory funkyness). So
# instead we're using pytest-env. This is also good since it will help split out
# testing environment
def test_pytest_ini_loads():
    assert os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


def test_initialize_hiplogdb(db):
    hiplogdb = HipLogDB()
    assert isinstance(hiplogdb.num_logs, int)


def test_get_daily_log(db, sample_db):
    x = sample_db.get_daily_log("mark", "2023-09-15")
    assert isinstance(x, DailyLog)


def test_new_log_updates_num(db):
    hiplogdb = HipLogDB()
    n1 = hiplogdb.num_logs
    hiplogdb.upload_log(
        DailyLog(date="2024-01-01", activities={"Yoga": Activity(name="Yoga")})
    )
    n2 = hiplogdb.num_logs
    assert n2 == n1 + 1


def test_existing_log_keeps_num(db):
    hiplogdb = HipLogDB()

    hiplogdb.upload_log(
        DailyLog(date="2024-01-01", activities={"Yoga": Activity(name="Yoga")})
    )
    n1 = hiplogdb.num_logs

    hiplogdb.upload_log(
        DailyLog(date="2024-01-01", activities={"Handstand": Activity(name="Yoga")})
    )
    n2 = hiplogdb.num_logs

    assert n2 == n1


def test_get_log_needs_valid_date(db):
    hiplogdb = HipLogDB()
    with pytest.raises(ValueError, match="Invalid date provided"):
        hiplogdb.get_daily_log("2023-11111-1")


def test_delete_log(db):
    # Create a log
    date = "2024-01-01"
    hiplogdb = HipLogDB()
    hiplogdb.upload_log(DailyLog(date=date, activities={"Yoga": Activity(name="Yoga")}))
    status1 = hiplogdb._collection.document(date).get().exists

    # Delete it
    hiplogdb.delete_log(date)

    # Test that it doesn't exist
    status2 = hiplogdb._collection.document(date).get().exists
    assert status1 != status2


# def test_get_activity_summary(db):
def test_get_activity_summary(db, caplog):
    # For reference how to change logging (must use Run mode, not debug mode):
    # caplog.set_level(logging.DEBUG, logger="services.hiplogdb")

    hiplogdb = HipLogDB()
    name = "Tennis"
    for d in ["2023-01-01", "2023-01-02", "2023-01-03"]:
        hiplogdb.upload_log(DailyLog(date=d, activities={name: Activity(name=name)}))

    x = hiplogdb.get_activity_summary(name)
    assert x["total_count"] == 3
