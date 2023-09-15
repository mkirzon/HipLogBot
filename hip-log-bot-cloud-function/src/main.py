import logging
import traceback
import firebase_admin
import functions_framework
from services.hiplogdb import HipLogDB
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
        db_logs = HipLogDB()

        # Parse the intent
        intent = Intent(req)
        logger.info(f"Parsed intent request: {intent}")

        # First handle generic requests, that don't require specific log queries.
        # Otherwise do log-based actions
        if intent.type == "GetNumLogs":
            num_logs = db_logs.num_logs
            res = f"There are {num_logs} logs"

        elif intent.type == "GetDailyLog":
            log = db_logs.get_daily_log(intent.date)
            logger.info(f"Retrieved DailyLog (local object) generated:\n{log}")

        elif intent.type == "LogActivity":
            log = db_logs.get_daily_log(intent.date)
            log.add_activity(**intent.log_input)
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif intent.type == "LogPain":
            log = db_logs.get_daily_log(intent.date)
            log.add_pain(**intent.log_input)
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif intent.type == "DeleteDailyLog":
            db_logs.delete_log(intent.date)
            res = f"Your entry '{intent.date}' was deleted"

        elif intent.type == "GetActivitySummary":
            activity_name = intent.log_input["name"]
            stats = db_logs.get_activity_summary(activity_name)
            output = [f"**Summary Stats for '{activity_name}'**\n"]
            output += [f"{k}: {v}" for k, v in stats.items()]
            res = "\n".join(output)

        if intent.type in ["LogActivity", "LogPain", "GetDailyLog"]:
            # TODO add logic to bubble up new vs update status

            # TODO: retrieve into here too but tbd how cuz also need to handle
            # differently

            # Upload the new/modified log back
            logger.info("Uploading DailyLog")
            db_logs.upload_log(log)
            logger.info("Completed upload")

            res = log.__str__()

    except ValueError as e:  # noqa
        # Graceful message back if supported case
        # TODO: change
        if "Unsupported intent" in str(e):
            res = f"The processing server doesn't support this yet (intent = {req['queryResult']['intent']['displayName']}))"  # noqa

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
