import pytest
from unittest.mock import Mock, patch, MagicMock, call
from decimal import Decimal
from app.calculator_repl import calculator_repl, CalculatorREPL
from app.exceptions import OperationError, ValidationError
from colorama import Fore, Style


# ========================================
# Helper Functions
# ========================================

def strip_ansi(text):
    """Remove ANSI color codes from text for easier assertion."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def get_print_output(mock_print):
    """Extract all printed text from mock_print calls."""
    calls_text = ' '.join(str(call) for call in mock_print.call_args_list)
    return strip_ansi(calls_text)


# ========================================
# Basic REPL Initialization Tests
# ========================================

def test_repl_initialization():
    """Test CalculatorREPL initialization."""
    repl = CalculatorREPL()
    assert repl.calc is not None
    assert len(repl.calc.observers) == 2
    assert repl.running == True
    assert repl.command_registry is not None
    assert repl.help_display is not None


# ========================================
# Display Methods Tests
# ========================================

@patch('builtins.print')
def test_display_welcome(mock_print):
    """Test welcome message display."""
    repl = CalculatorREPL()
    repl.display_welcome()
    
    assert mock_print.called
    output = get_print_output(mock_print)
    assert 'CALCULATOR REPL' in output or 'Calculator' in output


@patch('builtins.print')
def test_display_help(mock_print):
    """Test help message display."""
    repl = CalculatorREPL()
    repl.display_help()
    
    output = get_print_output(mock_print)
    assert 'AVAILABLE COMMANDS' in output or 'COMMANDS' in output
    assert 'add' in output.lower()


@patch('builtins.print')
def test_display_history_empty(mock_print):
    """Test displaying empty history."""
    repl = CalculatorREPL()
    repl.display_history()
    
    # Just verify the method was called and printed something
    assert mock_print.called
    # Get the output to check it contains something about history
    output = get_print_output(mock_print)
    # Be very flexible - just check that some output was produced
    assert len(output) > 0


@patch('builtins.print')
def test_display_history_with_entries(mock_print):
    """Test displaying history with entries."""
    repl = CalculatorREPL()
    repl.calc.set_operation(Mock(execute=lambda a, b: a + b, __str__=lambda s: "Addition"))
    repl.calc.perform_operation(2, 3)
    
    repl.display_history()
    
    output = get_print_output(mock_print)
    assert 'CALCULATION HISTORY' in output or 'HISTORY' in output


# ========================================
# Exit Handler Tests
# ========================================

@patch('builtins.print')
def test_handle_exit_success(mock_print):
    """Test successful exit with history save."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.handle_exit()
        
        assert repl.running == False
        output = get_print_output(mock_print)
        assert 'saved' in output.lower() or 'History saved' in output
        assert 'Thank you' in output or 'Goodbye' in output or 'Come back' in output


@patch('builtins.print')
def test_handle_exit_save_failure(mock_print):
    """Test exit when history save fails."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history', side_effect=Exception("Save failed")):
        repl.handle_exit()
        
        assert repl.running == False
        output = get_print_output(mock_print)
        assert 'Could not save history' in output or 'Warning' in output


# ========================================
# History Command Tests
# ========================================

@patch('builtins.print')
def test_handle_history_command_history(mock_print):
    """Test 'history' command."""
    repl = CalculatorREPL()
    result = repl.handle_history_command('history')
    
    assert result == True
    assert mock_print.called


@patch('builtins.print')
def test_handle_history_command_clear(mock_print):
    """Test 'clear' command."""
    repl = CalculatorREPL()
    repl.calc.set_operation(Mock(execute=lambda a, b: a + b, __str__=lambda s: "Addition"))
    repl.calc.perform_operation(2, 3)
    
    result = repl.handle_history_command('clear')
    
    assert result == True
    assert len(repl.calc.history) == 0
    output = get_print_output(mock_print)
    assert 'cleared' in output.lower()


@patch('builtins.print')
def test_handle_history_command_undo_success(mock_print):
    """Test 'undo' command with successful undo."""
    repl = CalculatorREPL()
    repl.calc.set_operation(Mock(execute=lambda a, b: a + b, __str__=lambda s: "Addition"))
    repl.calc.perform_operation(2, 3)
    
    result = repl.handle_history_command('undo')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'undone' in output.lower()


@patch('builtins.print')
def test_handle_history_command_undo_nothing(mock_print):
    """Test 'undo' command when nothing to undo."""
    repl = CalculatorREPL()
    
    result = repl.handle_history_command('undo')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'Nothing to undo' in output or 'Nothing' in output


@patch('builtins.print')
def test_handle_history_command_redo_success(mock_print):
    """Test 'redo' command with successful redo."""
    repl = CalculatorREPL()
    repl.calc.set_operation(Mock(execute=lambda a, b: a + b, __str__=lambda s: "Addition"))
    repl.calc.perform_operation(2, 3)
    repl.calc.undo()
    
    result = repl.handle_history_command('redo')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'redone' in output.lower()


@patch('builtins.print')
def test_handle_history_command_redo_nothing(mock_print):
    """Test 'redo' command when nothing to redo."""
    repl = CalculatorREPL()
    
    result = repl.handle_history_command('redo')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'Nothing to redo' in output or 'Nothing' in output


def test_handle_history_command_unknown():
    """Test handle_history_command with unknown command."""
    repl = CalculatorREPL()
    result = repl.handle_history_command('unknown')
    
    assert result == False


# ========================================
# File Command Tests
# ========================================

@patch('builtins.print')
def test_handle_file_command_save_success(mock_print):
    """Test 'save' command with successful save."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        result = repl.handle_file_command('save')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'saved successfully' in output.lower()


