import sys
from dotenv import load_dotenv

sys.path.append(
    "/Users/mkirzon/Documents/2023/230901 - Hip Log Bot/hip-log-bot-cloud-function/src"
)

import os
import utils
import pytest
from firebase_admin import firestore


@pytest.fixture()
def reset_testuser():
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

    # TODO: reset any other attributes beyond DailyLogs
