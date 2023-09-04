import os
import traceback
import logging
import firebase_admin

from dotenv import load_dotenv
from flask import Flask, request
from flask_ngrok import run_with_ngrok


from src.services.db_logs import DBLogs
from src.services.intent_handler import Intent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
run_with_ngrok(app)  # Initialize ngrok when the app is run

load_dotenv()


@app.route("/")
def hello():
    return "Hello"


@app.route("/webhook", methods=["POST"])
def webhook():
    # Get dialog flow request
    req = request.get_json(force=True)

    # Initialize the firebase components
    firebase_cred = firebase_admin.credentials.Certificate(
        os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    )
    try:
        fb_app = firebase_admin.get_app(firebase_cred)
        logger.info("Opened existing Firestore app")
    except ValueError:
        fb_app = firebase_admin.initialize_app(firebase_cred)
        logger.info("Opened new Firestore app")

    try:
        # Initialize handlers
        db_logs = DBLogs()
        intent = Intent(req)
        logger.info(
            "The intent request parsed into the following `log_input`:\n{intent}"
        )

        # First handle generic requests, that don't require specific log queries.
        # Otherwise do log-based actions
        if intent.type == "GetNumLogs":
            logger.trace("IntentType if-case: GetNumLogs")
            num_logs = db_logs.num_logs
            res = f"There are {num_logs} logs"

        else:
            logger.trace("IntentType if-case: log-based")
            # Get the corresponding log for requested date
            log = db_logs.get_log(intent.date)

            if intent.type == "LogActivity":
                logger.trace("IntentType if-case: LogActivity")
                log.add_activity(**intent.log_input)

            elif intent.type == "LogPain":
                logger.trace("IntentType if-case: LogPain")
                log.add_pain(**intent.log_input)

            res = log.__str__()

            # Upload the new/modified log back
            logger.info("Uploading new/modified log")
            db_logs.upload_log(log)
            logger.info("Upload complete of this log:\n{log}")

    finally:
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

    return response


if __name__ == "__main__":
    # app.run()
    app.run(port=443, host="0.0.0.0", ssl_context="adhoc")
