import json
import logging
import datetime
import utils
from models.supported_intents import SupportedIntents

logger = logging.getLogger(__name__)


class Intent:
    """This class is the translation layer between DialogFlow's format to inputs
    expected by the python API (eg to initialize logs and Activities).

    Some of the transformations it may do are:
    * Capitalize names
    * others?

    """

    # Initialization
    def __init__(self, req):
        self._type = req["queryResult"]["intent"]["displayName"]
        self._raw_entity = req["queryResult"]["parameters"]
        self._log_input = {}
        self._date = None
        self._user = None

        if self._type not in SupportedIntents.all():
            raise ValueError("Unsupported intent passed")

        self._set_user(req)
        self._extract_log_input()

        logger.info(f"Parsed Dialogflow request into a {self.type} intent")

    # Magic methods
    def __str__(self):
        return f"{self.type} {f'(date={self._date})' if self._date else ''}: {json.dumps(self._log_input)}"  # noqa

    # Class methods
    @classmethod
    def extract_date(cls, date: str):
        """
        Format timestamp to just the date component string

        Parameters:
        - date (str): full timestamp string in '%Y-%m-%dT%H:%M:%S%z' format
        (e.g '2023-07-24T12:00:00+01:00')

        Returns:
        str: a date string in the '%Y-%m-%d' format
        """

        if date == "today":
            return str(datetime.date.today())
        else:
            return date.split("T")[0]

    # Properties
    @property
    def type(self):
        return self._type

    @property
    def entity(self):
        """The raw entity"""
        return self._raw_entity

    @property
    def log_input(self):
        """Get the log input that the entity was parsed into

        For example -
        * LogActivity: {name, sets}

        """
        return self._log_input

    @property
    def date(self):
        return self._date

    @property
    def user(self):
        return self._user

    # Public Methods

    # Private methods
    def _set_date(self):
        """
        Format timestamp to just the date component string

        Parameters:
        - date (str): full timestamp string in '%Y-%m-%dT%H:%M:%S%z' format
        (e.g '2023-07-24T12:00:00+01:00')

        Returns:
        str: a date string in the '%Y-%m-%d' format
        """

        self._date = Intent.extract_date(self._raw_entity["date"])

    def _extract_log_input(self):
        """Parse the raw entity dict into the dict input that matches the dict
        initialization format of the Record classes

        This sets the _log_input attribute, which aligns the names and types:
        * 'date' is removed
        * 'activity' or 'symptom' will be renamed to 'name'
        * 'severity' will be cast to int
        * Any attributes that are empty (strings), will be skipped

        Raises:
            ValueError: raises errors if date is missing for intent types that should
            include a date
        """

        logger.debug(
            f"Starting parsing raw intent response based on '{self._type}' logic"
        )

        # Extract date for date-based activities
        if self.type in [
            SupportedIntents.LogActivity,
            SupportedIntents.LogSymptom,
            SupportedIntents.GetDailyLog,
            SupportedIntents.DeleteDailyLog,
        ]:
            # Expecting a date parameter for these intents
            if not self._raw_entity.get("date"):
                raise ValueError("Input entity is missing a date among the attributes")

            # Extract date as a top level attribute and remove it from the parsed
            # entities as it's not needed there
            self._set_date()
            logger.debug(f"Set intent date as {self._date}")

        # Now do the processing. In some cases, intent keys/vals need to be renamed
        if self.type == SupportedIntents.LogActivity:
            self._log_input["name"] = self._raw_entity["activity"].lower()

            # Prepare the set dicts from the individaul arrays of reps/durations/weights
            self._log_input["sets"] = []

            # Check that all attributes have values for each set
            attribute_lengths = set(
                [
                    len(v)
                    for k, v in self._raw_entity.items()
                    if k in ["reps", "weight", "duration"] and v != []
                ]
            )
            if len(attribute_lengths) > 1:
                logger.debug("Unique attribute_lenghts > 1 (aka mismatch)")
                raise ValueError("Mismatched number of reps/weights/durations")
            # If no reps/duration/weights provided, skip
            elif attribute_lengths:
                n_sets = len(self._raw_entity["reps"])
                for i in range(n_sets):
                    s = {}  # {"reps": 3, weight: {"amount": 12, "unit": "kg"}}
                    if self._raw_entity["reps"]:
                        s["reps"] = int(self._raw_entity["reps"][i])
                    if self._raw_entity["weight"]:
                        s["weight"] = self._raw_entity["weight"][i]
                    if self._raw_entity["duration"]:
                        s["duration"] = self._raw_entity["duration"][i]
                    self._log_input["sets"].append(s)
            else:
                self._log_input["sets"].append({"reps": 1})

        elif self.type == SupportedIntents.LogSymptom:
            self._log_input["name"] = self._raw_entity["symptom"].lower()
            self._log_input["severity"] = int(self._raw_entity["severity"])

        elif self.type == SupportedIntents.GetActivitySummary:
            self._log_input["name"] = self._raw_entity["activity"].lower()

        # Explicitly handle the simpler activities (can't be in a catch all Else)
        elif self.type in [
            SupportedIntents.DeleteDailyLog,
            SupportedIntents.GetNumLogs,
            SupportedIntents.GetCommandList,
            SupportedIntents.GetActivityList,
            SupportedIntents.GetSymptomList,
        ]:
            logger.debug("Skipping any log input parsing for this intent")
            pass

    def _set_user(self, req):
        """Set the user property, with default handling

        Handles 2 situations:
        1) a test call, can be local or from DialogFlow directly (missing
        `originalDetectIntentRequest`). In this case, defaults to a fake
        username (eg MarkTheTester)
        2) a production call (eg Facebook messenger trigger). This has an expected
        format

        Args:
            req (_type_): request object from DialogFlow
        """
        if not req.get("originalDetectIntentRequest"):
            logger.debug(
                f"originalDetectIntentRequest not found so assuming called locally directly. Defaulting user={utils.test_username}"  # noqa
            )
            user = utils.test_username

        elif req.get("originalDetectIntentRequest")["source"] == "DIALOGFLOW_CONSOLE":
            logger.debug(
                f"originalDetectIntentRequest source is 'DIALOGFLOW_CONSOLE'.  Defaulting user={utils.test_username}"  # noqa
            )
            user = utils.test_username

        else:
            user = (
                req.get("originalDetectIntentRequest", {})
                .get("payload", {})
                .get("data", {})
                .get("sender", {})
                .get("id")
                or "default_value"
            )

            if user == "default_value":
                raise ValueError(
                    "User info not found as expected in originalDetectIntentRequest from Dialogflow. Maybe it's not a FB call"  # noqa
                )

        logger.debug(f"Set user = '{user}'")
        self._user = user
