"""
Tests for Help Menu Decorator implementation.
"""

import pytest
from unittest.mock import Mock, MagicMock
from colorama import Fore, Style
from app.help_decorator import (
    HelpDisplay,
    BaseHelp,
    HelpDecorator,
    CategoryDecorator,
    ColorDecorator,
    ExamplesDecorator,
    HelpMenuBuilder
)
from app.command_pattern import CommandRegistry


class TestHelpDisplay:
    """Test the abstract HelpDisplay base class."""
    
    def test_help_display_is_abstract(self):
        """Test that HelpDisplay cannot be instantiated directly."""
        with pytest.raises(TypeError):
            HelpDisplay()
    
    def test_help_display_requires_display_method(self):
        """Test that subclasses must implement display method."""
        class IncompleteHelp(HelpDisplay):
            pass
        
        with pytest.raises(TypeError):
            IncompleteHelp()


class TestBaseHelp:
    """Test BaseHelp class."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create a mock command registry."""
        return Mock(spec=CommandRegistry)
    
    def test_base_help_initialization(self, mock_registry):
        """Test BaseHelp initialization."""
        base_help = BaseHelp(mock_registry)
        assert base_help.command_registry == mock_registry
    
    def test_base_help_display(self, mock_registry):
        """Test BaseHelp display method."""
        base_help = BaseHelp(mock_registry)
        output = base_help.display()
        
        assert isinstance(output, str)
        assert "AVAILABLE COMMANDS" in output
        assert "=" * 50 in output
        assert Fore.CYAN in output
        assert Style.BRIGHT in output
        assert Style.RESET_ALL in output
    
    def test_base_help_display_structure(self, mock_registry):
        """Test that base help has proper structure."""
        base_help = BaseHelp(mock_registry)
        output = base_help.display()
        lines = output.split('\n')
        
        # Should have header with separators
        assert any("=" * 50 in line for line in lines)
        assert any("AVAILABLE COMMANDS" in line for line in lines)


class TestHelpDecorator:
    """Test HelpDecorator abstract class."""
    
    def test_help_decorator_initialization(self):
        """Test HelpDecorator initialization."""
        mock_help = Mock(spec=HelpDisplay)
        mock_help.display.return_value = "test output"
        
        decorator = HelpDecorator(mock_help)
        assert decorator._help_display == mock_help
    
    def test_help_decorator_display(self):
        """Test HelpDecorator display delegates to wrapped instance."""
        mock_help = Mock(spec=HelpDisplay)
        mock_help.display.return_value = "test output"
        
        decorator = HelpDecorator(mock_help)
        result = decorator.display()
        
        assert result == "test output"
        mock_help.display.assert_called_once()


