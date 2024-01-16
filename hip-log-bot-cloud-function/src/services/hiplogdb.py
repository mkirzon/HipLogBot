import logging
import os
from typing import List
from firebase_admin import firestore
from models.daily_log import DailyLog
from utils import is_valid_date_format
from google.cloud.firestore_v1 import aggregation

logger = logging.getLogger(__name__)
# print(__name__)


class HipLogDB:
    """A handler class for interacting with the Firestore Database for the Hip Log Bots

    The database is a schema-less document store, where the collection will contain a
    set of documents. Each document is a daily record (eg key = "2023-03-04")

    Attributes:
        num_logs (int): number of daily logs for current user in the database (assuming
        a single user)
        collection_name (str): the selected collection name we'll be writing to

    """

    # Initialization
    def __init__(self):
        """Initialize a handler for my Firestore database.

        The "database" instance (eg prod vs test) is by the `FIRESTORE_COLLECTION_NAME`
        env var. This assumes you have the firebase app already started outside of this
        context with `firebase_admin.initialize_app()`.
        """
        self._db = firestore.client()
        logger.debug(
            f"Initializing HipLogDB() instance with collection '{os.environ['FIRESTORE_COLLECTION_NAME']}'"  # noqa
        )
        self._collection_name = os.environ["FIRESTORE_COLLECTION_NAME"]
        self._collection = self._db.collection(self._collection_name)

    # Public Methods
    def get_log(self, user: str, date: str, initialize_empty=False) -> DailyLog:
        """Download a user's daily log document

        Query firestore collection by user-date and return it as a DailyLog object.
        If date doesn't exist, it can initialize a DailyLog

        Args:
            user (str): 'user id' document name in 'users' collection
            date (str): 'date' document name in dailyLogs
            initialize_empty: if True, will return a new DailyLog instance for date

        Returns:
            DailyLog/None: a DailyLog object or None if record not found
        """
        logger.info(f"Starting DailyLog fetch from database for '{date}'")
        # Input checking
        if not is_valid_date_format(date):
            raise ValueError("Invalid date provided. Must be a 'YYYY-MM-DD' string")

        # Download doc as json
        fetched_doc = self._get_user_log_ref(user, date).get()

        if fetched_doc.exists:
            fetched_dict = fetched_doc.to_dict()
            logger.info(f"Retrieved log as dict:\n{fetched_dict}")  # noqa

            # Map the Firestore dict to the DailyLog object
            log = DailyLog.from_dict(date, fetched_dict)
            logger.debug("Converted log dict to DailyLog")

        else:
            logger.info(f"Didn't find log for '{date}'")
            if initialize_empty:
                logger.info(f"Initializing empty DailyLog for '{date}'")
                log = DailyLog(date)
            else:
                logger.info("Returning empty (None)")
                log = None

        return log

    def upload_log(self, user: str, log: DailyLog):
        log_dict = log.to_dict()

        logger.info(f"Uploading '{log.date}' log; dict:\n{log_dict}")
        self._get_user_log_ref(user, log.date).set(log_dict)

        # In case this was a new one, update the count
        # TODO: optimization - run this only if log was new
        # self._num_logs = self.get_num_logs_by_user(user)

    def delete_log(self, user: str, date: str) -> None:
        try:
            self._get_user_log_ref(user, date).delete()
            logger.info(f"Document with ID {date} deleted successfully!")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def get_activity_summary(self, user: str, activity_name: str) -> dict:
        """Get summary statistics for an activity

        Fetch stats with a collection query and format them into a nice summary

        Returns: a dict of stats
        """

        stats = {}

        # Stat 1: total num
        # TODO need to filter on the contents of the keys of the activities
        query = self._get_user_dailylogs_ref(user).order_by(
            f"activities.{activity_name}"
        )
        aggregate_query = aggregation.AggregationQuery(query)
        aggregate_query.count(alias="all")
        results = aggregate_query.get()
        logger.debug(f"Returned result: {results}")
        stats["total_count"] = results[0][0].value

        return stats

    def get_activity_list_by_user(self, user: str) -> List[str]:
        """Get a list of activities for a user

        TODO:
            * This is highly inefficient and requires downloading each document for a
            user and should instead be handled with a user attribute that's maintained
            on each upload
        """
        # Get all the daily logs for the user
        daily_logs_ref = self._get_user_dailylogs_ref(user).stream()

        # Set to store unique activities
        unique_activities_set = set()

        # Iterate over daily logs and extract activities
        for daily_log in daily_logs_ref:
            daily_log_dict = daily_log.get("")
            logger.debug(f"Reading doc: {daily_log_dict}")
            activities_map = daily_log_dict.get("activities", {})

            # Add activities to the set
            unique_activities_set.update(activities_map.keys())

        res = list(unique_activities_set)
        res.sort()
        return res

    def get_symptom_list_by_user(self, user: str) -> List[str]:
        """Get a list of symptoms for a user

        TODO:
            * This is highly inefficient and requires downloading each document for a
            user and should instead be handled with a user attribute that's maintained
            on each upload
        """
        # Get all the daily logs for the user
        daily_logs_ref = self._get_user_dailylogs_ref(user).stream()

        # Set to store unique symptoms
        unique_symptoms_set = set()

        # Iterate over daily logs and extract symptoms
        for daily_log in daily_logs_ref:
            daily_log_dict = daily_log.get("")
            logger.debug(f"Reading symptoms from doc: {daily_log_dict}")
            symptoms_map = daily_log_dict.get("symptoms", {})

            # Add symptoms to the set
            unique_symptoms_set.update(symptoms_map.keys())

        res = list(unique_symptoms_set)
        res.sort()
        return res

    def get_num_logs_by_user(self, user: str) -> int:
        return self._get_user_dailylogs_ref(user).count().get()[0][0].value

    # Private methods
    def _get_user_log_ref(self, user: str, date: str):
        """Get reference to a user's single day log"""

        return self._get_user_dailylogs_ref(user).document(date)

    def _get_user_dailylogs_ref(self, user: str):
        """Get reference to all daily logs for a user"""
        return self._collection.document(user).collection("DailyLogs")
