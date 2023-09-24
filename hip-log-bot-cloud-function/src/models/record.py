from __future__ import annotations
from typing import List
import logging
from models.measurement import Measurement

logger = logging.getLogger(__name__)


class Record:
    """
    Base class for records to share by Activities/Pains/etc

    A generic object to store a name (eg Activity name, a Pain body part) + any number
    of attributes. The point of the Base class is to share generic methods for
    initialization, printing, properties
    """

    # Initialization & Magic methods
    def __init__(self, name, **attributes):
        self.name = name
        for key, value in attributes.items():
            setattr(self, f"{key}", value)
        logger.debug(
            f"Initialized Record '{self.name}' with {len(self.attributes)} attributes"  # noqa
        )

    def __str__(self):
        parts = [self.name]
        for k, v in self.attributes.items():
            if k == "name" or not v:  # skip since initialized with this
                continue

            if isinstance(v, list):
                v = [x.__str__() if hasattr(x, "__str__") else x for x in v]

            parts.append(f"{k} {v}")

        return ", ".join(parts)

    def __eq__(self, other):
        if not isinstance(other, Record):
            # Don't attempt to compare against unrelated types
            return NotImplemented
        for attr in set(list(self.attributes.keys()) + list(other.attributes.keys())):
            self_attr = getattr(self, attr)
            other_attr = getattr(other, attr)

            if (self_attr is None) != (other_attr is None):
                return False

            if self_attr != other_attr:
                return False

        return True

    # Properties
    @property
    def attributes(self):
        """Get a dictionary of all the Record attributes that we created (including
        'name'). Necessary because these are dynamically created. This is different
        from `to_dict()` because the values here can be non-dicts (eg Measurement).

        Returns:
            dict: Dict value
        """
        attrs = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__") and not callable(value):
                attrs[key] = value

        return attrs

    # Public Methods
    def to_dict(self, skip_empty=False) -> dict:
        """Get a fully converted dictionary representation of the record (even
        nested objects will be standard dicts)

        Args:
            skip_empty: if value is None, then it will be removed

        Returns:
            dict: Dictionary
        """
        x = {}
        for k, v in self.attributes.items():
            if isinstance(v, Measurement):
                v = v.to_dict()

            x[k] = v

        # TODO: implement skip_empty logic

        return x


class Set:
    # Initialization and Magic methods
    def __init__(
        self, reps: int = None, duration: Measurement = None, weight: Measurement = None
    ):
        if reps and not isinstance(reps, int):
            raise TypeError("reps must be int input")
        self.reps = reps

        if isinstance(duration, dict):
            duration = Measurement(**duration)
        if isinstance(weight, dict):
            weight = Measurement(**weight)

        self.duration = duration
        self.weight = weight

    def __str__(self):
        parts = []
        if self.reps:
            parts.append(f"{self.reps}x")
        if self.duration:
            parts.append(f"{self.duration}")
        if self.weight:
            parts.append(f"{self.weight}")
        return ":".join(parts)

    def __eq__(self, other):
        if not isinstance(other, Set):
            # Don't attempt to compare against unrelated types
            return NotImplemented
        for attr in ["reps", "duration", "weight"]:
            self_attr = getattr(self, attr)
            other_attr = getattr(other, attr)

            if (self_attr is None) != (other_attr is None):
                return False

            if self_attr != other_attr:
                return False

        return True

    # Converters
    def to_dict(self):
        """Convert a Set to dict, skipping empty attributes (eg if no duration set,
        will not be included)

        Returns:
            dict: Dict
        """
        res = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__") and not callable(value) and value:
                res[key] = value.to_dict() if hasattr(value, "to_dict") else value

        return res


class Activity(Record):
    # Initialization
    def __init__(self, name, sets: List[Set] = None):
        """Initialize Activity

        Supports a basic activity or with set info. If no set info provided, defaults
        to a single set with reps=1
        """
        super().__init__(name)
        self.sets = sets if sets is not None else [Set(reps=1)]

    # Class Methods
    @classmethod
    def from_dict(cls, activity_dict: dict) -> Activity:
        activity = cls(activity_dict["name"], [])
        for s in activity_dict["sets"]:
            activity.sets.append(Set(**s))

        return activity

    # Public methods
    def add_set(self, set: Set):
        self.sets.append(set)

    def to_dict(self, include_name=True):
        """Convert activity to a pure dict

        Args:
            include_name (bool, optional): Set to false to omit an entry for 'name'.
            Defaults to True. Not including name is handy when converting for our
            firestore data model

        Returns:
            dict: Dict of activity
        """
        result = {
            "sets": [s.to_dict() if hasattr(s, "to_dict") else s for s in self.sets]
        }
        if include_name:
            result["name"] = self.name
        return result


class Pain(Record):
    ALLOWED_LEVELS = [0, 1, 2, 3]

    def __init__(self, name, level: int):
        super().__init__(name)

        if level not in self.ALLOWED_LEVELS:
            raise ValueError(
                f"Invalid pain level: {level}. Allowed levels are: {', '.join(map(str, self.ALLOWED_LEVELS))}"  # noqa
            )
        self.level = level
