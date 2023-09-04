# This is for testing what i'm doing in cloud function

import os
import logging
import traceback
import firebase_admin
from dotenv import load_dotenv
import sys

load_dotenv()


from services.db_logs import DBLogs
from services.intent_handler import Intent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Currently this is what i have to do different in cloud functions since for some
# reason this isn't detected automatically from the service account(but I'm not
# convinced it's using the service accoutn )
os.environ["GOOGLE_CLOUD_PROJECT"] = "hip-log-bot"


req = {
    "queryResult": {
        "queryText": "i did yoga yesterday for 10 minutes",
        "parameters": {
            "activity": "Yoga",
            "date": "2023-09-03T12:00:00+01:00",
            "duration": {"amount": 10, "unit": "min"},
            "reps": "",
            "weight": "",
        },
        "intent": {
            "name": "projects/hip-log-bot/agent/intents/3f813326-a34e-4845-875d-5803cf3c3cc2",
            "displayName": "LogActivity",
        },
    },
    "originalDetectIntentRequest": {"source": "DIALOGFLOW_CONSOLE", "payload": {}},
    "session": "projects/hip-log-bot/agent/sessions/a6480f9a-41d7-18e7-6f0d-c3ee14c98cfe",
}

# Initialize the firebase components
try:
    fb_app = firebase_admin.get_app()
    logger.info("Opened existing Firestore app")
except ValueError:
    fb_app = firebase_admin.initialize_app()
    logger.info("Opened new Firestore app")

try:
    # Initialize handlers
    db_logs = DBLogs()
    intent = Intent(req)
    logger.info("The intent request parsed into the following `log_input`:\n{intent}")

    # First handle generic requests, that don't require specific log queries.
    # Otherwise do log-based actions
    if intent.type == "GetNumLogs":
        logger.debug("IntentType if-case: GetNumLogs")
        num_logs = db_logs.num_logs
        res = f"There are {num_logs} logs"

    else:
        logger.debug("IntentType if-case: log-based")
        # Get the corresponding log for requested date
        log = db_logs.get_log(intent.date)

        if intent.type == "LogActivity":
            logger.debug("IntentType if-case: LogActivity")
            log.add_activity(**intent.log_input)

        elif intent.type == "LogPain":
            logger.debug("IntentType if-case: LogPain")
            log.add_pain(**intent.log_input)

        logger.info(f"Log item created:\n{log}")
        res = log.__str__()

        # Upload the new/modified log back
        logger.info("Uploading new/modified log")
        db_logs.upload_log(log)
        logger.info("Upload complete of this log")

except:  # noqa
    logger.error(f"Failed logging, here's the input request:\n{req}\n")
    traceback.print_exc()
    res = "FAILED"

# Close fireabse
try:
    firebase_admin.delete_app(fb_app)
    logger.info("Closed Firestore app")
except ValueError:
    logger.warning("Failed to close Firestore app")
    pass

# Send response back to DialogFlow
response = {"fulfillmentText": res}

print(response)
