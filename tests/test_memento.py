import pytest
from decimal import Decimal
from datetime import datetime
from app.calculator_memento import CalculatorMemento
from app.calculation import Calculation


def test_memento_initialization():
    """Test that CalculatorMemento initializes correctly."""
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Subtraction", operand1=Decimal("5"), operand2=Decimal("2"))
    
    history = [calc1, calc2]
    memento = CalculatorMemento(history=history)
    
    assert len(memento.history) == 2
    assert memento.history[0] == calc1
    assert memento.history[1] == calc2
    assert isinstance(memento.timestamp, datetime)


def test_memento_to_dict():
    """Test converting memento to dictionary (covers line 34)."""
    calc1 = Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("5"))
    
    history = [calc1, calc2]
    memento = CalculatorMemento(history=history)
    
    # Convert to dictionary
    memento_dict = memento.to_dict()
    
    # Verify structure
    assert 'history' in memento_dict
    assert 'timestamp' in memento_dict
    assert len(memento_dict['history']) == 2
    assert isinstance(memento_dict['timestamp'], str)
    
    # Verify first calculation in dict
    assert memento_dict['history'][0]['operation'] == 'Addition'
    assert memento_dict['history'][0]['operand1'] == '2'
    assert memento_dict['history'][0]['operand2'] == '3'
    assert memento_dict['history'][0]['result'] == '5'


def test_memento_from_dict():
    """Test creating memento from dictionary (covers line 53)."""
    # Create original memento
    calc1 = Calculation(operation="Division", operand1=Decimal("10"), operand2=Decimal("2"))
    original_memento = CalculatorMemento(history=[calc1])
    
    # Convert to dict
    memento_dict = original_memento.to_dict()
    
    # Recreate memento from dict
    restored_memento = CalculatorMemento.from_dict(memento_dict)
    
    # Verify the restored memento
    assert len(restored_memento.history) == 1
    assert restored_memento.history[0].operation == "Division"
    assert restored_memento.history[0].operand1 == Decimal("10")
    assert restored_memento.history[0].operand2 == Decimal("2")
    assert restored_memento.history[0].result == Decimal("5")
    assert isinstance(restored_memento.timestamp, datetime)


def test_memento_round_trip():
    """Test full serialization and deserialization cycle."""
    # Create calculations
    calc1 = Calculation(operation="Power", operand1=Decimal("2"), operand2=Decimal("3"))
    calc2 = Calculation(operation="Root", operand1=Decimal("16"), operand2=Decimal("2"))
    
    # Create memento
    original_memento = CalculatorMemento(history=[calc1, calc2])
    
    # Convert to dict and back
    memento_dict = original_memento.to_dict()
    restored_memento = CalculatorMemento.from_dict(memento_dict)
    
    # Verify all calculations match
    assert len(restored_memento.history) == 2
    assert restored_memento.history[0].operation == calc1.operation
    assert restored_memento.history[0].result == calc1.result
    assert restored_memento.history[1].operation == calc2.operation
    assert restored_memento.history[1].result == calc2.result


def test_memento_empty_history():
    """Test memento with empty history."""
    memento = CalculatorMemento(history=[])
    
    assert len(memento.history) == 0
    assert isinstance(memento.timestamp, datetime)
    
    # Test serialization with empty history
    memento_dict = memento.to_dict()
    assert memento_dict['history'] == []
    
    # Test deserialization with empty history
    restored_memento = CalculatorMemento.from_dict(memento_dict)
    assert len(restored_memento.history) == 0


def test_memento_timestamp_preservation():
    """Test that timestamp is properly preserved through serialization."""
    calc = Calculation(operation="Addition", operand1=Decimal("1"), operand2=Decimal("1"))
    custom_timestamp = datetime(2024, 1, 15, 10, 30, 45)
    
    memento = CalculatorMemento(history=[calc], timestamp=custom_timestamp)
    
    # Serialize and deserialize
    memento_dict = memento.to_dict()
    restored_memento = CalculatorMemento.from_dict(memento_dict)
    
    # Verify timestamp is preserved
    assert restored_memento.timestamp == custom_timestamp