class TestCategoryDecorator:
    """Test CategoryDecorator class."""
    
    @pytest.fixture
    def command_registry(self):
        """Create a real command registry with test data."""
        registry = CommandRegistry()
        return registry
    
    @pytest.fixture
    def base_help(self, command_registry):
        """Create a base help instance."""
        return BaseHelp(command_registry)
    
    def test_category_decorator_initialization(self, base_help, command_registry):
        """Test CategoryDecorator initialization."""
        decorator = CategoryDecorator(base_help, command_registry)
        assert decorator._help_display == base_help
        assert decorator.command_registry == command_registry
    
    def test_category_decorator_display(self, base_help, command_registry):
        """Test CategoryDecorator display method."""
        decorator = CategoryDecorator(base_help, command_registry)
        output = decorator.display()
        
        assert isinstance(output, str)
        assert "AVAILABLE COMMANDS" in output
        assert "Basic Operations" in output
        assert "Advanced Operations" in output
        assert "History Management" in output
        assert "File Operations" in output
        assert "Other" in output
    
    def test_category_decorator_includes_commands(self, base_help, command_registry):
        """Test that CategoryDecorator includes command names."""
        decorator = CategoryDecorator(base_help, command_registry)
        output = decorator.display()
        
        # Check for basic operation commands
        assert "add" in output
        assert "subtract" in output
        assert "multiply" in output
        assert "divide" in output
        
        # Check for advanced operations
        assert "power" in output
        assert "root" in output
        
        # Check for history commands
        assert "history" in output
        assert "undo" in output
        
        # Check for file commands
        assert "save" in output
        assert "load" in output
    
    def test_category_decorator_includes_descriptions(self, base_help, command_registry):
        """Test that CategoryDecorator includes command descriptions."""
        decorator = CategoryDecorator(base_help, command_registry)
        output = decorator.display()
        
        assert "Add two numbers" in output
        assert "Subtract second number from first" in output
        assert "Show calculation history" in output
    
    def test_category_decorator_has_icons(self, base_help, command_registry):
        """Test that CategoryDecorator includes category icons."""
        decorator = CategoryDecorator(base_help, command_registry)
        output = decorator.display()
        
        # Check for emoji icons
        assert "📊" in output  # Basic Operations
        assert "🔢" in output  # Advanced Operations
        assert "📜" in output  # History Management
        assert "💾" in output  # File Operations
        assert "🚪" in output  # Other
    
    def test_category_decorator_has_colors(self, base_help, command_registry):
        """Test that CategoryDecorator includes color codes."""
        decorator = CategoryDecorator(base_help, command_registry)
        output = decorator.display()
        
        assert Fore.GREEN in output    # Basic Operations
        assert Fore.YELLOW in output   # Advanced Operations
        assert Fore.BLUE in output     # History Management
        assert Fore.MAGENTA in output  # File Operations
        assert Fore.CYAN in output     # Other
    
    def test_category_decorator_order(self, base_help, command_registry):
        """Test that categories appear in the correct order."""
        decorator = CategoryDecorator(base_help, command_registry)
        output = decorator.display()
        
        # Find positions of each category
        basic_pos = output.find("Basic Operations")
        advanced_pos = output.find("Advanced Operations")
        history_pos = output.find("History Management")
        file_pos = output.find("File Operations")
        other_pos = output.find("Other")
        
        # Verify order
        assert basic_pos < advanced_pos
        assert advanced_pos < history_pos
        assert history_pos < file_pos
        assert file_pos < other_pos
    
    def test_category_decorator_with_empty_category(self, base_help):
        """Test CategoryDecorator with a registry that has empty categories."""
        mock_registry = Mock(spec=CommandRegistry)
        mock_registry.get_commands_by_category.return_value = {
            'Basic Operations': [
                {'name': 'add', 'description': 'Add two numbers'}
            ]
        }
        
        decorator = CategoryDecorator(base_help, mock_registry)
        output = decorator.display()
        
        assert "Basic Operations" in output
        assert "add" in output
        # Other categories should not appear since they're not in the mock


class TestColorDecorator:
    """Test ColorDecorator class."""
    
    @pytest.fixture
    def mock_help(self):
        """Create a mock help display."""
        mock = Mock(spec=HelpDisplay)
        mock.display.return_value = "test output with colors"
        return mock
    
    def test_color_decorator_initialization(self, mock_help):
        """Test ColorDecorator initialization."""
        decorator = ColorDecorator(mock_help)
        assert decorator._help_display == mock_help
    
    def test_color_decorator_display(self, mock_help):
        """Test ColorDecorator display method."""
        decorator = ColorDecorator(mock_help)
        output = decorator.display()
        
        assert output == "test output with colors"
        mock_help.display.assert_called_once()
    
    def test_color_decorator_passes_through(self):
        """Test that ColorDecorator passes through the base output."""
        registry = CommandRegistry()
        base_help = BaseHelp(registry)
        
        decorator = ColorDecorator(base_help)
        output = decorator.display()
        
        # Should contain the base help output
        assert "AVAILABLE COMMANDS" in output


