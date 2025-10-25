########################
# Command Pattern      #
########################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from app.calculator import Calculator
from app.operations import OperationFactory


class Command(ABC):
    """
    Abstract base class for all commands.
    
    Implements the Command Design Pattern to encapsulate requests as objects,
    allowing for parameterization, queuing, and logging of operations.
    """
    
    @abstractmethod
    def execute(self) -> Optional[Decimal]:
        """
        Execute the command.
        
        Returns:
            Optional[Decimal]: Result of the command execution.
        """
        pass # pragma: no cover
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get human-readable description of the command.
        
        Returns:
            str: Description of what the command does.
        """
        pass # pragma: no cover
    
    @abstractmethod
    def get_category(self) -> str:
        """
        Get the category this command belongs to.
        
        Returns:
            str: Category name (e.g., 'Basic Operations', 'Advanced Operations').
        """
        pass # pragma: no cover


class OperationCommand(Command):
    """
    Command for executing calculator operations.
    
    Encapsulates an operation request with its operands and executes it
    through the calculator instance.
    """
    
    def __init__(self, calculator: Calculator, operation_type: str, 
                 a: str, b: str, description: str, category: str):
        """
        Initialize the operation command.
        
        Args:
            calculator: Calculator instance to perform the operation.
            operation_type: Type of operation (e.g., 'add', 'subtract').
            a: First operand as string.
            b: Second operand as string.
            description: Human-readable description of the operation.
            category: Category this operation belongs to.
        """
        self.calculator = calculator
        self.operation_type = operation_type
        self.a = a
        self.b = b
        self.description = description
        self.category = category
    
    def execute(self) -> Optional[Decimal]:
        """
        Execute the operation command.
        
        Returns:
            Optional[Decimal]: Result of the operation.
        """
        operation = OperationFactory.create_operation(self.operation_type)
        self.calculator.set_operation(operation)
        return self.calculator.perform_operation(self.a, self.b)
    
    def get_description(self) -> str:
        """Get command description."""
        return self.description
    
    def get_category(self) -> str:
        """Get command category."""
        return self.category


class HistoryCommand(Command):
    """
    Command for history management operations.
    """
    
    def __init__(self, calculator: Calculator, action: str, description: str):
        """
        Initialize history command.
        
        Args:
            calculator: Calculator instance.
            action: History action ('show', 'clear', 'undo', 'redo').
            description: Human-readable description.
        """
        self.calculator = calculator
        self.action = action
        self.description = description
    
    def execute(self) -> Optional[Decimal]:
        """Execute the history command."""
        if self.action == 'show':
            return self.calculator.show_history()
        elif self.action == 'clear':
            self.calculator.clear_history()
        elif self.action == 'undo':
            return self.calculator.undo()
        elif self.action == 'redo':
            return self.calculator.redo()
        return None
    
    def get_description(self) -> str:
        """Get command description."""
        return self.description
    
    def get_category(self) -> str:
        """Get command category."""
        return "History Management"


class FileCommand(Command):
    """
    Command for file operations.
    """
    
    def __init__(self, calculator: Calculator, action: str, description: str):
        """
        Initialize file command.
        
        Args:
            calculator: Calculator instance.
            action: File action ('save', 'load').
            description: Human-readable description.
        """
        self.calculator = calculator
        self.action = action
        self.description = description
    
    def execute(self) -> Optional[Decimal]:
        """Execute the file command."""
        if self.action == 'save':
            self.calculator.save_history()
        elif self.action == 'load':
            self.calculator.load_history()
        return None
    
    def get_description(self) -> str:
        """Get command description."""
        return self.description
    
    def get_category(self) -> str:
        """Get command category."""
        return "File Operations"


class CommandRegistry:
    """
    Registry for managing available commands.
    
    Provides a central place to register and retrieve commands,
    supporting the dynamic help menu generation.
    """
    
    def __init__(self):
        """Initialize the command registry."""
        self.commands = {}
        self._register_default_commands()
    
    def _register_default_commands(self):
        """Register default command metadata."""
        # Basic Operations
        self.register_command_metadata('add', 'Add two numbers', 'Basic Operations')
        self.register_command_metadata('subtract', 'Subtract second number from first', 'Basic Operations')
        self.register_command_metadata('multiply', 'Multiply two numbers', 'Basic Operations')
        self.register_command_metadata('divide', 'Divide first number by second', 'Basic Operations')
        
        # Advanced Operations
        self.register_command_metadata('power', 'Raise first number to second power', 'Advanced Operations')
        self.register_command_metadata('root', 'Calculate nth root of first number', 'Advanced Operations')
        self.register_command_metadata('modulus', 'Calculate remainder of division', 'Advanced Operations')
        self.register_command_metadata('intdiv', 'Integer division (quotient only)', 'Advanced Operations')
        self.register_command_metadata('percentage', 'Calculate percentage (a/b × 100)', 'Advanced Operations')
        self.register_command_metadata('absdiff', 'Absolute difference between numbers', 'Advanced Operations')
        
        # History Management
        self.register_command_metadata('history', 'Show calculation history', 'History Management')
        self.register_command_metadata('clear', 'Clear calculation history', 'History Management')
        self.register_command_metadata('undo', 'Undo the last calculation', 'History Management')
        self.register_command_metadata('redo', 'Redo the last undone calculation', 'History Management')
        
        # File Operations
        self.register_command_metadata('save', 'Save calculation history to file', 'File Operations')
        self.register_command_metadata('load', 'Load calculation history from file', 'File Operations')
        
        # Other
        self.register_command_metadata('help', 'Show this help message', 'Other')
        self.register_command_metadata('exit', 'Exit the calculator', 'Other')
    
    def register_command_metadata(self, name: str, description: str, category: str):
        """
        Register command metadata.
        
        Args:
            name: Command name.
            description: Command description.
            category: Command category.
        """
        self.commands[name] = {
            'description': description,
            'category': category
        }
    
    def get_commands_by_category(self) -> dict:
        """
        Get commands organized by category.
        
        Returns:
            dict: Dictionary with categories as keys and lists of commands as values.
        """
        categorized = {}
        for cmd_name, metadata in self.commands.items():
            category = metadata['category']
            if category not in categorized:
                categorized[category] = []
            categorized[category].append({
                'name': cmd_name,
                'description': metadata['description']
            })
        return categorized
    
    def get_command_info(self, name: str) -> dict:
        """
        Get information about a specific command.
        
        Args:
            name: Command name.
            
        Returns:
            dict: Command metadata or None if not found.
        """
        return self.commands.get(name)