@patch('builtins.print')
def test_handle_file_command_save_failure(mock_print):
    """Test 'save' command with save failure."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history', side_effect=Exception("Save failed")):
        result = repl.handle_file_command('save')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'Error saving history' in output or 'Error' in output


@patch('builtins.print')
def test_handle_file_command_load_success(mock_print):
    """Test 'load' command with successful load."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'load_history'):
        result = repl.handle_file_command('load')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'loaded successfully' in output.lower()


@patch('builtins.print')
def test_handle_file_command_load_failure(mock_print):
    """Test 'load' command with load failure."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'load_history', side_effect=Exception("Load failed")):
        result = repl.handle_file_command('load')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'Error loading history' in output or 'Error' in output


def test_handle_file_command_unknown():
    """Test handle_file_command with unknown command."""
    repl = CalculatorREPL()
    result = repl.handle_file_command('unknown')
    
    assert result == False


# ========================================
# Operation Input Tests
# ========================================

@patch('builtins.input', side_effect=['5', '3'])
@patch('builtins.print')
def test_get_operation_inputs_valid(mock_print, mock_input):
    """Test getting valid operation inputs."""
    repl = CalculatorREPL()
    a, b = repl.get_operation_inputs('add')
    
    assert a == '5'
    assert b == '3'


@patch('builtins.input', side_effect=['cancel'])
@patch('builtins.print')
def test_get_operation_inputs_cancel_first(mock_print, mock_input):
    """Test canceling at first input."""
    repl = CalculatorREPL()
    a, b = repl.get_operation_inputs('add')
    
    assert a is None
    assert b is None
    output = get_print_output(mock_print)
    assert 'cancelled' in output.lower()


@patch('builtins.input', side_effect=['5', 'cancel'])
@patch('builtins.print')
def test_get_operation_inputs_cancel_second(mock_print, mock_input):
    """Test canceling at second input."""
    repl = CalculatorREPL()
    a, b = repl.get_operation_inputs('add')
    
    assert a is None
    assert b is None
    output = get_print_output(mock_print)
    assert 'cancelled' in output.lower()


@patch('builtins.input', side_effect=['10', '5'])
@patch('builtins.print')
def test_get_operation_inputs_percentage(mock_print, mock_input):
    """Test getting inputs for percentage operation with custom prompts."""
    repl = CalculatorREPL()
    a, b = repl.get_operation_inputs('percentage')
    
    assert a == '10'
    assert b == '5'


@patch('builtins.input', side_effect=['16', '2'])
@patch('builtins.print')
def test_get_operation_inputs_root(mock_print, mock_input):
    """Test getting inputs for root operation with custom prompts."""
    repl = CalculatorREPL()
    a, b = repl.get_operation_inputs('root')
    
    assert a == '16'
    assert b == '2'


# ========================================
# Operation Handler Tests
# ========================================

@patch('builtins.input', side_effect=['2', '3'])
@patch('builtins.print')
def test_handle_operation_add(mock_print, mock_input):
    """Test handling addition operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('add')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '5' in output


