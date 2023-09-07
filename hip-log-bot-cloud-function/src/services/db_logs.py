import logging
import os
from firebase_admin import firestore
from models.daily_log import DailyLog
from utils import is_valid_date_format

logger = logging.getLogger(__name__)


class DBLogs:
    """A handler class for interacting with the Firestore Database for the Hip Log Bots

    The database is a schema-less document store, where the collection will contain a set of documents.
    Each document is a daily record (so it's name will be "2023-03-04")

    Attributes:
        num_logs (int): number of daily logs for current user in the database (assuming a single user)
        collection_name (str): the selected collection name we'll be writing to

    """

    # Initialization
    def __init__(self):
        """Initialize a handler for my Firestore database.
        This assumes you have the firebase app already started outside of this context
        with `firebase_admin.initialize_app()`
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
    def get_log(self, date: str) -> DailyLog:
        """Get a log object by date

        Query firestore collection by date and return it as a Log object.
        If date doesn't exist, it initializes the log object

        Returns:
            DailyLog: a populated or empty (just date) DailyLog object
        """
        # Input checking
        if not is_valid_date_format(date):
            raise ValueError("Invalid date provided. Must be a 'YYYY-MM-DD' string")

        # Download doc as json
        x = self._fetch_document_by_id(date)

        if x.exists:
            x = x.to_dict()
            logger.info(
                f"Log retrieved successfully. Preview of the returned dict from Firestore:\n{x}"  # noqa
            )

            # Map the Firestore dict to the DailyLog object
            log = DailyLog.from_dict(x)
            logger.info("Log converted to Python log object successfully")

        else:
            # TODO: this shouldn't live here, but handle it upstream
            print(f"Log for date '{date}' doesn't exist. Initiating DailyLog instance")
            log = DailyLog(date)

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

    # Private methods
    def _get_num_logs(self) -> int:
        documents = self._collection.stream()
        doc_count = sum(1 for _ in documents)
        return doc_count

    def _fetch_document_by_id(self, document_id: str):
        """Download the document"""
        x = self._collection.document(document_id).get()
        logger.debug(
            f"Downloaded document '{self._collection_name}.{document_id}'. Created at '{x.create_time}' and last updated at {x.update_time}'"
        )
        return x
