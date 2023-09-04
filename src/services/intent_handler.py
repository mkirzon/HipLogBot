import copy
import json
import logging

logger = logging.getLogger(__name__)


class Intent:
    ALLOWED_TYPES = ["LogPain", "LogActivity", "GetNumLogs"]

    # Magic methods
    def __str__(self):
        return f"{self.type} {f'(date={self._date})' if self._date else ''}: {json.dumps(self._log_input)}"  # noqa

    # Initialization
    def __init__(self, req):
        self._type = req["queryResult"]["intent"]["displayName"]
        self._raw_entity = req["queryResult"]["parameters"]
        self._log_input = None
        self._date = None

        if self.type not in self.ALLOWED_TYPES:
            raise ValueError("Unsupported intent passed")

        self._parse_entity()

        logger.info(f"Parsed Dialogflow request into a {self.type} intent")

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
        """Get the log input that the entity was parsed into"""
        return self._log_input

    @property
    def date(self):
        return self._date

    # Public Methods

    # Private methods
    def _extract_date(self, date: str) -> str:
        """
        Format timestamp to just the date component string

        Parameters:
        - date (str): full timestamp string in '%Y-%m-%dT%H:%M:%S%z' format
        (e.g '2023-07-24T12:00:00+01:00')

        Returns:
        str: a date string in the '%Y-%m-%d' format
        """

        return date.split("T")[0]

    def _parse_entity(self):
        # Initialize the copy since we'll just modifying the parsed entitites
        self._log_input = copy.deepcopy(self._raw_entity)

        if self.type == "GetNumLogs":
            pass
        else:
            # Expecting a date parameter for these intents
            if not self._raw_entity["date"]:
                raise ValueError("Input entity is missing a date among the attributes")

            # Extract date as a top level attribute and remove it from the parsed
            # entities as it's not needed there
            self._date = self._extract_date(self._raw_entity["date"])
            self._log_input.pop("date", None)

            # For now, the only difference is that some of the names mismatch from the
            # request to my OO model
            if self.type == "LogActivity":
                logger.debug("Parsing LogActivity entity")
                self._log_input["name"] = self._log_input.pop("activity").capitalize()

            elif self.type == "LogPain":
                logger.debug("Parsing LogPain entity")
                self._log_input["name"] = self._log_input.pop("body_part").capitalize()
                self._log_input["level"] = self._log_input.pop("pain_level")
