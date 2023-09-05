import logging
from models.record import Activity, Pain

logger = logging.getLogger(__name__)
logger.propagate = True


class DailyLog:
    # Magic Methods
    def __str__(self):
        output = [f"--- Daily Log for {self._date} ---"]

        output.append("\n[Activities]")
        for idx, activity in enumerate(self._activities):
            output.append(f"{idx+1}) {self._activities[activity].__str__()}")

        output.append(self._activity_notes)

        output.append("\n[Pain]")
        for idx, pain in enumerate(self._pains):
            output.append(f"{idx+1}) {self._pains[pain].__str__()}")

        output.append(self._pain_notes)

        return "\n".join(output)

    # Class Methods
    @classmethod
    def from_dict(cls, input_dict):
        instance = cls(input_dict["date"])

        if input_dict.get("activity_notes"):
            instance.set_activity_notes(input_dict.get("activity_notes"))

        if input_dict.get("pain_notes"):
            instance.set_pain_notes(input_dict.get("pain_notes"))

        if input_dict.get("activities"):
            for activity_name, record in input_dict["activities"].items():
                instance.add_activity(**record)

        if input_dict.get("pain"):
            for x in input_dict["pain"]:
                instance.add_pain(**x)

        return instance

    # Initialization
    def __init__(self, date, activites={}, pains={}, activity_notes="", pain_notes=""):
        self.set_date(date)
        self._activities = {}
        self._pains = {}
        self._activity_notes = activity_notes
        self._pain_notes = pain_notes

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
    def add_activity(self, name: str, **attributes):
        # Check if the activity name already exists in the day's records
        res = None
        if name in self._activities:
            logging.info(
                f"Activity '{name}' already exists for {self._date}. Overwriting previous entry."  # noqa
            )
            res = "update"
        else:
            logging.info(
                f"Activity '{name}' doesn't exist yet for {self._date}. Creating new entry."  # noqa
            )
            res = "new"

        # Create/update activity with the provided attributes and add it to
        # the records
        self._activities[name] = Activity(name, **attributes)

        # TODO look into returning status t/f w notes
        return res

    def delete_activity(self, name: str):
        """Remove the activity if it exists, if not notify"""
        if name in self._activities:
            del self._activities[name]
            return True
        else:
            logging.info(
                f"Activity '{name}' doesn't exist for {self._date}. Nothing to delete."  # noqa
            )
            return False

    def get_activity(self, name: str) -> Activity:
        """Retrieve corresponding Activity object"""
        activity = self._activities.get(name)
        if activity:
            return activity
        else:
            logging.info(f"No activity named {name} found.")
            return None

    def list_activities(self):
        """List all activity names."""
        for activity_name in self._activities.keys():
            print(activity_name)

    # Public Methods related to Pains
    def add_pain(self, name: str, level):
        # Check if the activity name already exists in the day's records
        if name in self._pains:
            print(
                f"Pain record '{name}' already exists for {self._date}. Overwriting previous entry."  # noqa
            )

        # Create a new activity with the provided attributes and add it to the records # noqa
        self._pains[name] = Pain(name, level)

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

    # Other public methods
    def set_date(self, date):
        self._date = date

    # Converters/Serializers
    def to_dict(self):
        return {
            "date": self.date,
            "activities": {
                name: activity.to_dict() for name, activity in self.activities.items()
            },
            "pains": {name: pain.to_dict() for name, pain in self.pains.items()},
            "pain_notes": self._pain_notes,
            "activity_notes": self._activity_notes,
        }
