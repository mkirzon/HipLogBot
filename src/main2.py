import sys 
print(sys.path)

# import models.record
from src.models.record import *

record = Record("Test", attr1="value1", attr2=Measurement(10, "kg"))
assert record.to_dict() == {"name": "Test", "attr1": "value1", "attr2": {"amount": 10, "unit": "kg"}}

