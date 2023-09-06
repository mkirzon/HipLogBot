import logging

from services.db_logs import DBLogs
from dotenv import load_dotenv
import firebase_admin

logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if not load_dotenv():
    logger.info(".env file not found")

# Initialize the firebase components
try:
    fb_app = firebase_admin.get_app()
    logger.info("Opened existing Firestore app")
except ValueError:
    fb_app = firebase_admin.initialize_app()
    logger.info("Opened new Firestore app")
db_logs = DBLogs()

db_logs.get_log("2023-09-01")
