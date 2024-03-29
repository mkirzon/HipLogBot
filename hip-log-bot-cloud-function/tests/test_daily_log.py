from models.record import Activity, Symptom, Set, Measurement as M
from models.daily_log import DailyLog


# Tests for DailyLog class
def test_dailylog_initialization():
    log = DailyLog("2021-09-01", activities=[Activity(name="Yoga")])
    assert log._date == "2021-09-01"
    assert "Yoga" in log._activities.keys()
    assert log._symptoms == {}


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
            "symptoms": {
                "Left hip": {"severity": 3},
                "Right hip": {"severity": 2},
            },
        },
    )
    assert log._date == "2021-09-01"
    assert set(log.activities.keys()) == set(["Yoga", "Curls"])
    assert len(log.activities["Curls"].sets) == 2
    assert all(
        x in log.symptoms.values()
        for x in [Symptom("Left hip", 3), Symptom("Right hip", 2)]
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


def test_add_symptom():
    log = DailyLog("2021-09-01")
    log.add_symptom(Symptom("Headache", 2))
    assert "Headache" in log.symptoms
    assert log.symptoms["Headache"].severity == 2


def test_daily_log_print():
    log = DailyLog(
        "2023-09-24",
        activities=[
            Activity(
                "curls",  # intentionally testing lower case
                [Set(reps=10, weight=M(10, "kg")), Set(reps=8, weight=M(8, "kg"))],
            ),
            Activity("Yoga", [Set(duration=M(3, "min"))]),
        ],
        symptoms=[Symptom("left hip", 3)],
    )

    assert (
        log.__str__()
        == """Sep. 24, 2023 Log:

2x activities:
* Curls 2 sets: 10x 10kg, 8x 8kg
* Yoga 1 sets: 3min

1x symptom records:
* Left Hip: 3"""
    )


def test_log_to_dict():
    """
    Motivation for test:
    * Found that I was unintentionally uploading symptoms with the 'name' attribute
    """
    log = DailyLog("2021-09-01")
    log.add_symptom(Symptom("Headache", 2))
    log.to_dict() == {
        "date": "2021-09-01",
        "activities": [],
        "symptoms": {"Headache": {"severity": 2}},
        "symptom_notes": "",
        "activity_notes": "",
    }


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
