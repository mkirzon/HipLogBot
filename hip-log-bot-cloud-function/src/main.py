import logging
import traceback
import firebase_admin
import functions_framework
from services.db_logs import DBLogs
from models.intent import Intent
from dotenv import load_dotenv


logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get env variables for auth
if not load_dotenv():
    logger.info(".env file not found")


@functions_framework.http
def main(request):
    logger.debug("Starting main()")
    req = request.get_json(force=True)

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

        # Parse the intent
        intent = Intent(req)
        logger.info(f"The intent request was parsed: {intent}")

        # First handle generic requests, that don't require specific log queries.
        # Otherwise do log-based actions
        if intent.type == "GetNumLogs":
            logger.debug("Executing main logic for intent: GetNumLogs")
            num_logs = db_logs.num_logs
            res = f"There are {num_logs} logs"

        elif intent.type == "GetDailyLog":
            logger.debug("IntentType: GetDailyLog")
            log = db_logs.get_log(intent.date)

        elif intent.type == "LogActivity":
            logger.debug("Executing main logic for intent: LogActivity")
            log = db_logs.get_log(intent.date)
            log.add_activity(**intent.log_input)
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif intent.type == "LogPain":
            logger.debug("Executing main logic for intent: LogPain")
            log = db_logs.get_log(intent.date)
            log.add_pain(**intent.log_input)
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif intent.type == "DeleteDailyLog":
            logger.debug("Executing main logic for intent: DeleteDailyLog")
            db_logs.delete_log(intent.date)

        if intent.type in ["LogActivity", "LogPain", "GetDailyLog"]:
            # TODO add logic to bubble up new vs update status

            # Upload the new/modified log back
            logger.info("Uploading new/modified log")
            db_logs.upload_log(log)
            logger.info("Upload complete of this log")

            res = log.__str__()

    except ValueError as e:  # noqa
        # Graceful message back if supported case
        if "Unsupported intent passed" in str(e):
            res = f"The processing server doesn't support this yet (intent = {req['queryResult']['intent']['displayName']}))"

        else:
            # TODO: standardize this block cuz it's used twice
            logger.error(f"Failed logging, here's the input request:\n{req}\n")
            traceback.print_exc()
            res = "FAILED"

    except Exception:
        logger.error(f"Failed logging, here's the input request:\n{req}\n")
        traceback.print_exc()
        res = "FAILED"

    # Close fireabse
    try:
        firebase_admin.delete_app(fb_app)
        logger.debug("Closed Firestore app")
    except ValueError:
        logger.warning("Failed to close Firestore app")
        pass

    # Send response back to DialogFlow
    response = {"fulfillmentText": res}

    return response
