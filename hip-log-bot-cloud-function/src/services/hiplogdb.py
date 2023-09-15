import logging
import os
from firebase_admin import firestore
from models.daily_log import DailyLog
from utils import is_valid_date_format
from google.cloud.firestore_v1 import aggregation
from google.cloud.firestore_v1.base_query import FieldFilter

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
        self._collection_name = os.environ["FIRESTORE_COLLECTION_NAME"]
        self._collection = self._db.collection(self._collection_name)
        self._num_logs = self._get_num_logs()

    # Properties
    @property
    def num_logs(self):
        return self._num_logs

    @property
    def collection_name(self):
        return self.__collection_name

    # Public Methods
    def get_daily_log(self, user, date: str, initialize_empty=False) -> DailyLog:
        """Get a user's daily log document as a local DailyLog object

        Query firestore collection by user-date and return it as a DailyLog object.
        If date doesn't exist, it initializes the log object

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
        # x = self._fetch_document_by_id(date)
        fetched_doc = (
            self._collection.document(user).collection("DailyLogs").document(date).get()
        )

        if fetched_doc.exists:
            fetched_dict = fetched_doc.to_dict()
            logger.info(f"Retrieved log as dict:\n{fetched_dict}")  # noqa

            # Map the Firestore dict to the DailyLog object
            log = DailyLog.from_dict(date, fetched_dict)
            logger.debug("Converted log dict to DailyLog")

        else:
            logger.info(f"Didn't find log for '{date}'")
            if initialize_empty:
                logger.info(f"Initializing empty DailLog for '{date}'")
                log = DailyLog(date)
            else:
                logger.info("Returning empty (None)")
                log = None

        return log

    def upload_log(self, log: DailyLog):
        log_dict = log.to_dict()

        logger.info(f"Will upload this dict:\n{log_dict}")
        self._collection.document(log.date).set(log_dict)

        # In case this was a new one, update the count
        # TODO: optimization - run this only if log was new
        self._num_logs = self._get_num_logs()

    def delete_log(self, date: str) -> None:
        # pass
        try:
            self._collection.document(date).delete()
            logger.info(f"Document with ID {date} deleted successfully!")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

    def get_activity_summary(self, activity_name: str) -> dict:
        """Get summary statistics for an activity

        Fetch stats with a collection query and format them into a nice summary

        Returns: a dict of stats
        """

        stats = {}

        # Stat 1: total num
        # TODO need to filte ron the contents of the keys of thea ctiviteis
        query = self._collection.where(
            filter=FieldFilter(f"activities.{activity_name}.name", "==", activity_name)
        )
        aggregate_query = aggregation.AggregationQuery(query)
        aggregate_query.count(alias="all")
        results = aggregate_query.get()
        stats["total_count"] = results[0][0].value

        return stats

    # Private methods
    def _get_num_logs(self) -> int:
        documents = self._collection.stream()
        doc_count = sum(1 for _ in documents)
        return doc_count

    def _fetch_document_by_id(self, document_id: str):
        """Download the document"""
        x = self._collection.document(document_id).get()
        logger.debug(
            f"Downloaded document '{self._collection_name}.{document_id}'. Created at '{x.create_time}' and last updated at {x.update_time}'"  # noqa
        )
        return x
