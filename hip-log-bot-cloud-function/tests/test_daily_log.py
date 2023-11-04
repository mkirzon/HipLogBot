from models.record import Activity, Pain, Set, Measurement as M
from models.daily_log import DailyLog


# Tests for DailyLog class
def test_dailylog_initialization():
    log = DailyLog("2021-09-01", activities=[Activity(name="Yoga")])
    assert log._date == "2021-09-01"
    assert "Yoga" in log._activities.keys()
    assert log._pains == {}


def test_dailylog_initialization_from_dict():
    log = DailyLog.from_dict(
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
    assert set(log.activities.keys()) == set(["Yoga", "Curls"])
    assert len(log.activities["Curls"].sets) == 2
    assert all(
        x in log.pains.values() for x in [Pain("Left hip", 3), Pain("Right hip", 2)]
    )


def test_add_new_activity():
    a1 = Activity(name="Yoga")
    a2 = Activity(name="Running", sets=[Set(duration=M(10, "min"))])
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
    log.add_pain(Pain("Headache", 2))
    assert "Headache" in log.pains
    assert log.pains["Headache"].level == 2


def test_daily_log_print():
    log = DailyLog(
        "2023-09-24",
        activities=[
            Activity(
                "Curls",
                [Set(reps=10, weight=M(10, "kg")), Set(reps=8, weight=M(8, "kg"))],
            ),
            Activity("Yoga", [Set(duration=M(3, "min"))]),
        ],
        pains=[Pain("Left hip", 3)],
    )

    assert (
        log.__str__()
        == """Sep. 24, 2023 Log:

2x activities:
* Curls 2 sets: 10x 10kg, 8x 8kg
* Yoga 1 sets: 3min

1x pain records:
* Left hip pain: 3"""
    )


def test_add_activity_to_existing_log():
    log = DailyLog(
        "2023-11-04",
        activities=[
            Activity(
                "Yoga",
                [Set(reps=1)],
            ),
            Activity("Handstands", [Set(reps=5), Set(reps=10)]),
        ],
    )

    log.add_activity(Activity("Handstands", [Set(reps=4)]))

    print("helo")
