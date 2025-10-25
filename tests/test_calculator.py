import datetime
from pathlib import Path
import pandas as pd
import pytest
from unittest.mock import Mock, patch, PropertyMock
from decimal import Decimal
from tempfile import TemporaryDirectory
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, AutoSaveObserver
from app.operations import OperationFactory


# Fixture to initialize Calculator with a temporary directory for file paths
@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file:
            
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            yield Calculator(config=config)


# Test Calculator Initialization

def test_calculator_initialization(calculator):
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []
    assert calculator.operation_strategy is None


# Test Logging Setup

@patch('app.calculator.logging.info')
def test_logging_setup(logging_info_mock):
    with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
         patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file:
        mock_log_dir.return_value = Path('/tmp/logs')
        mock_log_file.return_value = Path('/tmp/logs/calculator.log')
        
        calculator = Calculator(CalculatorConfig())
        logging_info_mock.assert_any_call("Calculator initialized with configuration")


# NEW TEST: Cover lines 77-79 (logging setup error handling)
def test_logging_setup_failure():
    """Test that logging setup handles errors properly."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)
        
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch('logging.basicConfig', side_effect=Exception("Logging setup failed")):
            
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            
            with pytest.raises(Exception, match="Logging setup failed"):
                Calculator(config=config)


# NEW TEST: Cover lines 103-106 (load history warning on failure)
def test_calculator_init_with_load_history_failure():
    """Test calculator initialization when load_history fails (covers warning log)."""
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)
        
        with patch.object(CalculatorConfig, 'log_dir', new_callable=PropertyMock) as mock_log_dir, \
             patch.object(CalculatorConfig, 'log_file', new_callable=PropertyMock) as mock_log_file, \
             patch.object(CalculatorConfig, 'history_dir', new_callable=PropertyMock) as mock_history_dir, \
             patch.object(CalculatorConfig, 'history_file', new_callable=PropertyMock) as mock_history_file, \
             patch('app.calculator.Calculator.load_history', side_effect=Exception("Cannot load history")), \
             patch('logging.warning') as mock_warning:
            
            mock_log_dir.return_value = temp_path / "logs"
            mock_log_file.return_value = temp_path / "logs/calculator.log"
            mock_history_dir.return_value = temp_path / "history"
            mock_history_file.return_value = temp_path / "history/calculator_history.csv"
            
            calc = Calculator(config=config)
            mock_warning.assert_called()
            assert calc.history == []


# Test Adding and Removing Observers

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator.observers


def test_remove_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    calculator.remove_observer(observer)
    assert observer not in calculator.observers


# NEW TEST: Test observer notification
def test_notify_observers(calculator):
    """Test that observers are notified of new calculations."""
    mock_observer = Mock()
    calculator.add_observer(mock_observer)
    
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    
    mock_observer.update.assert_called_once()
    call_args = mock_observer.update.call_args[0][0]
    assert call_args.result == Decimal('5')


# Test Setting Operations

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator.operation_strategy == operation


# Test Performing Operations

def test_perform_operation_addition(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    result = calculator.perform_operation(2, 3)
    assert result == Decimal('5')


def test_perform_operation_validation_error(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', 3)


def test_perform_operation_operation_error(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation(2, 3)


# NEW TEST: Cover line 219 (perform_operation ValidationError logging)
def test_perform_operation_logs_validation_error(calculator):
    """Test that validation errors are logged properly."""
    calculator.set_operation(OperationFactory.create_operation('add'))
    
    with patch('logging.error') as mock_error:
        with pytest.raises(ValidationError):
            calculator.perform_operation('invalid', 3)
        
        mock_error.assert_called()
        assert any('Validation error' in str(call) for call in mock_error.call_args_list)


# Test Undo/Redo Functionality

def test_undo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    assert calculator.history == []


def test_redo(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.undo()
    calculator.redo()
    assert len(calculator.history) == 1


# NEW TEST: Cover line 371 (undo returns False when stack is empty)
def test_undo_empty_stack(calculator):
    """Test undo when there's nothing to undo."""
    result = calculator.undo()
    assert result == False
    assert calculator.history == []


# NEW TEST: Cover line 390 (redo returns False when stack is empty)
def test_redo_empty_stack(calculator):
    """Test redo when there's nothing to redo."""
    result = calculator.redo()
    assert result == False
    assert calculator.history == []


# NEW TEST: Test full undo/redo workflow
def test_undo_redo_workflow(calculator):
    """Test complete undo/redo workflow."""
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    assert len(calculator.history) == 1
    
    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation(4, 5)
    assert len(calculator.history) == 2
    
    # Undo last operation
    result = calculator.undo()
    assert result == True
    assert len(calculator.history) == 1
    
    # Undo again
    result = calculator.undo()
    assert result == True
    assert len(calculator.history) == 0
    
    # Try to undo when nothing left
    result = calculator.undo()
    assert result == False
    
    # Redo operations
    result = calculator.redo()
    assert result == True
    assert len(calculator.history) == 1
    
    result = calculator.redo()
    assert result == True
    assert len(calculator.history) == 2
    
    # Try to redo when nothing left
    result = calculator.redo()
    assert result == False


