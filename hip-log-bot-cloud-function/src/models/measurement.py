import logging

logger = logging.getLogger(__name__)


class Measurement:
    ALLOWED_UNITS = [
        "mg",
        "oz",
        "g",
        "CD",
        "kg",
        "lb",
        "t",
        "s",
        "second",
        "min",
        "h",
        "day",
        "wk",
        "mo",
        "yr",
        "decade",
        "century",
    ]

    # Initialization and Magic methods
    def __init__(self, amount: float, unit: str):
        self.amount = amount

        if not isinstance(unit, str):
            raise TypeError("unit must be a string")
        if unit not in self.ALLOWED_UNITS:
            raise ValueError("unit is not an allowed unit")

        self.unit = unit

    def __str__(self):
        return f"{self.amount}{self.unit}"

    def __eq__(self, other):
        return self.amount == other.amount and self.unit == other.unit

    # Public methods
    def to_kilograms(self):
        """Convert the measurement to kilograms.

        Raises:
            ValueError: If current measurement can't be converted (eg unsupported unit)
        """
        if self.unit == "lb":
            logger.debug("Converting lb to kg")
            self.amount = self.amount * 0.453592
            self.unit = "kg"
        elif self.unit == "kg":
            pass
        else:
            raise ValueError(f"Cannot convert {self.unit} to kilograms")

    # Converters
    def to_dict(self):
        return {"amount": self.amount, "unit": self.unit}
