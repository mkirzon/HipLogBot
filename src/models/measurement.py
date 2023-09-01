class Measurement:
  ALLOWED_UNITS = ["mg", "oz", "g", "CD", "kg", "lb", "t", 	"s", "second", "min", "h", "day", "wk", "mo", "yr", "decade", "century"]

  def __init__(self, amount: float, unit: str):
    self.amount = amount

    if not isinstance(unit, str):
      raise TypeError("unit must be a string")
    if unit not in self.ALLOWED_UNITS:
      raise ValueError("unit is not an allowed unit")

    self.unit = unit

  def __str__(self):
    return f"{self.amount}{self.unit}"

  def to_dict(self):
    return {
      'amount': self.amount,
      'unit': self.unit
    }

  # Additional methods can be added for functionality like conversion
  # For example, to convert weights from pounds to kilograms:
  def to_kilograms(self):
    if self.unit == "pounds":
      converted_value = self.amount * 0.453592
      return Measurement(converted_value, "kg")
    elif self.unit == "kg":
      return self
    else:
      raise ValueError(f"Cannot convert {self.unit} to kilograms")
