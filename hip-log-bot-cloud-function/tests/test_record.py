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

    s = Set(duration=Measurement(1, "kg"))
    assert s.reps is None and s.duration.__str__() == "1kg"


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


def test_set_equality():
    assert Set(1) == Set(1)
    assert Set(1) != Set(2)
    assert Set(duration=Measurement(1, "min")) == Set(duration=Measurement(1, "min"))
    assert Set(duration=Measurement(1, "min")) != Set(weight=Measurement(1, "min"))


def test_record_reps_error():
    with pytest.raises(TypeError):
        Set(reps="5")


# Tests for Activity class
def test_activity_initialization():
    activity = Activity(
        "Shoulder Press",
        sets=[Set(weight=Measurement(10, "kg")), Set(weight=Measurement(12, "kg"))],
    )
    assert activity.name == "Shoulder Press" and [
        x.weight.amount for x in activity.sets
    ] == [10, 12]


def test_activity_initialization_with_no_sets():
    activity = Activity("Yoga")
    assert activity.name == "Yoga" and activity.sets[0].reps == 1


def test_activity_initialization_with_set_dicts():
    # This shows that the sets can be defined with dicts rather than Measurements
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


def test_activity_from_dict():
    a1 = Activity.from_dict({"name": "Yoga", "sets": [{"reps": 1}]})
    assert a1 == Activity("Yoga", [Set(1)])

    a2 = Activity.from_dict(
        {
            "name": "Curls",
            "sets": [
                {"reps": 12, "weight": {"amount": 10, "unit": "kg"}},
                {"reps": 10, "weight": {"amount": 8, "unit": "kg"}},
            ],
        },
    )
    assert a2 == Activity(
        "Curls",
        [Set(12, weight=Measurement(10, "kg")), Set(10, weight=Measurement(8, "kg"))],
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

    assert activity.to_dict(include_name=False) == {
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


def test_activity_equality():
    a1 = Activity(
        "Yoga",
        sets=[
            Set(duration=Measurement(10, "min")),
            Set(duration=Measurement(12, "min")),
        ],
    )
    a2 = Activity(
        "Yoga",
        sets=[
            Set(duration=Measurement(10, "min")),
            Set(duration=Measurement(12, "min")),
        ],
    )
    a3 = Activity(
        "Yoga",
        sets=[
            Set(duration=Measurement(12, "min")),  # flipped order
            Set(duration=Measurement(10, "min")),
        ],
    )
    a4 = Activity("Yoga", sets=[Set(duration=Measurement(12, "min"))])
    assert a1 == a2
    assert a1 != a3
    assert a1 != a4


# Tests for Pain


def test_pain_initialization():
    pain = Pain("Headache", 2)
    assert pain.name == "Headache"
    assert pain.level == 2


def test_invalid_pain_level():
    with pytest.raises(ValueError):
        Pain("Headache", 5)


# Tests for outward conversions
