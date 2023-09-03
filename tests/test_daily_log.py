import logging
import pytest
from src.models.record import Activity, Pain, Record
from src.models.measurement import Measurement
from src.models.daily_log import DailyLog


# Tests for DailyLog class
def test_dailylog_initialization():
    log = DailyLog("2021-09-01")
    assert log._date == "2021-09-01"
    assert log._activities == {}
    assert log._pains == {}

def test_add_activity():
    log = DailyLog("2021-09-01")
    activity = Activity("Running", duration={"amount": 10, "unit": "min"})
    log.add_activity(**activity.get_attributes())
    assert "Running" in log._activities
    assert isinstance(log.get_activity("Running"), Activity)

def test_add_existing_activity(caplog):
    log = DailyLog("2021-09-01")
    activity1 = Activity("Running", duration={"amount": 10, "unit": "min"})
    log.add_activity(**activity1.get_attributes())
    
    activity2 = Activity("Running", duration={"amount": 15, "unit": "min"})
    # Expecting a warning when adding the same activity name again
    with caplog.at_level(logging.DEBUG):
        res = log.add_activity(**activity2.get_attributes())
    assert "already exists" in caplog.text
    assert res == "update"


def test_add_pain():
    log = DailyLog("2021-09-01")
    pain = Pain("Headache", 2)
    log.add_pain(pain.name, pain.level)
    assert "Headache" in log.pains
    assert log.pains["Headache"].level == 2

# More tests can be added as required, for example, testing other methods, edge cases, etc.
