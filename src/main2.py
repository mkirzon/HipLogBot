import os
import logging
import firebase_admin

from services.db_logs import DBLogs

logging.basicConfig(level=logging.INFO)


# Initialize the firebase components
os.environ[
    "FIRESTORE_KEY_PROD"
] = "/Users/mkirzon/Downloads/Project Auths/hip-log-bot-firebase-prod.json"

firebase_cred = firebase_admin.credentials.Certificate(
    os.environ.get("FIRESTORE_KEY_PROD")
)

try:
    fb_app = firebase_admin.get_app(firebase_cred)
except ValueError:
    fb_app = firebase_admin.initialize_app(firebase_cred)

db_logs = DBLogs()
print(db_logs.num_logs)


try:
    firebase_admin.delete_app(fb_app)
except ValueError:
    pass
