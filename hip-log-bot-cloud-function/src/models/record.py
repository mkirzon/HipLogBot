import logging
from models.measurement import Measurement

logger = logging.getLogger(__name__)


class Record:
    """
    Base class for records to share by Activities/Pains/etc

    While these objects will be flat, they must all have a name (eg an
    Activity name, a Pain name (body part))

    """

    def __init__(self, name, **attributes):
        self.name = name
        for key, value in attributes.items():
            setattr(self, f"{key}", value)
        logger.debug(
            f"Initialized Record '{self.name}' with {len(self.get_attributes())} attributes"  # noqa
        )

    def get_attributes(self) -> dict:
        """Get a dictionary of all the Record attributes that we created.
        Necessary because these are dynamically created. This is different
        from `to_dict()` because the values here can be non-dicts (eg
        Measurement).
        Note this also returns the name

        Returns:
            dict: Dict value
        """

        attrs = {}
        for key, value in self.__dict__.items():
            if not key.startswith("__") and not callable(value):
                attrs[key] = value

        return attrs

    def __str__(self):
        parts = [self.name]
        for k, v in self.get_attributes().items():
            if k == "name" or not v:  # skip since initialized with this
                continue

            if isinstance(v, Measurement):
                parts.append(v.__str__())
            else:
                parts.append(f"{v} {k}")

        return ", ".join(parts)

    def to_dict(self, skip_empty=False) -> dict:
        """Get a fully converted dictionary representation of the record (even
        nested objects will be standard dicts)

        Args:
            skip_empty: if value is None, then it will be removed

        Returns:
            dict: Dictionary
        """
        x = {}
        for k, v in self.get_attributes().items():
            if isinstance(v, Measurement):
                v = v.to_dict()
            x[k] = v

        return x


class Activity(Record):
    def __init__(
        self,
        name,
        reps: int = None,
        duration: Measurement = None,
        weight: Measurement = None,
    ):
        super().__init__(name)
        self.reps = reps

        if isinstance(duration, dict):
            duration = Measurement(**duration)
        if isinstance(weight, dict):
            weight = Measurement(**weight)

        self.duration = duration
        self.weight = weight


class Pain(Record):
    ALLOWED_LEVELS = [0, 1, 2, 3]

    def __init__(self, name, level: int):
        super().__init__(name)

        if level not in self.ALLOWED_LEVELS:
            raise ValueError(
                f"Invalid pain level: {level}. Allowed levels are: {', '.join(map(str, self.ALLOWED_LEVELS))}"  # noqa
            )
        self.level = level
