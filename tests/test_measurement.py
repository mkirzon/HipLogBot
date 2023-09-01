import sys
import pytest
print(sys.path)
from src.models.measurement import Measurement  


def test_initialization():
    m = Measurement(10, "mg")
    assert m.amount == 10
    assert m.unit == "mg"

def test_string_representation():
    m = Measurement(15, "oz")
    assert str(m) == "15oz"

def test_to_dict():
    m = Measurement(5, "g")
    assert m.to_dict() == {'amount': 5, 'unit': 'g'}

def test_invalid_unit():
    with pytest.raises(ValueError):
        m = Measurement(10, "invalid_unit")

def test_non_string_unit():
    with pytest.raises(TypeError):
        m = Measurement(10, 123)

def test_conversion_to_kilograms():
    m = Measurement(2, "lb")
    m.to_kilograms()
    assert m.amount == pytest.approx(0.907, 0.001)  # Using approx to handle floating point precision
    assert m.unit == "kg"

    m2 = Measurement(1, "kg")
    m2.to_kilograms()
    assert m2.amount == 1
    assert m2.unit == "kg"

def test_invalid_conversion_to_kilograms():
    m = Measurement(10, "mg")
    with pytest.raises(ValueError):
        m.to_kilograms()

