from typing import List
from datetime import datetime
import logging
from models.record import Activity, Symptom

logger = logging.getLogger(__name__)
logger.propagate = True


class DailyLog:
    # Initialization and Magic Methods
    def __init__(
        self,
        date,
        activities: List[Activity] = [],
        symptoms: List[Symptom] = [],
        activity_notes=None,
        symptom_notes=None,
    ):
        self._date = date
        self._activity_notes = activity_notes
        self._symptom_notes = symptom_notes
        self._activities = {}
        self._symptoms = {}

        for a in activities:
            self.add_activity(a, overwrite=False)

        for p in symptoms:
            self.add_symptom(p)

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

        output.extend(["", f"{len(self.symptoms)}x symptom records:"])
        for idx, symptom in enumerate(self._symptoms):
            output.append(f"* {self._symptoms[symptom].__str__()}")

        if self._symptom_notes:
            output.append(self._symptom_notes)

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

        if input_dict.get("symptom_notes"):
            logger.debug("Parsing 'symptom_notes'")
            daily_log.set_symptom_notes(input_dict.get("symptom_notes"))

        if input_dict.get("activities"):
            for activity_name, activity_dict in input_dict["activities"].items():
                logger.debug(
                    f"Parsing activity {activity_name} with input dict: {activity_dict}"
                )
                activity_dict["name"] = activity_name
                daily_log.add_activity(Activity.from_dict(activity_dict))

        if input_dict.get("symptoms"):
            logger.debug("Parsing 'symptoms'")
            for symptom_name, symptom_dict in input_dict["symptoms"].items():
                logger.debug(
                    f"Parsing symptom {symptom_name} with input: {symptom_dict}"
                )
                daily_log.add_symptom(Symptom(symptom_name, symptom_dict["severity"]))

        logger.debug("Finished creating a DailyLog instance")

        return daily_log

    # Properties
    @property
    def activities(self) -> dict:
        return self._activities

    @property
    def symptoms(self):
        return self._symptoms

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
                # TODO: somewhere here
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

    # Public Methods related to Symptoms
    def add_symptom(self, symptom: Symptom):
        # Check if the activity name already exists in the day's records
        if symptom.name in self._symptoms:
            print(
                f"Symptom record '{symptom.name}' already exists for {self._date}. Overwriting previous entry."  # noqa
            )

        # Create a new activity with the provided attributes and add it to the records # noqa
        self._symptoms[symptom.name] = symptom

    def delete_Symptom(self, name: str):
        # Remove the activity if it exists, if not notify
        if name in self._symptoms:
            del self._symptoms[name]
        else:
            print(
                f"Symptom record '{name}' doesn't exist for {self._date}. Nothing to delete."  # noqa
            )

    # Public Methods related to Notes
    def set_activity_notes(self, notes: str):
        self._activity_notes = notes

    def set_symptom_notes(self, notes: str):
        self._symptom_notes = notes

    # Converters/Serializers
    def to_dict(self):
        return {
            "date": self.date,
            "activities": {
                name: activity.to_dict(include_name=False)
                for name, activity in self.activities.items()
            },
            "symptoms": {
                name: symptom.to_dict(include_name=False)
                for name, symptom in self.symptoms.items()
            },
            "symptom_notes": self._symptom_notes,
            "activity_notes": self._activity_notes,
        }
