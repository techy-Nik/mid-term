########################
# Calculator REPL       #
########################

from decimal import Decimal
import logging

from colorama import init, Fore, Back, Style

from app.calculator import Calculator
from app.exceptions import OperationError, ValidationError
from app.history import AutoSaveObserver, LoggingObserver
from app.operations import OperationFactory
from app.command_pattern import CommandRegistry, OperationCommand, HistoryCommand, FileCommand
from app.help_decorator import HelpMenuBuilder

# Initialize colorama for cross-platform color support
init(autoreset=True)


class CalculatorREPL:
    """Enhanced REPL interface for the calculator with improved organization and full color support."""
    
    OPERATION_COMMANDS = [
        'add', 'subtract', 'multiply', 'divide', 
        'power', 'root', 'modulus', 'intdiv', 
        'percentage', 'absdiff'
    ]
    
    # Color scheme configuration
    COLORS = {
        'header': Fore.CYAN + Style.BRIGHT,
        'success': Fore.GREEN + Style.BRIGHT,
        'error': Fore.RED + Style.BRIGHT,
        'warning': Fore.YELLOW + Style.BRIGHT,
        'info': Fore.BLUE + Style.BRIGHT,
        'prompt': Fore.CYAN + Style.BRIGHT,
        'result': Fore.YELLOW + Style.BRIGHT,
        'highlight': Fore.MAGENTA + Style.BRIGHT,
        'normal': Fore.WHITE,
        'dim': Fore.WHITE + Style.DIM
    }
    
    def __init__(self):
        """Initialize the calculator and register observers."""
        self.calc = Calculator()
        self.calc.add_observer(LoggingObserver())
        self.calc.add_observer(AutoSaveObserver(self.calc))
        self.running = True
        
        # Initialize Command Pattern components
        self.command_registry = CommandRegistry()
        
        # Build dynamic help menu using Decorator Pattern
        self.help_display = (HelpMenuBuilder(self.command_registry)
                           .with_categories()
                           .with_colors()
                           .build())
    
    def display_welcome(self):
        """Display colorful welcome message with ASCII art."""
        c = self.COLORS
        print(f"\n{c['header']}╔{'═' * 50}╗")
        print(f"{c['header']}║{' ' * 50}║")
        print(f"{c['header']}║{Fore.YELLOW}{Style.BRIGHT}{'🧮 ADVANCED CALCULATOR REPL'.center(50)}{c['header']}║")
        print(f"{c['header']}║{Fore.CYAN}{'With Design Patterns & Colors!'.center(50)}{c['header']}║")
        print(f"{c['header']}║{' ' * 50}║")
        print(f"{c['header']}╚{'═' * 50}╝{Style.RESET_ALL}")
        print(f"\n{c['info']}💡 Type {c['highlight']}'help'{c['info']} for available commands")
        print(f"{c['dim']}   Type {c['highlight']}'exit'{c['dim']} to quit the calculator{Style.RESET_ALL}\n")
    
    def display_help(self):
        """Display dynamically generated help menu using Decorator Pattern."""
        help_text = self.help_display.display()
        print(help_text)
    
    def display_history(self):
        """Display calculation history in a beautifully formatted manner with colors."""
        history = self.calc.show_history()
        c = self.COLORS
        
        if not history:
            print(f"\n{c['warning']}╔{'═' * 48}╗") # pragma: no cover
            print(f"{c['warning']}║{'📭 No Calculations in History'.center(48)}║") # pragma: no cover
            print(f"{c['warning']}╚{'═' * 48}╝{Style.RESET_ALL}\n") # pragma: no cover
        else:
            print(f"\n{c['header']}╔{'═' * 60}╗")
            print(f"{c['header']}║{' ' * 60}║")
            print(f"{c['header']}║{c['highlight']}{'📜 CALCULATION HISTORY'.center(60)}{c['header']}║")
            print(f"{c['header']}║{' ' * 60}║")
            print(f"{c['header']}╠{'═' * 60}╣{Style.RESET_ALL}")
            
            for i, entry in enumerate(history, 1):
                # Alternate row colors for better readability
                if i % 2 == 0:
                    num_color = Fore.CYAN
                    entry_color = Fore.WHITE
                else:
                    num_color = Fore.BLUE
                    entry_color = Fore.GREEN
                
                print(f"{c['header']}║ {num_color}{Style.BRIGHT}{i:3d}.{Style.RESET_ALL} {entry_color}{entry:<53}{c['header']}║{Style.RESET_ALL}")
            
            print(f"{c['header']}╚{'═' * 60}╝{Style.RESET_ALL}")
            print(f"{c['info']}Total calculations: {c['highlight']}{len(history)}{Style.RESET_ALL}\n")
    
    def handle_exit(self):
        """Handle exit command with colorful history saving animation."""
        c = self.COLORS
        print(f"\n{c['header']}╔{'═' * 48}╗")
        print(f"{c['header']}║{c['info']}{'🔄 Saving History...'.center(48)}{c['header']}║")
        print(f"{c['header']}╚{'═' * 48}╝{Style.RESET_ALL}")
        
        try:
            self.calc.save_history()
            print(f"{c['success']}✅ History saved successfully!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{c['warning']}⚠️  Warning: Could not save history")
            print(f"{c['error']}   Reason: {e}{Style.RESET_ALL}")
        
        print(f"\n{c['highlight']}╔{'═' * 48}╗")
        print(f"{c['highlight']}║{Fore.YELLOW}{'👋 Thank you for using Calculator!'.center(48)}{c['highlight']}║")
        print(f"{c['highlight']}║{Fore.CYAN}{'Come back soon!'.center(48)}{c['highlight']}║")
        print(f"{c['highlight']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
        
        self.running = False
    
    def handle_history_command(self, command):
        """Handle history-related commands using Command Pattern with colorful feedback."""
        c = self.COLORS
        history_commands = {
            'history': ('show', 'History displayed', '📜'),
            'clear': ('clear', 'History cleared', '🗑️'),
            'undo': ('undo', 'Operation undone', '↩️'),
            'redo': ('redo', 'Operation redone', '↪️')
        }
        
        if command not in history_commands:
            return False
        
        action, success_msg, icon = history_commands[command]
        
        if command == 'history':
            self.display_history()
            return True
        
        # Create and execute history command using Command Pattern
        cmd_info = self.command_registry.get_command_info(command)
        hist_cmd = HistoryCommand(
            self.calc, 
            action, 
            cmd_info['description'] if cmd_info else ''
        )
        
        result = hist_cmd.execute()
        
        if command == 'clear':
            print(f"\n{c['success']}╔{'═' * 48}╗")
            print(f"{c['success']}║{f'{icon} {success_msg}!'.center(48)}║")
            print(f"{c['success']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
        elif command in ['undo', 'redo']:
            if result:
                print(f"\n{c['success']}╔{'═' * 48}╗")
                print(f"{c['success']}║{f'{icon} {success_msg}!'.center(48)}║")
                print(f"{c['success']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
            else:
                print(f"\n{c['warning']}╔{'═' * 48}╗")
                print(f"{c['warning']}║{f'⚠️  Nothing to {command}'.center(48)}║")
                print(f"{c['warning']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
        
        return True
    
    def handle_file_command(self, command):
        """Handle file operations using Command Pattern with colorful status."""
        c = self.COLORS
        if command not in ['save', 'load']:
            return False
        
        cmd_info = self.command_registry.get_command_info(command)
        file_cmd = FileCommand(
            self.calc,
            command,
            cmd_info['description'] if cmd_info else ''
        )
        
        try:
            action_icon = '💾' if command == 'save' else '📂'
            action_msg = 'Saving' if command == 'save' else 'Loading'
            
            print(f"\n{c['info']}{action_icon} {action_msg} history...{Style.RESET_ALL}")
            file_cmd.execute()
            
            action_done = 'saved' if command == 'save' else 'loaded'
            print(f"{c['success']}╔{'═' * 48}╗")
            print(f"{c['success']}║{f'✅ History {action_done} successfully!'.center(48)}║")
            print(f"{c['success']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
        except Exception as e:
            action = 'saving' if command == 'save' else 'loading'
            print(f"{c['error']}╔{'═' * 48}╗")
            print(f"{c['error']}║{f'❌ Error {action} history'.center(48)}║")
            print(f"{c['error']}╚{'═' * 48}╝")
            print(f"{c['warning']}Reason: {e}{Style.RESET_ALL}\n")
        
        return True
    
    def get_operation_inputs(self, command):
        """Get and validate operation inputs with colorful, context-specific prompts."""
        c = self.COLORS
        
        cancel_msg = "(or type 'cancel' to abort)"
        
        print(f"\n{c['header']}╔{'═' * 48}╗")
        print(f"{c['header']}║{c['info']}{'📝 Enter Numbers'.center(48)}{c['header']}║")
        print(f"{c['header']}║{c['dim']}{cancel_msg.center(48)}{c['header']}║")
        print(f"{c['header']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
        
        # Customize prompts based on operation with icons
        prompts = {
            'percentage': ("💯 Value", "📊 Total (base)"),
            'root': ("🔢 Number", "📐 Root degree (n)"),
            'power': ("🔢 Base", "⚡ Exponent"),
            'modulus': ("🔢 Dividend", "➗ Divisor"),
            'intdiv': ("🔢 Dividend", "➗ Divisor"),
            'absdiff': ("🔢 First number", "🔢 Second number"),
            'add': ("➕ First number", "➕ Second number"),
            'subtract': ("➖ First number", "➖ Second number"),
            'multiply': ("✖️  First number", "✖️  Second number"),
            'divide': ("➗ Dividend", "➗ Divisor")
        }
        
        prompt1, prompt2 = prompts.get(command, ("🔢 First number", "🔢 Second number"))
        
        a = input(f"{c['prompt']}{prompt1}: {c['normal']}").strip()
        if a.lower() == 'cancel':
            print(f"\n{c['warning']}🚫 Operation cancelled{Style.RESET_ALL}\n")
            return None, None
        
        b = input(f"{c['prompt']}{prompt2}: {c['normal']}").strip()
        if b.lower() == 'cancel':
            print(f"\n{c['warning']}🚫 Operation cancelled{Style.RESET_ALL}\n")
            return None, None
        
        return a, b
    
    def handle_operation(self, command):
        """Handle arithmetic operations using Command Pattern with beautiful result display."""
        c = self.COLORS
        if command not in self.OPERATION_COMMANDS:
            return False
        
        try:
            a, b = self.get_operation_inputs(command)
            if a is None or b is None:
                return True
            
            # Create and execute operation command using Command Pattern
            cmd_info = self.command_registry.get_command_info(command)
            operation_cmd = OperationCommand(
                self.calc,
                command,
                a,
                b,
                cmd_info['description'] if cmd_info else '',
                cmd_info['category'] if cmd_info else ''
            )
            
            # Show processing message
            print(f"\n{c['info']}⚙️  Calculating...{Style.RESET_ALL}")
            
            result = operation_cmd.execute()
            
            # Normalize Decimal results
            if isinstance(result, Decimal):
                result = result.normalize()
            
            # Display beautiful result box
            print(f"\n{c['success']}╔{'═' * 50}╗")
            print(f"{c['success']}║{' ' * 50}║")
            
            if command == 'percentage':
                result_text = f"✨ RESULT: {result}%"
                padding = 48 - len(str(result))
                print(f"{c['success']}║  {c['highlight']}{result_text}{' ' * (padding - 12)} {c['success']}║")
            else:
                result_str = str(result)
                padding = 38 - len(result_str)
                print(f"{c['success']}║  {c['highlight']}✨ RESULT: {c['result']}{result_str}{' ' * padding} {c['success']}║")
            
            print(f"{c['success']}║{' ' * 50}║")
            print(f"{c['success']}╚{'═' * 50}╝{Style.RESET_ALL}\n")
            
        except (ValidationError, OperationError) as e:
            print(f"\n{c['error']}╔{'═' * 50}╗")
            print(f"{c['error']}║{' ' * 50}║")
            print(f"{c['error']}║  {Fore.WHITE}❌ ERROR{' ' * 40} ║")
            error_msg = str(e)
            # Wrap long error messages
            if len(error_msg) > 44:
                error_msg = error_msg[:44] + "..."
            padding = 46 - len(error_msg)
            print(f"{c['error']}║  {Fore.YELLOW}{error_msg}{' ' * padding} ║")
            print(f"{c['error']}║{' ' * 50}║")
            print(f"{c['error']}╚{'═' * 50}╝{Style.RESET_ALL}\n")
        except Exception as e:
            print(f"\n{c['error']}╔{'═' * 50}╗")
            print(f"{c['error']}║{' ' * 50}║")
            print(f"{c['error']}║  {Fore.WHITE}⚠️  UNEXPECTED ERROR{' ' * 29} ║")
            error_msg = str(e)
            if len(error_msg) > 44:
                error_msg = error_msg[:44] + "..."
            padding = 46 - len(error_msg)
            print(f"{c['error']}║  {Fore.YELLOW}{error_msg}{' ' * padding} ║")
            print(f"{c['error']}║{' ' * 50}║")
            print(f"{c['error']}╚{'═' * 50}╝{Style.RESET_ALL}\n")
        
        return True
    
    def process_command(self, command):
        """Process a single command with colorful feedback."""
        c = self.COLORS
        command = command.lower().strip()
        
        if not command:
            return
        
        if command == 'help':
            self.display_help()
            return
        
        if command == 'exit':
            self.handle_exit()
            return
        
        # Try each command handler
        if self.handle_history_command(command):
            return
        
        if self.handle_file_command(command):
            return
        
        if self.handle_operation(command):
            return
        
        # Unknown command with colorful error
        print(f"\n{c['error']}╔{'═' * 50}╗")
        print(f"{c['error']}║{' ' * 50}║")
        print(f"{c['error']}║  {Fore.WHITE}❓ UNKNOWN COMMAND{' ' * 31} ║")
        cmd_display = command if len(command) <= 40 else command[:40] + "..."
        padding = 46 - len(cmd_display)
        print(f"{c['error']}║  {Fore.YELLOW}'{cmd_display}'{' ' * padding} ║")
        print(f"{c['error']}║{' ' * 50}║")
        print(f"{c['error']}║  {Fore.CYAN}💡 Type 'help' for available commands{' ' * 10} ║")
        print(f"{c['error']}║{' ' * 50}║")
        print(f"{c['error']}╚{'═' * 50}╝{Style.RESET_ALL}\n")
    
    def run(self):
        """Main REPL loop with colorful interface."""
        c = self.COLORS
        self.display_welcome()
        
        while self.running:
            try:
                command = input(f"{c['prompt']}➤ {c['highlight']}Enter command: {c['normal']}")
                self.process_command(command)
                
            except KeyboardInterrupt:
                print(f"\n\n{c['warning']}╔{'═' * 48}╗")
                print(f"{c['warning']}║{Fore.YELLOW}{'🚫 Operation Cancelled'.center(48)}{c['warning']}║")
                print(f"{c['warning']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
                continue
            
            except EOFError:
                print(f"\n\n{c['info']}╔{'═' * 48}╗")
                print(f"{c['info']}║{Fore.YELLOW}{'🔚 Input Terminated'.center(48)}{c['info']}║")
                print(f"{c['info']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
                self.handle_exit()
                break
            
            except Exception as e:
                print(f"\n{c['error']}╔{'═' * 48}╗")
                print(f"{c['error']}║{Fore.WHITE}{'⚠️  ERROR'.center(48)}{c['error']}║")
                print(f"{c['error']}║{Fore.YELLOW}{str(e).center(48)}{c['error']}║")
                print(f"{c['error']}╚{'═' * 48}╝{Style.RESET_ALL}\n")
                continue


def calculator_repl():
    """
    Command-line interface for the calculator.

    Implements a Read-Eval-Print Loop (REPL) that continuously prompts the user
    for commands, processes arithmetic operations, and manages calculation history.
    
    Features:
    - Command Pattern: Operations encapsulated as command objects
    - Decorator Pattern: Dynamic help menu generation
    - Colorama: Full color-coded outputs for enhanced UX
    - Beautiful box drawing with Unicode characters
    - Context-aware prompts with emojis
    
    This is the main entry point that maintains backward compatibility.
    """
    try:
        repl = CalculatorREPL()
        repl.run()
    except Exception as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}╔{'═' * 48}╗")
        print(f"{Fore.RED}{Style.BRIGHT}║{Fore.WHITE}{'💥 FATAL ERROR'.center(48)}{Fore.RED}║")
        print(f"{Fore.RED}{Style.BRIGHT}║{Fore.YELLOW}{str(e).center(48)}{Fore.RED}║")
        print(f"{Fore.RED}{Style.BRIGHT}╚{'═' * 48}╝{Style.RESET_ALL}\n")
        logging.error(f"Fatal error in calculator REPL: {e}")
        raise