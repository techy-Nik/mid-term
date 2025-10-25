import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.exceptions import OperationError
import logging


def test_addition():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("5")


def test_subtraction():
    calc = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc.result == Decimal("2")


def test_multiplication():
    calc = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("2"))
    assert calc.result == Decimal("8")


def test_division():
    calc = Calculation(operation="Division", operand1=Decimal("8"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")


def test_division_by_zero():
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        Calculation(operation="Division", operand1=Decimal("8"), operand2=Decimal("0"))


def test_power():
    calc = Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.result == Decimal("8")


def test_negative_power():
    with pytest.raises(OperationError, match="Negative exponents are not supported"):
        Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("-3"))


def test_root():
    calc = Calculation(operation="Root", operand1=Decimal("16"), operand2=Decimal("2"))
    assert calc.result == Decimal("4")


def test_invalid_root():
    with pytest.raises(OperationError, match="Cannot calculate root of negative number"):
        Calculation(operation="Root", operand1=Decimal("-16"), operand2=Decimal("2"))


def test_unknown_operation():
    with pytest.raises(OperationError, match="Unknown operation"):
        Calculation(operation="Unknown", operand1=Decimal("5"), operand2=Decimal("3"))


def test_to_dict():
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    result_dict = calc.to_dict()
    assert result_dict == {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": calc.timestamp.isoformat()
    }


def test_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    calc = Calculation.from_dict(data)
    assert calc.operation == "Addition"
    assert calc.operand1 == Decimal("2")
    assert calc.operand2 == Decimal("3")
    assert calc.result == Decimal("5")


def test_invalid_from_dict():
    data = {
        "operation": "Addition",
        "operand1": "invalid",
        "operand2": "3",
        "result": "5",
        "timestamp": datetime.now().isoformat()
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        Calculation.from_dict(data)


def test_format_result():
    calc = Calculation(operation="Division", operand1=Decimal("1"), operand2=Decimal("3"))
    assert calc.format_result(precision=2) == "0.33"
    assert calc.format_result(precision=10) == "0.3333333333"


def test_equality():
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc3 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("3"))
    assert calc1 == calc2
    assert calc1 != calc3


# New Test to Cover Logging Warning
def test_from_dict_result_mismatch(caplog):
    """
    Test the from_dict method to ensure it logs a warning when the saved result
    does not match the computed result.
    """
    # Arrange
    data = {
        "operation": "Addition",
        "operand1": "2",
        "operand2": "3",
        "result": "10",  # Incorrect result to trigger logging.warning
        "timestamp": datetime.now().isoformat()
    }

    # Act
    with caplog.at_level(logging.WARNING):
        calc = Calculation.from_dict(data)

    # Assert
    assert "Loaded calculation result 10 differs from computed result 5" in caplog.text


# NEW TEST: Cover zero root case (line 81)
def test_zero_root():
    """
    Test that attempting to calculate a zero root raises an OperationError.
    This covers the y == 0 condition in _raise_invalid_root.
    """
    with pytest.raises(OperationError, match="Zero root is undefined"):
        Calculation(operation="Root", operand1=Decimal("16"), operand2=Decimal("0"))


# NEW TEST: Cover the final else clause in _raise_invalid_root (line 81)
def test_root_edge_case_with_zero_radicand_and_negative_index():
    """
    Test an edge case where both x=0 and y is negative.
    This should trigger the final else in _raise_invalid_root.
    """
    # When x=0 and y<0, it fails the x >= 0 and y != 0 check
    # This goes to _raise_invalid_root where y != 0 (so first check passes)
    # and x < 0 check fails (x=0 is not < 0), hitting the final raise
    with pytest.raises(OperationError):
        Calculation(operation="Root", operand1=Decimal("0"), operand2=Decimal("-2"))


# NEW TEST: Cover format_result with edge case that triggers InvalidOperation (line 200)
def test_format_result_with_extreme_value():
    """
    Test format_result with a value that might cause InvalidOperation during quantize.
    This should gracefully fall back to str(result).
    """
    # Create a calculation with a very large or special result
    calc = Calculation(operation="Power", operand1=Decimal("10"), operand2=Decimal("50"))
    # This should still work even with extreme values
    formatted = calc.format_result(precision=2)
    assert isinstance(formatted, str)
    assert len(formatted) > 0


# NEW TEST: Cover the normalize() path in format_result (line 222)
def test_format_result_removes_trailing_zeros():
    """
    Test that format_result properly removes trailing zeros using normalize().
    This covers line 222 where the result is returned after normalization.
    """
    # Create a calculation that results in a number with trailing zeros
    calc = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("4"))
    # Result is 2.5, which when formatted should not have unnecessary trailing zeros
    formatted = calc.format_result(precision=5)
    assert formatted == "2.5"
    
    # Another test with a whole number - check it's a valid number string
    calc2 = Calculation(operation="Multiplication", operand1=Decimal("2"), operand2=Decimal("5"))
    formatted2 = calc2.format_result(precision=5)
    # normalize() may return scientific notation, so just verify it converts back correctly
    assert Decimal(formatted2) == Decimal("10")


# NEW TEST: Additional edge case for format_result
def test_format_result_with_very_small_precision():
    """
    Test format_result with precision of 0 to ensure it handles edge cases.
    """
    calc = Calculation(operation="Division", operand1=Decimal("7"), operand2=Decimal("3"))
    formatted = calc.format_result(precision=0)
    assert formatted == "2"


# NEW TEST: Test __repr__ method for completeness
def test_repr():
    """
    Test the __repr__ method returns a detailed string representation.
    """
    calc = Calculation(operation="Multiplication", operand1=Decimal("3"), operand2=Decimal("4"))
    repr_str = repr(calc)
    assert "Calculation" in repr_str
    assert "operation='Multiplication'" in repr_str
    assert "operand1=3" in repr_str
    assert "operand2=4" in repr_str
    assert "result=12" in repr_str


# NEW TEST: Test __str__ method for completeness
def test_str():
    """
    Test the __str__ method returns a human-readable string.
    """
    calc = Calculation(operation="Addition", operand1=Decimal("5"), operand2=Decimal("3"))
    str_repr = str(calc)
    assert str_repr == "Addition(5, 3) = 8"


# NEW TEST: Test equality with non-Calculation object
def test_equality_with_non_calculation():
    """
    Test that comparing a Calculation with a non-Calculation object returns NotImplemented.
    """
    calc = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    assert calc.__eq__("not a calculation") == NotImplemented
    assert calc != "not a calculation"