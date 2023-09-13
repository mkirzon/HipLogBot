import pytest
from models.record import Record, Activity, Pain, Set
from models.measurement import Measurement

# Tests for Record class


def test_record_initialization():
    record = Record("Test", attr1="value1", attr2="value2")
    assert record.name == "Test"
    assert record.attr1 == "value1"
    assert record.attr2 == "value2"


def test_record_to_dict():
    record = Record("Test", attr1="value1", attr2=Measurement(10, "kg"))
    assert record.to_dict() == {
        "name": "Test",
        "attr1": "value1",
        "attr2": {"amount": 10, "unit": "kg"},
    }


def test_print_record():
    record = Record("Test", reps="10", attr2="value2")
    assert record.__str__() == "Test, reps 10, attr2 value2"


# Tests for Set class
def test_set_initialization():
    s = Set(reps=10)
    assert s.reps == 10 and s.duration is None


def test_set_initialization_with_dict():
    s = Set(reps=10, duration={"amount": 10, "unit": "min"})
    assert s.duration.amount == 10 and s.duration.unit == "min"


def test_print_set():
    assert Set(reps=10, duration={"amount": 10, "unit": "min"}).__str__() == "10x:10min"
    assert Set(reps=10, weight={"amount": 5, "unit": "kg"}).__str__() == "10x:5kg"
    assert (
        Set(
            reps=10,
            duration={"amount": 10, "unit": "min"},
            weight={"amount": 5, "unit": "kg"},
        ).__str__()
        == "10x:10min:5kg"
    )
    assert Set(weight={"amount": 5, "unit": "lb"}).__str__() == "5lb"


# Tests for Activity class
def test_activity_initialization():
    activity = Activity(
        "Shoulder Press",
        sets=[Set(weight=Measurement(10, "kg")), Set(weight=Measurement(12, "kg"))],
    )
    assert activity.name == "Shoulder Press" and [
        x.weight.amount for x in activity.sets
    ] == [10, 12]


def test_activity_initialization_with_dict():
    activity = Activity(
        "Running",
        sets=[
            Set(
                duration={"amount": 10, "unit": "min"},
                weight={"amount": 50, "unit": "kg"},
            ),
        ],
    )
    assert (
        activity.sets[0].duration.amount == 10 and activity.sets[0].weight.amount == 50
    )


def test_add_set_to_activity():
    activity = Activity("Yoga", sets=[Set(duration=Measurement(10, "min"))])
    activity.add_set(Set(duration=Measurement(30, "min")))

    assert len(activity.sets) == 2


def test_activity_to_dict():
    activity = Activity(
        "Shoulder Press",
        sets=[Set(weight=Measurement(10, "kg")), Set(weight=Measurement(12, "kg"))],
    )

    assert activity.to_dict() == {
        "name": "Shoulder Press",
        "sets": [
            {"weight": {"amount": 10, "unit": "kg"}},
            {"weight": {"amount": 12, "unit": "kg"}},
        ],
    }


def test_print_activity():
    activity = Activity(
        "Shoulder Press",
        sets=[Set(weight=Measurement(10, "kg")), Set(weight=Measurement(12, "kg"))],
    )

    assert activity.__str__() == "Shoulder Press, sets ['10kg', '12kg']"


# Tests for Pain


def test_pain_initialization():
    pain = Pain("Headache", 2)
    assert pain.name == "Headache"
    assert pain.level == 2


def test_invalid_pain_level():
    with pytest.raises(ValueError):
        Pain("Headache", 5)


# Tests for outward conversions
