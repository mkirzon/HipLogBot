from src.models.measurement import Measurement

class Record:
  """
  Base class for records to share by Activities/Pains/etc

  While these objects will be flat, they must all have a name (eg an Activity name, a Pain name (body part))

  """
  def __init__(self, name, **attributes):
    self.name = name
    for key, value in attributes.items():
      setattr(self, f"{key}", value)

  def get_attributes(self) -> dict:
    attrs = {}
    for key, value in self.__dict__.items():
        if not key.startswith('__') and not callable(value):
            attrs[key] = value
    return attrs

  def __str__(self):
    parts = [self.name]
    for k, v in self.get_attributes().items():
      if k == 'name' or not v: # skip since initialized with this
        continue

      if isinstance(v, Measurement):
        parts.append(v.__str__())
      else:
        parts.append(f"{v} {k}")

    return ', '.join(parts)

  def to_dict(self):
    x = {}
    for k, v in self.get_attributes().items():
      if isinstance(v, Measurement):
        v = v.to_dict()
      x[k] = v

    return x

class Activity(Record):
  def __init__(self, name, reps: int = None, duration: Measurement = None, weight: Measurement = None):
      super().__init__(name)
      self.reps = reps

      if isinstance(duration, dict):
        duration = Measurement(**duration)
      if isinstance(weight, dict):
        weight = Measurement(**weight)

      self.duration = duration
      self.weight = weight


class Pain(Record):
  ALLOWED_LEVELS = [0,1,2,3]

  def __init__(self, name, level: int):
      super().__init__(name)

      if level not in self.ALLOWED_LEVELS:
          raise ValueError(f"Invalid pain level: {level}. Allowed levels are: {', '.join(map(str, self.ALLOWED_LEVELS))}")
      self.level = level
