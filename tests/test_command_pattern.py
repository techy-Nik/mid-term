"""
Tests for Command Pattern implementation.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from app.command_pattern import (
    Command,
    OperationCommand,
    HistoryCommand,
    FileCommand,
    CommandRegistry
)
from app.calculator import Calculator
from app.operations import Addition


class TestCommand:
    """Test the abstract Command base class."""
    
    def test_command_is_abstract(self):
        """Test that Command cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Command()
    
    def test_command_requires_execute_method(self):
        """Test that subclasses must implement execute method."""
        class IncompleteCommand(Command):
            def get_description(self):
                return "test"
            def get_category(self):
                return "test"
        
        with pytest.raises(TypeError):
            IncompleteCommand()
    
    def test_command_requires_get_description_method(self):
        """Test that subclasses must implement get_description method."""
        class IncompleteCommand(Command):
            def execute(self):
                pass
            def get_category(self):
                return "test"
        
        with pytest.raises(TypeError):
            IncompleteCommand()
    
    def test_command_requires_get_category_method(self):
        """Test that subclasses must implement get_category method."""
        class IncompleteCommand(Command):
            def execute(self):
                pass
            def get_description(self):
                return "test"
        
        with pytest.raises(TypeError):
            IncompleteCommand()


class TestOperationCommand:
    """Test OperationCommand class."""
    
    @pytest.fixture
    def mock_calculator(self):
        """Create a mock calculator."""
        return Mock(spec=Calculator)
    
    def test_operation_command_initialization(self, mock_calculator):
        """Test OperationCommand initialization."""
        cmd = OperationCommand(
            mock_calculator,
            'add',
            '5',
            '3',
            'Add two numbers',
            'Basic Operations'
        )
        
        assert cmd.calculator == mock_calculator
        assert cmd.operation_type == 'add'
        assert cmd.a == '5'
        assert cmd.b == '3'
        assert cmd.description == 'Add two numbers'
        assert cmd.category == 'Basic Operations'
    
    def test_operation_command_execute(self, mock_calculator):
        """Test OperationCommand execute method."""
        mock_calculator.perform_operation.return_value = Decimal('8')
        
        cmd = OperationCommand(
            mock_calculator,
            'add',
            '5',
            '3',
            'Add two numbers',
            'Basic Operations'
        )
        
        result = cmd.execute()
        
        assert result == Decimal('8')
        mock_calculator.set_operation.assert_called_once()
        mock_calculator.perform_operation.assert_called_once_with('5', '3')
    
    def test_operation_command_get_description(self, mock_calculator):
        """Test get_description method."""
        cmd = OperationCommand(
            mock_calculator,
            'add',
            '5',
            '3',
            'Add two numbers',
            'Basic Operations'
        )
        
        assert cmd.get_description() == 'Add two numbers'
    
    def test_operation_command_get_category(self, mock_calculator):
        """Test get_category method."""
        cmd = OperationCommand(
            mock_calculator,
            'multiply',
            '4',
            '7',
            'Multiply two numbers',
            'Basic Operations'
        )
        
        assert cmd.get_category() == 'Basic Operations'


class TestHistoryCommand:
    """Test HistoryCommand class."""
    
    @pytest.fixture
    def mock_calculator(self):
        """Create a mock calculator."""
        return Mock(spec=Calculator)
    
    def test_history_command_initialization(self, mock_calculator):
        """Test HistoryCommand initialization."""
        cmd = HistoryCommand(
            mock_calculator,
            'show',
            'Show calculation history'
        )
        
        assert cmd.calculator == mock_calculator
        assert cmd.action == 'show'
        assert cmd.description == 'Show calculation history'
    
    def test_history_command_show_action(self, mock_calculator):
        """Test history command with 'show' action."""
        mock_calculator.show_history.return_value = None
        
        cmd = HistoryCommand(mock_calculator, 'show', 'Show history')
        result = cmd.execute()
        
        mock_calculator.show_history.assert_called_once()
        assert result is None
    
    def test_history_command_clear_action(self, mock_calculator):
        """Test history command with 'clear' action."""
        cmd = HistoryCommand(mock_calculator, 'clear', 'Clear history')
        result = cmd.execute()
        
        mock_calculator.clear_history.assert_called_once()
        assert result is None
    
    def test_history_command_undo_action(self, mock_calculator):
        """Test history command with 'undo' action."""
        mock_calculator.undo.return_value = Decimal('10')
        
        cmd = HistoryCommand(mock_calculator, 'undo', 'Undo last calculation')
        result = cmd.execute()
        
        mock_calculator.undo.assert_called_once()
        assert result == Decimal('10')
    
    def test_history_command_redo_action(self, mock_calculator):
        """Test history command with 'redo' action."""
        mock_calculator.redo.return_value = Decimal('15')
        
        cmd = HistoryCommand(mock_calculator, 'redo', 'Redo calculation')
        result = cmd.execute()
        
        mock_calculator.redo.assert_called_once()
        assert result == Decimal('15')
    
    def test_history_command_invalid_action(self, mock_calculator):
        """Test history command with invalid action."""
        cmd = HistoryCommand(mock_calculator, 'invalid', 'Invalid action')
        result = cmd.execute()
        
        assert result is None
    
    def test_history_command_get_description(self, mock_calculator):
        """Test get_description method."""
        cmd = HistoryCommand(mock_calculator, 'show', 'Show history')
        assert cmd.get_description() == 'Show history'
    
    def test_history_command_get_category(self, mock_calculator):
        """Test get_category method."""
        cmd = HistoryCommand(mock_calculator, 'show', 'Show history')
        assert cmd.get_category() == 'History Management'


