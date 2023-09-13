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

    # Magic methods
    def __str__(self):
        parts = [self.name]
        for k, v in self.attributes.items():
            if k == "name" or not v:  # skip since initialized with this
                continue

            if isinstance(v, list):
                # parts.append(
                #     f"[{', '.join([x.__str__() if hasattr(x, '__str__') else x for x in v ])}]"
                # )
                v = [x.__str__() if hasattr(x, "__str__") else x for x in v]

            # if isinstance(v, Measurement):
            #     parts.append(v.__str__())
            # else:
            #     parts.append(f"{k} {v}")
            parts.append(f"{k} {v}")

        return ", ".join(parts)

    # Initialization
    def __init__(self, name, **attributes):
        self.name = name
        for key, value in attributes.items():
            setattr(self, f"{key}", value)
        logger.debug(
            f"Initialized Record '{self.name}' with {len(self.attributes)} attributes"  # noqa
        )

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
    def __init__(
        self, reps: int = None, duration: Measurement = None, weight: Measurement = None
    ):
        self.reps = reps

        if isinstance(duration, dict):
            duration = Measurement(**duration)
        if isinstance(weight, dict):
            weight = Measurement(**weight)

        self.duration = duration
        self.weight = weight

    def to_dict(self):
        res = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__") and not callable(value) and value:
                res[key] = value.to_dict() if hasattr(value, "to_dict") else value

        return res

    def __str__(self):
        parts = []
        if self.reps:
            parts.append(f"{self.reps}x")
        if self.duration:
            parts.append(f"{self.duration}")
        if self.weight:
            parts.append(f"{self.weight}")
        return ":".join(parts)


class Activity(Record):
    # Initialization
    def __init__(self, name, sets: List[Set]):
        super().__init__(name)
        self.sets = sets

    # Public methods
    def add_set(self, set: Set):
        self.sets.append(set)

    def to_dict(self):
        return {
            "name": self.name,
            "sets": [s.to_dict() if hasattr(s, "to_dict") else s for s in self.sets],
        }


class Pain(Record):
    ALLOWED_LEVELS = [0, 1, 2, 3]

    def __init__(self, name, level: int):
        super().__init__(name)

        if level not in self.ALLOWED_LEVELS:
            raise ValueError(
                f"Invalid pain level: {level}. Allowed levels are: {', '.join(map(str, self.ALLOWED_LEVELS))}"  # noqa
            )
        self.level = level
