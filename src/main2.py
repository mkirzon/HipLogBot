# import models.record
import logging
from models.daily_log import DailyLog
from src.models.record import *

logging.basicConfig(level=logging.DEBUG)

# record = Record("Test", attr1="value1", attr2=Measurement(10, "kg"))



log = DailyLog("2021-09-01")
activity1 = Activity("Running", duration={"amount": 10, "unit": "min"})
log.add_activity(**activity1.get_attributes())

activity2 = Activity("Running", duration={"amount": 15, "unit": "min"})
# Expecting a warning when adding the same activity name again
res = log.add_activity(**activity2.get_attributes())