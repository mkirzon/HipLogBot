import logging
import traceback
import firebase_admin
import functions_framework
from models.record import Activity
from services.hiplogdb import HipLogDB
from models.intent import Intent
from dotenv import load_dotenv
from utils import get_runtime_config

logging.basicConfig(level=get_runtime_config()["log_level"])
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
        hiplogdb = HipLogDB()

        # Parse the intent
        intent = Intent(req)
        logger.info(f"Parsed intent request: {intent}")

        # First handle generic requests, that don't require specific log queries.
        # Otherwise do log-based actions
        if intent.type == "GetNumLogs":
            num_logs = hiplogdb.num_logs
            res = f"There are {num_logs} logs"

        elif intent.type == "GetDailyLog":
            log = hiplogdb.get_log(intent.user, intent.date)
            logger.info(f"Retrieved DailyLog (local object) generated:\n{log}")

        elif intent.type == "LogActivity":
            log = hiplogdb.get_log(intent.user, intent.date, initialize_empty=True)
            for s in intent.log_input["sets"]:
                log.add_activity(
                    Activity(intent.log_input["name"], intent.log_input["sets"])
                )
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif intent.type == "LogPain":
            log = hiplogdb.get_log(intent.user, intent.date)
            log.add_pain(**intent.log_input)
            logger.info(f"DailyLog (local object) generated:\n{log}")

        elif intent.type == "DeleteDailyLog":
            hiplogdb.delete_log(intent.user, intent.date)
            res = f"Your entry '{intent.date}' was deleted"

        elif intent.type == "GetActivitySummary":
            activity_name = intent.log_input["name"]
            stats = hiplogdb.get_activity_summary(activity_name)
            output = [f"**Summary Stats for '{activity_name}'**\n"]
            output += [f"{k}: {v}" for k, v in stats.items()]
            res = "\n".join(output)

        if intent.type in ["LogActivity", "LogPain", "GetDailyLog"]:
            # TODO add logic to bubble up new vs update status

            # TODO: retrieve into here too but tbd how cuz also need to handle
            # differently

            # Upload the new/modified log back
            logger.info("Uploading DailyLog")
            hiplogdb.upload_log(intent.user, log)
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
