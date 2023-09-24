import json
import logging

logger = logging.getLogger(__name__)


class Intent:
    """This class is the translation layer between DialogFlow's format to inputs
    expected by the python API (eg to initialize logs and Activities).

    Some of the transformations it may do are:
    * Capitalize activity/pain names
    * others?

    """

    SUPPORTED_INTENTS = [
        "LogPain",
        "LogActivity",
        "GetNumLogs",
        "GetDailyLog",
        "DeleteDailyLog",
        "GetActivitySummary",
    ]

    # Initialization
    def __init__(self, req):
        self._type = req["queryResult"]["intent"]["displayName"]
        self._raw_entity = req["queryResult"]["parameters"]
        self._log_input = {}
        self._date = None
        self._user = None

        if self._type not in self.SUPPORTED_INTENTS:
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
        """Get the log input that the entity was parsed into."""
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
        initialization format of the Activity/Pain/Record classes

        This sets the _log_input attribute, which aligns the names and types:
        * 'date' is removed
        * 'acitivity' or 'body_part' will be renamed to 'name'
        * 'pain_level' will be renamed to 'level' and cast to int
        * Any attributes that are empty (strings), will be skipped

        Raises:
            ValueError: raises errors if date is missing for intent types that should
            include a date
        """
        # Initialize the copy since we'll just modifying the parsed entitites
        # self._log_input = {
        #     k: v for k, v in self._raw_entity.items() if v != "" and k != "date"
        # }

        logger.debug(
            f"Starting parsing raw intent response based on '{self._type}' logic"
        )

        # Extract date for date-based activities
        if self.type in ["LogActivity", "LogPain", "GetDailyLog", "DeleteDailyLog"]:
            # Expecting a date parameter for these intents
            if not self._raw_entity.get("date"):
                raise ValueError("Input entity is missing a date among the attributes")

            # Extract date as a top level attribute and remove it from the parsed
            # entities as it's not needed there
            self._set_date()
            logger.debug(f"Set intent date as {self._date}")

        # Now do the processing. In some cases, intent keys/vals need to be renamed
        if self.type == "GetNumLogs":
            pass

        elif self.type == "LogActivity":
            self._log_input["name"] = self._raw_entity["activity"].title()

            # Prepare the set dicts from the individaul arrays of reps/durations/weights
            self._log_input["sets"] = []

            # Check that all attributes have values for each set
            attribute_lengths = set(
                [
                    len(v)
                    for k, v in self._raw_entity.items()
                    if k not in ["activity", "date"] and v != []
                ]
            )
            if len(attribute_lengths) > 1:
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

        elif self.type == "LogPain":
            self._log_input["name"] = self._raw_entity["body_part"].title()
            self._log_input["level"] = int(self._raw_entity["pain_level"])

        elif self.type == "DeleteDailyLog":
            pass

        elif self.type == "GetActivitySummary":
            # TODO: log_input no longer makes sense in the context of this intent.
            #       Maybe activity_name is more of a Intent class attribute?
            self._log_input["name"] = self._raw_entity["activity"].title()
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
                "originalDetectIntentRequest not found so assuming called by Dialogflow directly. Defaulting user=MarkTheTester"  # noqa
            )
            user = "MarkTheTester"

        elif req.get("originalDetectIntentRequest")["source"] == "DIALOGFLOW_CONSOLE":
            logger.debug(
                "originalDetectIntentRequest source is 'DIALOGFLOW_CONSOLE'.  Defaulting user=MarkTheTester"  # noqa
            )
            user = "MarkTheTester"

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