# NEW TEST: Test that performing new operation clears redo stack
def test_new_operation_clears_redo_stack(calculator):
    """Test that performing a new operation clears the redo stack."""
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.perform_operation(4, 5)
    
    # Undo one operation
    calculator.undo()
    assert len(calculator.redo_stack) > 0
    
    # Perform new operation (should clear redo stack)
    calculator.perform_operation(6, 7)
    assert len(calculator.redo_stack) == 0


# Test History Management

@patch('app.calculator.pd.DataFrame.to_csv')
def test_save_history(mock_to_csv, calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.save_history()
    mock_to_csv.assert_called_once()


# NEW TEST: Cover lines 230-233 (save_history with empty history)
def test_save_empty_history(calculator):
    """Test saving when history is empty (covers empty history branch)."""
    calculator.clear_history()
    
    calculator.save_history()
    
    assert calculator.config.history_file.exists()
    
    df = pd.read_csv(calculator.config.history_file)
    assert df.empty
    assert list(df.columns) == ['operation', 'operand1', 'operand2', 'result', 'timestamp']


# NEW TEST: Cover lines 268-275 (save_history failure)
def test_save_history_failure(calculator):
    """Test save_history error handling."""
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    
    with patch('pandas.DataFrame.to_csv', side_effect=Exception("Write error")), \
         patch('logging.error') as mock_error:
        
        with pytest.raises(OperationError, match="Failed to save history"):
            calculator.save_history()
        
        mock_error.assert_called()


@patch('app.calculator.pd.read_csv')
@patch('app.calculator.Path.exists', return_value=True)
def test_load_history(mock_exists, mock_read_csv, calculator):
    mock_read_csv.return_value = pd.DataFrame({
        'operation': ['Addition'],
        'operand1': ['2'],
        'operand2': ['3'],
        'result': ['5'],
        'timestamp': [datetime.datetime.now().isoformat()]
    })
    
    try:
        calculator.load_history()
        assert len(calculator.history) == 1
        assert calculator.history[0].operation == "Addition"
        assert calculator.history[0].operand1 == Decimal("2")
        assert calculator.history[0].operand2 == Decimal("3")
        assert calculator.history[0].result == Decimal("5")
    except OperationError:
        pytest.fail("Loading history failed due to OperationError")


# NEW TEST: Cover line 305 (load_history when file doesn't exist)
def test_load_history_no_file(calculator):
    """Test load_history when no history file exists."""
    if calculator.config.history_file.exists():
        calculator.config.history_file.unlink()
    
    with patch('logging.info') as mock_info:
        calculator.load_history()
        
        assert any('No history file found' in str(call) for call in mock_info.call_args_list)
        assert calculator.history == []


# NEW TEST: Cover lines 309-312 (load_history with empty file)
def test_load_history_empty_file(calculator):
    """Test load_history with an empty CSV file."""
    calculator.config.history_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(columns=['operation', 'operand1', 'operand2', 'result', 'timestamp']
                ).to_csv(calculator.config.history_file, index=False)
    
    with patch('logging.info') as mock_info:
        calculator.load_history()
        
        assert any('empty history' in str(call).lower() for call in mock_info.call_args_list)
        assert calculator.history == []


# NEW TEST: Cover lines 324-333 (load_history failure)
def test_load_history_failure(calculator):
    """Test load_history error handling when called explicitly."""
    # Create a history file first
    calculator.config.history_dir.mkdir(parents=True, exist_ok=True)
    calculator.config.history_file.touch()
    
    # Now test load_history failure when called explicitly
    with patch('pandas.read_csv', side_effect=Exception("Read error")), \
         patch('logging.error') as mock_error:
        
        with pytest.raises(OperationError, match="Failed to load history"):
            calculator.load_history()
        
        mock_error.assert_called()


# NEW TEST: Cover line 344 (get_history_dataframe)
def test_get_history_dataframe(calculator):
    """Test getting history as a DataFrame."""
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation(2, 3)
    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation(4, 5)
    
    df = calculator.get_history_dataframe()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ['operation', 'operand1', 'operand2', 'result', 'timestamp']
    assert df.iloc[0]['operation'] == 'Addition'
    assert df.iloc[1]['operation'] == 'Multiplication'


# Test Clearing History

def test_clear_history(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    calculator.perform_operation(2, 3)
    calculator.clear_history()
    assert calculator.history == []
    assert calculator.undo_stack == []
    assert calculator.redo_stack == []


# NEW TEST: Test history size limit
def test_history_size_limit(calculator):
    """Test that history respects max size limit."""
    calculator.set_operation(OperationFactory.create_operation('add'))
    
    max_size = calculator.config.max_history_size
    
    for i in range(max_size + 5):
        calculator.perform_operation(i, 1)
    
    assert len(calculator.history) <= max_size


# NEW TEST: Test calculator with default config (no config provided)
def test_calculator_default_config():
    """Test calculator initialization with default config."""
    with patch('app.calculator.Path') as mock_path, \
         patch('app.calculator.CalculatorConfig') as mock_config_class, \
         patch('os.makedirs'), \
         patch('logging.basicConfig'), \
         patch('logging.info'):
        
        mock_path.return_value.parent.parent = Path('/tmp')
        
        calc = Calculator()
        
        mock_config_class.assert_called_once()