from dotenv import load_dotenv
import os
import pytest
import firebase_admin

# from firebase_admin import firestore

from services.db_logs import DBLogs


@pytest.fixture(scope="module")
def db():
    # load_dotenv("hip-log-bot-cloud-function/.env") # works with vs code GUI launches
    load_dotenv(".env")
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "blablabla"

    try:
        fb_app = firebase_admin.get_app()
    except ValueError:
        fb_app = firebase_admin.initialize_app()
    yield fb_app


def test_get_log(db):
    db_log = DBLogs()
    print(db_log.num_logs)


# In current state, .env isn't getting loaded when run from VS code visaul
def test_other():
    # os.chdir("hip-log-bot-cloud-function")
    # load_dotenv(".env")
    # print("hello")
    print(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])


# TODO: initialize a test db app

# TODO: test that num logs is updated after new entry

# TODO: test thta num logs is correct after updating entries

# TODO: test valid input date for get_log
