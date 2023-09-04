import os
import logging
import firebase_admin
from firebase_admin import firestore
import functions_framework


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["GOOGLE_CLOUD_PROJECT"] = "hip-log-bot"


@functions_framework.http
def hello_http(request):
    # Get dialog flow request
    req = request.get_json(force=True)

    try:
        fb_app = firebase_admin.get_app()
        logger.info("Opened existing Firestore app")
    except ValueError:
        fb_app = firebase_admin.initialize_app()
        logger.info("Opened new Firestore app")

    # Initialize handlers

    db = firestore.client()
    collection_ref = db.collection("activityLogs")
    documents = collection_ref.stream()
    doc_count = sum(1 for _ in documents)
    res = f"Num docs = {doc_count}"

    # Send response back to DialogFlow
    response = {"fulfillmentText": res}

    return response
