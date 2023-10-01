from typing import List
from datetime import datetime
import logging
from models.record import Activity, Pain

logger = logging.getLogger(__name__)
logger.propagate = True


class DailyLog:
    # Initialization and Magic Methods
    def __init__(
        self,
        date,
        activities: List[Activity] = [],
        pains: List[Pain] = [],
        activity_notes=None,
        pain_notes=None,
    ):
        self._date = date
        self._activity_notes = activity_notes
        self._pain_notes = pain_notes
        self._activities = {}
        self._pains = {}

        for a in activities:
            self.add_activity(a, overwrite=False)

        for p in pains:
            self.add_pain(p)

    def __str__(self):
        formatted_date = datetime.strptime(self._date, "%Y-%m-%d").strftime(
            "%b. %-d, %Y"
        )
        header = f"{formatted_date} Log:"

        output = [header, ""]
        output.append(f"{len(self.activities)}x activities:")
        for idx, activity in enumerate(self._activities):
            output.append(f"* {self._activities[activity].__str__()}")

        if self._activity_notes:
            output.append(self._activity_notes)

        output.extend(["", f"{len(self.pains)}x pain records:"])
        for idx, pain in enumerate(self._pains):
            output.append(f"* {self._pains[pain].__str__()}")

        if self._pain_notes:
            output.append(self._pain_notes)

        return "\n".join(output)

    # Class Methods
    @classmethod
    def from_dict(cls, date: str, input_dict: dict):
        """Initialize a DailyLog using a dict.

        The input dict structure matches what comes from the Firestore fetch so this
        will be used when downloading a log from Firestore rather than when
        initializing activities from new intents.
        """
        logger.debug("Building DailyLog instance with `from_dict()` method")
        daily_log = cls(date)

        if input_dict.get("activity_notes"):
            logger.debug("Parsing 'activity_notes'")
            daily_log.set_activity_notes(input_dict.get("activity_notes"))

        if input_dict.get("pain_notes"):
            logger.debug("Parsing 'pain_notes'")
            daily_log.set_pain_notes(input_dict.get("pain_notes"))

        if input_dict.get("activities"):
            for activity_name, activity_dict in input_dict["activities"].items():
                logger.debug(
                    f"Parsing activity {activity_name} with input dict: {activity_dict}"
                )
                activity_dict["name"] = activity_name
                daily_log.add_activity(Activity.from_dict(activity_dict))

        if input_dict.get("pains"):
            logger.debug("Parsing 'pains'")
            for pain_name, pain_level in input_dict["pains"].items():
                logger.debug(f"Parsing pain {pain_name} with input: pain_level")
                daily_log.add_pain(Pain(pain_name, pain_level))

        logger.debug("Finished creating a DailyLog instance")

        return daily_log

    # Properties
    @property
    def activities(self) -> dict:
        return self._activities

    @property
    def pains(self):
        return self._pains

    @property
    def date(self):
        return self._date

    # Public Methods related to Activities
    def add_activity(self, activity: Activity, overwrite: bool = False):
        """Add or update an activity to a DailyLog. When updating, by default will
        append as a new set

        Args:
            activity (Activity): an Activity
            overwrite (bool, optional): if True, will overwrite the full instance of
            that activity. If False (default), will simply append the new activity's
            sets
        """
        # Check if the activity name already exists in the day's records
        name = activity.name
        if name in self._activities:
            logger.info(f"Activity '{name}' already exists in this DailyLog")
            if overwrite:
                logger.info("Overwriting activity's sets")
                self._activities[name] = activity
            else:
                logger.info("Adding a new set to activity")
                self._activities[name].sets.extend(activity.sets)
        else:
            logger.info(
                f"Adding activity '{name}' for the first time to the daily log's 'activities' dict"  # noqa
            )  # noqa
            self._activities[name] = activity

    def delete_activity(self, name: str):
        """Remove the activity if it exists, if not notify"""
        if name in self._activities:
            del self._activities[name]
            return True
        else:
            logger.info(
                f"Activity '{name}' doesn't exist for {self._date}. Nothing to delete."  # noqa
            )
            return False

    def get_activity(self, name: str) -> Activity:
        """Retrieve corresponding Activity object"""
        activity = self._activities.get(name)
        if activity:
            return activity
        else:
            logger.info(f"No activity named {name} found.")
            return None

    def list_activities(self):
        """List all activity names."""
        for activity_name in self._activities.keys():
            print(activity_name)

    # Public Methods related to Pains
    def add_pain(self, pain: Pain):
        # Check if the activity name already exists in the day's records
        if pain.name in self._pains:
            print(
                f"Pain record '{pain.name}' already exists for {self._date}. Overwriting previous entry."  # noqa
            )

        # Create a new activity with the provided attributes and add it to the records # noqa
        self._pains[pain.name] = pain

    def delete_pain(self, name: str):
        # Remove the activity if it exists, if not notify
        if name in self._pains:
            del self._pains[name]
        else:
            print(
                f"Pain record '{name}' doesn't exist for {self._date}. Nothing to delete."  # noqa
            )

    # Public Methods related to Notes
    def set_activity_notes(self, notes: str):
        self._activity_notes = notes

    def set_pain_notes(self, notes: str):
        self._pain_notes = notes

    # Converters/Serializers
    def to_dict(self):
        return {
            "date": self.date,
            "activities": {
                name: activity.to_dict(include_name=False)
                for name, activity in self.activities.items()
            },
            "pains": {name: pain.to_dict() for name, pain in self.pains.items()},
            "pain_notes": self._pain_notes,
            "activity_notes": self._activity_notes,
        }