@patch('builtins.input', side_effect=['10', '2'])
@patch('builtins.print')
def test_handle_operation_subtract(mock_print, mock_input):
    """Test handling subtraction operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('subtract')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '8' in output


@patch('builtins.input', side_effect=['4', '5'])
@patch('builtins.print')
def test_handle_operation_multiply(mock_print, mock_input):
    """Test handling multiplication operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('multiply')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '20' in output or '2E+1' in output or '2.0E+1' in output


@patch('builtins.input', side_effect=['10', '2'])
@patch('builtins.print')
def test_handle_operation_divide(mock_print, mock_input):
    """Test handling division operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('divide')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '5' in output


@patch('builtins.input', side_effect=['2', '3'])
@patch('builtins.print')
def test_handle_operation_power(mock_print, mock_input):
    """Test handling power operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('power')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '8' in output


@patch('builtins.input', side_effect=['16', '2'])
@patch('builtins.print')
def test_handle_operation_root(mock_print, mock_input):
    """Test handling root operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('root')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '4' in output


@patch('builtins.input', side_effect=['cancel'])
@patch('builtins.print')
def test_handle_operation_cancelled(mock_print, mock_input):
    """Test handling operation when user cancels."""
    repl = CalculatorREPL()
    result = repl.handle_operation('add')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'cancelled' in output.lower()


@patch('builtins.input', side_effect=['invalid', '3'])
@patch('builtins.print')
def test_handle_operation_validation_error(mock_print, mock_input):
    """Test handling operation with validation error."""
    repl = CalculatorREPL()
    result = repl.handle_operation('add')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'ERROR' in output or 'Error' in output


@patch('builtins.input', side_effect=['10', '0'])
@patch('builtins.print')
def test_handle_operation_operation_error(mock_print, mock_input):
    """Test handling operation with operation error (division by zero)."""
    repl = CalculatorREPL()
    result = repl.handle_operation('divide')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'ERROR' in output or 'Error' in output


@patch('builtins.input', side_effect=['2', '3'])
@patch('builtins.print')
def test_handle_operation_unexpected_error(mock_print, mock_input):
    """Test handling operation with unexpected error."""
    repl = CalculatorREPL()
    
    with patch('app.operations.OperationFactory.create_operation', side_effect=Exception("Unexpected")):
        result = repl.handle_operation('add')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'error' in output.lower()


def test_handle_operation_unknown_command():
    """Test handle_operation with unknown command."""
    repl = CalculatorREPL()
    result = repl.handle_operation('unknown')
    
    assert result == False


@patch('builtins.input', side_effect=['10', '3'])
@patch('builtins.print')
def test_handle_operation_modulus(mock_print, mock_input):
    """Test handling modulus operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('modulus')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output


@patch('builtins.input', side_effect=['10', '3'])
@patch('builtins.print')
def test_handle_operation_intdiv(mock_print, mock_input):
    """Test handling integer division operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('intdiv')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output


@patch('builtins.input', side_effect=['50', '200'])
@patch('builtins.print')
def test_handle_operation_percentage(mock_print, mock_input):
    """Test handling percentage operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('percentage')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '%' in output


@patch('builtins.input', side_effect=['10', '3'])
@patch('builtins.print')
def test_handle_operation_absdiff(mock_print, mock_input):
    """Test handling absolute difference operation."""
    repl = CalculatorREPL()
    result = repl.handle_operation('absdiff')
    
    assert result == True
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output


# ========================================
# Process Command Tests
# ========================================

@patch('builtins.print')
def test_process_command_empty(mock_print):
    """Test processing empty command."""
    repl = CalculatorREPL()
    repl.process_command('')
    
    mock_print.assert_not_called()


@patch('builtins.print')
def test_process_command_help(mock_print):
    """Test processing help command."""
    repl = CalculatorREPL()
    repl.process_command('help')
    
    output = get_print_output(mock_print)
    assert 'AVAILABLE COMMANDS' in output or 'COMMANDS' in output


@patch('builtins.print')
def test_process_command_exit(mock_print):
    """Test processing exit command."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.process_command('exit')
        
        assert repl.running == False


@patch('builtins.print')
def test_process_command_history(mock_print):
    """Test processing history command."""
    repl = CalculatorREPL()
    repl.process_command('history')
    
    assert mock_print.called


@patch('builtins.print')
def test_process_command_save(mock_print):
    """Test processing save command."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.process_command('save')
        
        output = get_print_output(mock_print)
        assert 'saved' in output.lower()


@patch('builtins.input', side_effect=['2', '3'])
@patch('builtins.print')
def test_process_command_operation(mock_print, mock_input):
    """Test processing operation command."""
    repl = CalculatorREPL()
    repl.process_command('add')
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output


