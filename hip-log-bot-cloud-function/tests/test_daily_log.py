from models.record import Activity, Pain, Set, Measurement
from models.daily_log import DailyLog


# Tests for DailyLog class
def test_dailylog_initialization():
    log = DailyLog("2021-09-01", activities=[Activity(name="Yoga")])
    assert log._date == "2021-09-01"
    assert "Yoga" in log._activities.keys()
    assert log._pains == {}


def test_dailylog_initialization_from_dict():
    log = DailyLog(
        "2021-09-01",
        {
            "activities": {
                "Yoga": {"sets": [{"reps": 1}]},
                "Curls": {
                    "sets": [
                        {"reps": 12, "weight": {"amount": 10, "unit": "kg"}},
                        {"reps": 10, "weight": {"amount": 8, "unit": "kg"}},
                    ]
                },
            },
            "activity_notes": "bla bla",
            "pains": {
                "Left hip": 3,
                "Right hip": 2,
            },
        },
    )
    assert log._date == "2021-09-01"
    assert len(log.activities) == 2
    assert len(log.activities["Curls"].sets) == 2


def test_add_new_activity():
    a1 = Activity(name="Yoga")
    a2 = Activity(name="Running", sets=[Set(duration=Measurement(10, "min"))])
    log = DailyLog("2021-09-01", activities=[a1])
    log.add_activity(a2)

    assert all(x in log.activities.values() for x in [a1, a2])


def test_update_activity():
    a1 = Activity(name="Yoga")
    log = DailyLog("2021-09-01", activities=[a1])
    log.add_activity(a1)

    assert log.activities["Yoga"] == Activity("Yoga", [Set(reps=1)] * 2)


def test_add_pain():
    log = DailyLog("2021-09-01")
    pain = Pain("Headache", 2)
    log.add_pain(pain.name, pain.level)
    assert "Headache" in log.pains
    assert log.pains["Headache"].level == 2


# More tests can be added as required, for example, testing other methods, edge cases