class TestFileCommand:
    """Test FileCommand class."""
    
    @pytest.fixture
    def mock_calculator(self):
        """Create a mock calculator."""
        return Mock(spec=Calculator)
    
    def test_file_command_initialization(self, mock_calculator):
        """Test FileCommand initialization."""
        cmd = FileCommand(
            mock_calculator,
            'save',
            'Save history to file'
        )
        
        assert cmd.calculator == mock_calculator
        assert cmd.action == 'save'
        assert cmd.description == 'Save history to file'
    
    def test_file_command_save_action(self, mock_calculator):
        """Test file command with 'save' action."""
        cmd = FileCommand(mock_calculator, 'save', 'Save history')
        result = cmd.execute()
        
        mock_calculator.save_history.assert_called_once()
        assert result is None
    
    def test_file_command_load_action(self, mock_calculator):
        """Test file command with 'load' action."""
        cmd = FileCommand(mock_calculator, 'load', 'Load history')
        result = cmd.execute()
        
        mock_calculator.load_history.assert_called_once()
        assert result is None
    
    def test_file_command_invalid_action(self, mock_calculator):
        """Test file command with invalid action."""
        cmd = FileCommand(mock_calculator, 'invalid', 'Invalid action')
        result = cmd.execute()
        
        assert result is None
    
    def test_file_command_get_description(self, mock_calculator):
        """Test get_description method."""
        cmd = FileCommand(mock_calculator, 'save', 'Save to file')
        assert cmd.get_description() == 'Save to file'
    
    def test_file_command_get_category(self, mock_calculator):
        """Test get_category method."""
        cmd = FileCommand(mock_calculator, 'load', 'Load from file')
        assert cmd.get_category() == 'File Operations'


class TestCommandRegistry:
    """Test CommandRegistry class."""
    
    def test_command_registry_initialization(self):
        """Test that registry initializes with default commands."""
        registry = CommandRegistry()
        
        assert len(registry.commands) > 0
        assert 'add' in registry.commands
        assert 'subtract' in registry.commands
        assert 'help' in registry.commands
    
    def test_register_command_metadata(self):
        """Test registering new command metadata."""
        registry = CommandRegistry()
        
        registry.register_command_metadata(
            'custom',
            'Custom command',
            'Custom Category'
        )
        
        assert 'custom' in registry.commands
        assert registry.commands['custom']['description'] == 'Custom command'
        assert registry.commands['custom']['category'] == 'Custom Category'
    
    def test_get_commands_by_category(self):
        """Test retrieving commands organized by category."""
        registry = CommandRegistry()
        categorized = registry.get_commands_by_category()
        
        assert 'Basic Operations' in categorized
        assert 'Advanced Operations' in categorized
        assert 'History Management' in categorized
        assert 'File Operations' in categorized
        assert 'Other' in categorized
        
        # Check that commands are in the right categories
        basic_commands = [cmd['name'] for cmd in categorized['Basic Operations']]
        assert 'add' in basic_commands
        assert 'subtract' in basic_commands
        assert 'multiply' in basic_commands
        assert 'divide' in basic_commands
    
    def test_get_command_info_existing_command(self):
        """Test getting info for existing command."""
        registry = CommandRegistry()
        info = registry.get_command_info('add')
        
        assert info is not None
        assert info['description'] == 'Add two numbers'
        assert info['category'] == 'Basic Operations'
    
    def test_get_command_info_nonexistent_command(self):
        """Test getting info for non-existent command."""
        registry = CommandRegistry()
        info = registry.get_command_info('nonexistent')
        
        assert info is None
    
    def test_all_default_commands_registered(self):
        """Test that all default commands are registered."""
        registry = CommandRegistry()
        
        expected_commands = [
            'add', 'subtract', 'multiply', 'divide',
            'power', 'root', 'modulus', 'intdiv', 'percentage', 'absdiff',
            'history', 'clear', 'undo', 'redo',
            'save', 'load',
            'help', 'exit'
        ]
        
        for cmd in expected_commands:
            assert cmd in registry.commands
    
    def test_command_categories_structure(self):
        """Test the structure of categorized commands."""
        registry = CommandRegistry()
        categorized = registry.get_commands_by_category()
        
        # Each category should have a list of command dictionaries
        for category, commands in categorized.items():
            assert isinstance(commands, list)
            for cmd in commands:
                assert 'name' in cmd
                assert 'description' in cmd
    
    def test_advanced_operations_category(self):
        """Test that advanced operations are properly categorized."""
        registry = CommandRegistry()
        categorized = registry.get_commands_by_category()
        
        advanced_commands = [cmd['name'] for cmd in categorized['Advanced Operations']]
        assert 'power' in advanced_commands
        assert 'root' in advanced_commands
        assert 'modulus' in advanced_commands
        assert 'intdiv' in advanced_commands
        assert 'percentage' in advanced_commands
        assert 'absdiff' in advanced_commands
    
    def test_history_management_category(self):
        """Test that history commands are properly categorized."""
        registry = CommandRegistry()
        categorized = registry.get_commands_by_category()
        
        history_commands = [cmd['name'] for cmd in categorized['History Management']]
        assert 'history' in history_commands
        assert 'clear' in history_commands
        assert 'undo' in history_commands
        assert 'redo' in history_commands
    
    def test_file_operations_category(self):
        """Test that file commands are properly categorized."""
        registry = CommandRegistry()
        categorized = registry.get_commands_by_category()
        
        file_commands = [cmd['name'] for cmd in categorized['File Operations']]
        assert 'save' in file_commands
        assert 'load' in file_commands
    
    def test_other_category(self):
        """Test that other commands are properly categorized."""
        registry = CommandRegistry()
        categorized = registry.get_commands_by_category()
        
        other_commands = [cmd['name'] for cmd in categorized['Other']]
        assert 'help' in other_commands
        assert 'exit' in other_commands