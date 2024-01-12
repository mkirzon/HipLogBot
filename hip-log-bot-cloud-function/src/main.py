import logging
import firebase_admin
import functions_framework
from services.executor import Executor
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

    # Initialize the firebase components
    try:
        fb_app = firebase_admin.get_app()
        logger.info("Opened existing Firestore app")
    except ValueError:
        fb_app = firebase_admin.initialize_app()
        logger.info("Opened new Firestore app")

    # Initialize handlers
    request = request.get_json(force=True)
    logger.debug(f"Input request:\n{request}")

    try:
        res = Executor(request).run()
    except:  # noqa
        res = "Something went wrong. Reach out to the developer"

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
