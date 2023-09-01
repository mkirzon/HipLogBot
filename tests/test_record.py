import pytest
from src.models.record import Record, Activity, Pain
from src.models.measurement import Measurement  

# Tests for Record class
def test_record_initialization():
    record = Record("Test", attr1="value1", attr2="value2")
    assert record.name == "Test"
    assert record.attr1 == "value1"
    assert record.attr2 == "value2"

def test_record_to_dict():
    record = Record("Test", attr1="value1", attr2="value2")
    assert record.to_dict() == {"name": "Test", "attr1": "value1", "attr2": "value2"}

# Tests for Activity class
def test_activity_initialization():
    duration = Measurement(10, "min")
    weight = Measurement(50, "kg")
    activity = Activity("Running", duration=duration, weight=weight)
    assert activity.name == "Running"
    assert activity.duration == duration
    assert activity.weight == weight

def test_activity_with_dict():
    activity = Activity("Running", duration={"amount": 10, "unit": "min"}, weight={"amount": 50, "unit": "kg"})
    assert activity.name == "Running"
    assert isinstance(activity.duration, Measurement)
    assert isinstance(activity.weight, Measurement)

# Tests for Pain class
def test_pain_initialization():
    pain = Pain("Headache", 2)
    assert pain.name == "Headache"
    assert pain.level == 2

def test_invalid_pain_level():
    with pytest.raises(ValueError):
        Pain("Headache", 5)

# More tests can be added as required, for example, testing the string representation, other methods, etc.