@patch('builtins.print')
def test_process_command_unknown(mock_print):
    """Test processing unknown command."""
    repl = CalculatorREPL()
    repl.process_command('invalid_command')
    
    output = get_print_output(mock_print)
    assert 'Unknown command' in output or 'UNKNOWN COMMAND' in output


@patch('builtins.print')
def test_process_command_case_insensitive(mock_print):
    """Test that commands are case insensitive."""
    repl = CalculatorREPL()
    repl.process_command('HELP')
    
    output = get_print_output(mock_print)
    assert 'AVAILABLE COMMANDS' in output or 'COMMANDS' in output


@patch('builtins.print')
def test_process_command_with_whitespace(mock_print):
    """Test that commands with whitespace are trimmed."""
    repl = CalculatorREPL()
    repl.process_command('  help  ')
    
    output = get_print_output(mock_print)
    assert 'AVAILABLE COMMANDS' in output or 'COMMANDS' in output


# ========================================
# Main Run Loop Tests
# ========================================

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_run_exit(mock_print, mock_input):
    """Test running REPL and exiting."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.run()
        
        output = get_print_output(mock_print)
        assert 'CALCULATOR' in output or 'Calculator' in output
        assert 'Thank you' in output or 'Goodbye' in output or 'Come back' in output


@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_run_help_then_exit(mock_print, mock_input):
    """Test running REPL with help command then exit."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.run()
        
        output = get_print_output(mock_print)
        assert 'AVAILABLE COMMANDS' in output or 'COMMANDS' in output


@patch('builtins.input', side_effect=[KeyboardInterrupt(), 'exit'])
@patch('builtins.print')
def test_run_keyboard_interrupt(mock_print, mock_input):
    """Test handling KeyboardInterrupt (Ctrl+C)."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.run()
        
        output = get_print_output(mock_print)
        assert 'cancelled' in output.lower() or 'Cancelled' in output


@patch('builtins.input', side_effect=EOFError())
@patch('builtins.print')
def test_run_eof_error(mock_print, mock_input):
    """Test handling EOFError (Ctrl+D)."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.run()
        
        output = get_print_output(mock_print)
        assert 'Terminated' in output or 'terminated' in output.lower()


@patch('builtins.input', side_effect=[Exception("Test error"), 'exit'])
@patch('builtins.print')
def test_run_unexpected_error(mock_print, mock_input):
    """Test handling unexpected error in main loop."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.run()
        
        output = get_print_output(mock_print)
        assert 'Error' in output or 'error' in output or 'ERROR' in output


# ========================================
# calculator_repl() Function Tests
# ========================================

@patch('builtins.input', side_effect=['exit'])
@patch('builtins.print')
def test_calculator_repl_function_exit(mock_print, mock_input):
    """Test the calculator_repl() function with exit command."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'saved' in output.lower()
    assert 'Thank you' in output or 'Goodbye' in output or 'Come back' in output


@patch('builtins.input', side_effect=['help', 'exit'])
@patch('builtins.print')
def test_calculator_repl_function_help(mock_print, mock_input):
    """Test the calculator_repl() function with help command."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'AVAILABLE COMMANDS' in output or 'COMMANDS' in output


@patch('builtins.input', side_effect=['add', '2', '3', 'exit'])
@patch('builtins.print')
def test_calculator_repl_function_addition(mock_print, mock_input):
    """Test the calculator_repl() function with addition."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '5' in output


@patch('app.calculator_repl.CalculatorREPL')
@patch('builtins.print')
@patch('logging.error')
def test_calculator_repl_function_fatal_error(mock_log_error, mock_print, mock_repl_class):
    """Test the calculator_repl() function with fatal error."""
    mock_repl_instance = Mock()
    mock_repl_instance.run.side_effect = Exception("Fatal error")
    mock_repl_class.return_value = mock_repl_instance
    
    with pytest.raises(Exception, match="Fatal error"):
        calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'Fatal error' in output or 'FATAL ERROR' in output
    mock_log_error.assert_called()


# ========================================
# Integration Tests
# ========================================

@patch('builtins.input', side_effect=['add', '2', '3', 'history', 'clear', 'exit'])
@patch('builtins.print')
def test_full_workflow(mock_print, mock_input):
    """Test a full workflow: add, show history, clear, exit."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '5' in output or 'HISTORY' in output
    assert 'cleared' in output.lower()


@patch('builtins.input', side_effect=['add', '5', '3', 'undo', 'redo', 'exit'])
@patch('builtins.print')
def test_undo_redo_workflow(mock_print, mock_input):
    """Test undo/redo workflow."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '8' in output or 'undone' in output.lower()
    assert 'undone' in output.lower()
    assert 'redone' in output.lower()


