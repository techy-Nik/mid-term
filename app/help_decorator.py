########################
# Help Menu Decorator  #
########################

from abc import ABC, abstractmethod
from colorama import Fore, Style


class HelpDisplay(ABC):
    """
    Abstract base class for help display.
    
    Part of the Decorator Pattern implementation for dynamic help menu generation.
    """
    
    @abstractmethod
    def display(self) -> str:
        """
        Display help information.
        
        Returns:
            str: Formatted help text.
        """
        pass # pragma: no cover


class BaseHelp(HelpDisplay):
    """
    Base help display implementation.
    
    Provides the basic structure for help information.
    """
    
    def __init__(self, command_registry):
        """
        Initialize base help.
        
        Args:
            command_registry: Registry containing command information.
        """
        self.command_registry = command_registry
    
    def display(self) -> str:
        """Display basic help structure."""
        output = []
        output.append("\n" + "=" * 50)
        output.append(f"{Fore.CYAN}{Style.BRIGHT}  AVAILABLE COMMANDS{Style.RESET_ALL}")
        output.append("=" * 50)
        return "\n".join(output)


class HelpDecorator(HelpDisplay):
    """
    Abstract decorator for help display.
    
    Implements the Decorator Pattern to add functionality to help display.
    """
    
    def __init__(self, help_display: HelpDisplay):
        """
        Initialize decorator.
        
        Args:
            help_display: HelpDisplay instance to decorate.
        """
        self._help_display = help_display
    
    def display(self) -> str:
        """Display decorated help."""
        return self._help_display.display()


class CategoryDecorator(HelpDecorator):
    """
    Decorator that adds categorized command listings to help display.
    
    Dynamically generates help sections based on registered commands.
    """
    
    def __init__(self, help_display: HelpDisplay, command_registry):
        """
        Initialize category decorator.
        
        Args:
            help_display: HelpDisplay instance to decorate.
            command_registry: Registry containing command information.
        """
        super().__init__(help_display)
        self.command_registry = command_registry
    
    def display(self) -> str:
        """Display help with categorized commands."""
        output = [self._help_display.display()]
        
        # Get commands organized by category
        categorized = self.command_registry.get_commands_by_category()
        
        # Define category icons and colors
        category_styles = {
            'Basic Operations': (Fore.GREEN, '📊'),
            'Advanced Operations': (Fore.YELLOW, '🔢'),
            'History Management': (Fore.BLUE, '📜'),
            'File Operations': (Fore.MAGENTA, '💾'),
            'Other': (Fore.CYAN, '🚪')
        }
        
        # Define preferred category order
        category_order = [
            'Basic Operations',
            'Advanced Operations', 
            'History Management',
            'File Operations',
            'Other'
        ]
        
        # Display commands by category in preferred order
        for category in category_order:
            if category in categorized:
                color, icon = category_styles.get(category, (Fore.WHITE, '•'))
                output.append(f"\n{color}{Style.BRIGHT}{icon} {category}:{Style.RESET_ALL}")
                
                commands = categorized[category]
                for cmd in commands:
                    output.append(f"  {Fore.WHITE}{cmd['name']:<13}{Style.RESET_ALL}- {cmd['description']}")
        
        output.append("=" * 50 + "\n")
        return "\n".join(output)


class ColorDecorator(HelpDecorator):
    """
    Decorator that adds color highlighting to help display.
    
    Enhances visual appearance with color-coded sections.
    """
    
    def display(self) -> str:
        """Display help with enhanced colors."""
        base_output = self._help_display.display()
        # The color is already applied in CategoryDecorator
        # This decorator can add additional styling if needed
        return base_output


class ExamplesDecorator(HelpDecorator):
    """
    Decorator that adds usage examples to help display.
    """
    
    def display(self) -> str:
        """Display help with usage examples."""
        output = [self._help_display.display()]
        
        output.append(f"\n{Fore.CYAN}{Style.BRIGHT}💡 USAGE EXAMPLES:{Style.RESET_ALL}")
        output.append(f"  {Fore.GREEN}add{Style.RESET_ALL}          : Add 10 and 5")
        output.append(f"  {Fore.GREEN}power{Style.RESET_ALL}        : Calculate 2^8")
        output.append(f"  {Fore.GREEN}percentage{Style.RESET_ALL}   : Find what % 25 is of 200")
        output.append(f"  {Fore.GREEN}history{Style.RESET_ALL}      : View all calculations")
        output.append("=" * 50 + "\n")
        
        return "\n".join(output)


class HelpMenuBuilder:
    """
    Builder for constructing decorated help menus.
    
    Provides a fluent interface for adding decorators to the help display.
    """
    
    def __init__(self, command_registry):
        """
        Initialize help menu builder.
        
        Args:
            command_registry: Registry containing command information.
        """
        self.command_registry = command_registry
        self.help_display = BaseHelp(command_registry)
    
    def with_categories(self):
        """Add category organization to help menu."""
        self.help_display = CategoryDecorator(self.help_display, self.command_registry)
        return self
    
    def with_colors(self):
        """Add color enhancement to help menu."""
        self.help_display = ColorDecorator(self.help_display)
        return self
    
    def with_examples(self):
        """Add usage examples to help menu."""
        self.help_display = ExamplesDecorator(self.help_display)
        return self
    
    def build(self) -> HelpDisplay:
        """
        Build and return the decorated help display.
        
        Returns:
            HelpDisplay: Fully decorated help display instance.
        """
        return self.help_display