class TestExamplesDecorator:
    """Test ExamplesDecorator class."""
    
    @pytest.fixture
    def mock_help(self):
        """Create a mock help display."""
        mock = Mock(spec=HelpDisplay)
        mock.display.return_value = "base output"
        return mock
    
    def test_examples_decorator_initialization(self, mock_help):
        """Test ExamplesDecorator initialization."""
        decorator = ExamplesDecorator(mock_help)
        assert decorator._help_display == mock_help
    
    def test_examples_decorator_display(self, mock_help):
        """Test ExamplesDecorator display method."""
        decorator = ExamplesDecorator(mock_help)
        output = decorator.display()
        
        assert isinstance(output, str)
        assert "base output" in output
        assert "USAGE EXAMPLES" in output
        mock_help.display.assert_called_once()
    
    def test_examples_decorator_includes_examples(self, mock_help):
        """Test that ExamplesDecorator includes usage examples."""
        decorator = ExamplesDecorator(mock_help)
        output = decorator.display()
        
        assert "add" in output
        assert "Add 10 and 5" in output
        assert "power" in output
        assert "Calculate 2^8" in output
        assert "percentage" in output
        assert "Find what % 25 is of 200" in output
        assert "history" in output
        assert "View all calculations" in output
    
    def test_examples_decorator_has_formatting(self, mock_help):
        """Test that ExamplesDecorator includes proper formatting."""
        decorator = ExamplesDecorator(mock_help)
        output = decorator.display()
        
        assert Fore.CYAN in output
        assert Style.BRIGHT in output
        assert Style.RESET_ALL in output
        assert "💡" in output  # Example icon
        assert "=" * 50 in output
    
    def test_examples_decorator_with_real_base(self):
        """Test ExamplesDecorator with real BaseHelp."""
        registry = CommandRegistry()
        base_help = BaseHelp(registry)
        
        decorator = ExamplesDecorator(base_help)
        output = decorator.display()
        
        assert "AVAILABLE COMMANDS" in output
        assert "USAGE EXAMPLES" in output