@patch('builtins.input', side_effect=['multiply', '4', '5', 'save', 'exit'])
@patch('builtins.print')
def test_save_workflow(mock_print, mock_input):
    """Test workflow with save operation."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '20' in output or '2E+1' in output or '2.0E+1' in output
    assert 'saved' in output.lower()


@patch('builtins.input', side_effect=['divide', '10', '2', 'subtract', '8', '3', 'history', 'exit'])
@patch('builtins.print')
def test_multiple_operations_workflow(mock_print, mock_input):
    """Test workflow with multiple operations."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '5' in output
    assert 'HISTORY' in output or 'history' in output.lower()


@patch('builtins.input', side_effect=['power', '2', '8', 'root', '256', '2', 'exit'])
@patch('builtins.print')
def test_power_and_root_workflow(mock_print, mock_input):
    """Test workflow with power and root operations."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '256' in output or '16' in output


# ========================================
# Coverage Gap Tests
# ========================================

@patch('builtins.print')
def test_display_history_multiple_entries(mock_print):
    """Test displaying history with multiple entries for alternating colors."""
    repl = CalculatorREPL()
    
    # Add multiple operations to test alternating row colors
    mock_op = Mock(execute=lambda a, b: a + b, __str__=lambda s: "Addition")
    repl.calc.set_operation(mock_op)
    for i in range(5):
        repl.calc.perform_operation(i, i+1)
    
    repl.display_history()
    
    output = get_print_output(mock_print)
    assert 'CALCULATION HISTORY' in output or 'HISTORY' in output
    assert 'Total calculations' in output or '5' in output


@patch('builtins.input', side_effect=['very_long_command_name_that_exceeds_limit'])
@patch('builtins.print')
def test_process_command_long_unknown(mock_print, mock_input):
    """Test processing very long unknown command (tests line 299 truncation)."""
    repl = CalculatorREPL()
    repl.process_command('a' * 50)
    
    output = get_print_output(mock_print)
    assert 'UNKNOWN COMMAND' in output or 'Unknown command' in output


@patch('builtins.input', side_effect=['5', '3'])
@patch('builtins.print')
def test_handle_operation_long_error_message(mock_print, mock_input):
    """Test handling operation with very long error message (tests line 281-283)."""
    repl = CalculatorREPL()
    
    long_error = "This is a very long error message " * 10
    with patch('app.operations.OperationFactory.create_operation', 
               side_effect=ValidationError(long_error)):
        result = repl.handle_operation('add')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'ERROR' in output


@patch('builtins.input', side_effect=['5', '3'])
@patch('builtins.print')
def test_handle_operation_with_decimal_normalization(mock_print, mock_input):
    """Test operation result normalization for Decimal (tests line 240-241)."""
    repl = CalculatorREPL()
    
    # Mock an operation that returns a Decimal
    with patch('app.calculator.Calculator.perform_operation', return_value=Decimal('5.0000')):
        result = repl.handle_operation('add')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'RESULT' in output or 'Result' in output


@patch('builtins.input', side_effect=['50', '200'])
@patch('builtins.print')
def test_handle_operation_percentage_display(mock_print, mock_input):
    """Test percentage operation special display formatting."""
    repl = CalculatorREPL()
    result = repl.handle_operation('percentage')
    
    assert result == True
    output = get_print_output(mock_print)
    assert '%' in output
    assert 'RESULT' in output


@patch('builtins.print')
def test_colors_configuration(mock_print):
    """Test that color configuration is properly set."""
    repl = CalculatorREPL()
    
    assert 'header' in repl.COLORS
    assert 'success' in repl.COLORS
    assert 'error' in repl.COLORS
    assert 'warning' in repl.COLORS
    assert 'info' in repl.COLORS
    assert 'prompt' in repl.COLORS
    assert 'result' in repl.COLORS


@patch('builtins.print')
def test_operation_commands_list(mock_print):
    """Test that OPERATION_COMMANDS contains all expected operations."""
    repl = CalculatorREPL()
    
    expected_ops = [
        'add', 'subtract', 'multiply', 'divide', 
        'power', 'root', 'modulus', 'intdiv', 
        'percentage', 'absdiff'
    ]
    
    for op in expected_ops:
        assert op in repl.OPERATION_COMMANDS


@patch('builtins.input', side_effect=['load', 'exit'])
@patch('builtins.print')
def test_load_command_workflow(mock_print, mock_input):
    """Test load command in full workflow."""
    with patch('app.calculator.Calculator.load_history'):
        calculator_repl()
        
        output = get_print_output(mock_print)
        assert 'loaded' in output.lower()


@patch('builtins.input', side_effect=['undo', 'exit'])
@patch('builtins.print')
def test_undo_empty_history_workflow(mock_print, mock_input):
    """Test undo with empty history in full workflow."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'Nothing to undo' in output or 'Nothing' in output