class TestHelpMenuBuilder:
    """Test HelpMenuBuilder class."""
    
    @pytest.fixture
    def command_registry(self):
        """Create a command registry."""
        return CommandRegistry()
    
    def test_help_menu_builder_initialization(self, command_registry):
        """Test HelpMenuBuilder initialization."""
        builder = HelpMenuBuilder(command_registry)
        
        assert builder.command_registry == command_registry
        assert isinstance(builder.help_display, BaseHelp)
    
    def test_help_menu_builder_with_categories(self, command_registry):
        """Test adding categories to builder."""
        builder = HelpMenuBuilder(command_registry)
        result = builder.with_categories()
        
        assert result == builder  # Fluent interface
        assert isinstance(builder.help_display, CategoryDecorator)
    
    def test_help_menu_builder_with_colors(self, command_registry):
        """Test adding colors to builder."""
        builder = HelpMenuBuilder(command_registry)
        result = builder.with_colors()
        
        assert result == builder  # Fluent interface
        assert isinstance(builder.help_display, ColorDecorator)
    
    def test_help_menu_builder_with_examples(self, command_registry):
        """Test adding examples to builder."""
        builder = HelpMenuBuilder(command_registry)
        result = builder.with_examples()
        
        assert result == builder  # Fluent interface
        assert isinstance(builder.help_display, ExamplesDecorator)
    
    def test_help_menu_builder_build(self, command_registry):
        """Test building the help display."""
        builder = HelpMenuBuilder(command_registry)
        help_display = builder.build()
        
        assert isinstance(help_display, HelpDisplay)
    
    def test_help_menu_builder_fluent_interface(self, command_registry):
        """Test fluent interface chain."""
        builder = HelpMenuBuilder(command_registry)
        help_display = builder.with_categories().with_colors().with_examples().build()
        
        assert isinstance(help_display, HelpDisplay)
    
    def test_help_menu_builder_full_chain(self, command_registry):
        """Test complete builder chain produces correct output."""
        builder = HelpMenuBuilder(command_registry)
        help_display = builder.with_categories().with_examples().build()
        
        output = help_display.display()
        
        # Should have all components
        assert "AVAILABLE COMMANDS" in output
        assert "Basic Operations" in output
        assert "USAGE EXAMPLES" in output
        assert "add" in output
    
    def test_help_menu_builder_decorator_stacking(self, command_registry):
        """Test that decorators stack correctly."""
        builder = HelpMenuBuilder(command_registry)
        
        # Start with base
        assert isinstance(builder.help_display, BaseHelp)
        
        # Add categories
        builder.with_categories()
        assert isinstance(builder.help_display, CategoryDecorator)
        
        # Add examples on top
        builder.with_examples()
        assert isinstance(builder.help_display, ExamplesDecorator)
        
        # The wrapped display should still be there
        output = builder.build().display()
        assert "AVAILABLE COMMANDS" in output
        assert "Basic Operations" in output
        assert "USAGE EXAMPLES" in output
    
    def test_help_menu_builder_minimal_build(self, command_registry):
        """Test building with minimal decorators."""
        builder = HelpMenuBuilder(command_registry)
        help_display = builder.build()
        
        output = help_display.display()
        
        # Should only have base help
        assert "AVAILABLE COMMANDS" in output
        # Should not have category details since no decorator added
        assert "Basic Operations" not in output
    
    def test_help_menu_builder_categories_only(self, command_registry):
        """Test building with only categories decorator."""
        builder = HelpMenuBuilder(command_registry)
        help_display = builder.with_categories().build()
        
        output = help_display.display()
        
        assert "AVAILABLE COMMANDS" in output
        assert "Basic Operations" in output
        assert "add" in output
        # Should not have examples
        assert "USAGE EXAMPLES" not in output
    
    def test_help_menu_builder_examples_only(self, command_registry):
        """Test building with only examples decorator."""
        builder = HelpMenuBuilder(command_registry)
        help_display = builder.with_examples().build()
        
        output = help_display.display()
        
        assert "AVAILABLE COMMANDS" in output
        assert "USAGE EXAMPLES" in output
        # May not have detailed categories since CategoryDecorator not added


class TestIntegration:
    """Integration tests for the complete help system."""
    
    def test_complete_help_menu(self):
        """Test creating a complete help menu with all features."""
        registry = CommandRegistry()
        builder = HelpMenuBuilder(registry)
        
        help_display = (builder
                       .with_categories()
                       .with_colors()
                       .with_examples()
                       .build())
        
        output = help_display.display()
        
        # Verify all major components
        assert "AVAILABLE COMMANDS" in output
        assert "Basic Operations" in output
        assert "Advanced Operations" in output
        assert "History Management" in output
        assert "File Operations" in output
        assert "Other" in output
        assert "USAGE EXAMPLES" in output
        
        # Verify commands are present
        assert "add" in output
        assert "power" in output
        assert "history" in output
        assert "save" in output
        
        # Verify formatting
        assert "📊" in output
        assert "🔢" in output
        assert "💡" in output
    
    def test_decorator_pattern_layering(self):
        """Test that decorator pattern correctly layers functionality."""
        registry = CommandRegistry()
        base = BaseHelp(registry)
        
        # Layer 1: Add categories
        with_categories = CategoryDecorator(base, registry)
        output1 = with_categories.display()
        assert "Basic Operations" in output1
        
        # Layer 2: Add examples on top of categories
        with_examples = ExamplesDecorator(with_categories)
        output2 = with_examples.display()
        assert "Basic Operations" in output2
        assert "USAGE EXAMPLES" in output2
        
        # Layer 3: Add colors (though it's pass-through)
        with_colors = ColorDecorator(with_examples)
        output3 = with_colors.display()
        assert "Basic Operations" in output3
        assert "USAGE EXAMPLES" in output3