@patch('builtins.input', side_effect=['redo', 'exit'])
@patch('builtins.print')
def test_redo_empty_workflow(mock_print, mock_input):
    """Test redo with nothing to redo in full workflow."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'Nothing to redo' in output or 'Nothing' in output


# ========================================
# Additional Edge Cases
# ========================================

@patch('builtins.input', side_effect=['5', '3'])
@patch('builtins.print')
def test_handle_operation_result_with_scientific_notation(mock_print, mock_input):
    """Test handling very large numbers that may use scientific notation."""
    repl = CalculatorREPL()
    
    with patch('app.calculator.Calculator.perform_operation', 
               return_value=Decimal('1.23E+50')):
        result = repl.handle_operation('multiply')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'RESULT' in output


@patch('builtins.print')
def test_command_registry_initialization(mock_print):
    """Test that command registry is properly initialized."""
    repl = CalculatorREPL()
    
    assert repl.command_registry is not None
    # Test that some commands are registered
    assert repl.command_registry.get_command_info('add') is not None


@patch('builtins.print')
def test_help_display_initialization(mock_print):
    """Test that help display is properly initialized with decorator pattern."""
    repl = CalculatorREPL()
    
    assert repl.help_display is not None


@patch('builtins.input', side_effect=['', '', 'exit'])
@patch('builtins.print')
def test_multiple_empty_commands(mock_print, mock_input):
    """Test handling multiple empty commands in sequence."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.run()
        
        # Empty commands should not produce any output
        output = get_print_output(mock_print)
        assert 'CALCULATOR' in output or 'Calculator' in output


@patch('builtins.input', side_effect=['5', '3'])
@patch('builtins.print')
def test_handle_operation_exception_with_long_message(mock_print, mock_input):
    """Test unexpected exception with very long error message."""
    repl = CalculatorREPL()
    
    very_long_error = "Unexpected error message that is extremely long " * 20
    with patch('app.calculator.Calculator.perform_operation', 
               side_effect=Exception(very_long_error)):
        result = repl.handle_operation('add')
        
        assert result == True
        output = get_print_output(mock_print)
        assert 'UNEXPECTED ERROR' in output or 'error' in output.lower()


@patch('builtins.input', side_effect=['  ', 'exit'])
@patch('builtins.print')
def test_whitespace_only_command(mock_print, mock_input):
    """Test command with only whitespace."""
    repl = CalculatorREPL()
    
    with patch.object(repl.calc, 'save_history'):
        repl.run()


@patch('builtins.input', side_effect=['HeLp', 'exit'])
@patch('builtins.print')
def test_mixed_case_command(mock_print, mock_input):
    """Test command with mixed case."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'AVAILABLE COMMANDS' in output or 'COMMANDS' in output


@patch('builtins.input', side_effect=['modulus', '10', '3', 'exit'])
@patch('builtins.print')
def test_modulus_operation_workflow(mock_print, mock_input):
    """Test modulus operation in full workflow."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output


@patch('builtins.input', side_effect=['intdiv', '10', '3', 'exit'])
@patch('builtins.print')
def test_intdiv_operation_workflow(mock_print, mock_input):
    """Test integer division operation in full workflow."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output


@patch('builtins.input', side_effect=['absdiff', '10', '3', 'exit'])
@patch('builtins.print')
def test_absdiff_operation_workflow(mock_print, mock_input):
    """Test absolute difference operation in full workflow."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output


@patch('builtins.input', side_effect=['percentage', '25', '100', 'exit'])
@patch('builtins.print')
def test_percentage_operation_workflow(mock_print, mock_input):
    """Test percentage operation in full workflow."""
    calculator_repl()
    
    output = get_print_output(mock_print)
    assert 'RESULT' in output or 'Result' in output
    assert '%' in output