"""
Interactive CLI interface for Stackmate.
"""

from rich.console import Console
from rich.prompt import Prompt
from rich.spinner import Spinner
import os
import asyncio
import sys
import termios
import tty

from .templates import TEMPLATES, AVAILABLE_STACKS
from .ai import StackAnalyzer

console = Console()

class InlineSelector:
    def __init__(self, options):
        self.options = options
        self.current_index = 0
        self.selected = None
        self.first_print = True

    def _get_char(self):
        """Get a single character from stdin."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _print_options(self):
        """Print all options with the current selection highlighted."""
        # Move cursor to the start of the options list
        if not self.first_print:
            # Move up by the number of options
            sys.stdout.write(f"\033[{len(self.options)}A")
        else:
            self.first_print = False
        
        # Clear all lines from cursor down
        sys.stdout.write("\033[J")
        
        # Print options
        for i, (key, label) in enumerate(self.options):
            if i == self.current_index:
                # Bold cyan for selected item
                sys.stdout.write(f"\033[1;36m> {label}\033[0m\n")
            else:
                sys.stdout.write(f"  {label}\n")
        sys.stdout.flush()

    def select(self):
        """Run the selection interface."""
        self._print_options()
        
        while True:
            char = self._get_char()
            
            if char == '\x1b':  # Arrow keys
                next_char = self._get_char()
                if next_char == '[':
                    last_char = self._get_char()
                    if last_char == 'A':  # Up arrow
                        self.current_index = (self.current_index - 1) % len(self.options)
                        self._print_options()
                    elif last_char == 'B':  # Down arrow
                        self.current_index = (self.current_index + 1) % len(self.options)
                        self._print_options()
            elif char == '\r':  # Enter
                self.selected = self.options[self.current_index][0]
                sys.stdout.write('\n')
                return self.selected
            elif char == '\x03':  # Ctrl+C
                sys.stdout.write('\n')
                return None

def display_header() -> None:
    """Display the application header."""
    console.print("\n[bold cyan]Stackmate - AI-Powered Tech Stack Generator[/]")
    console.print("[dim]Create modern web applications with best practices[/]\n")
    console.print("[dim]Use ↑/↓ arrows to select a stack, Enter to confirm[/]\n")

async def create_project(project_name: str, stack_name: str, description: str = None) -> None:
    """Create a new project with the selected stack."""
    try:
        if stack_name == "custom":
            if not description:
                raise ValueError("Description is required for custom stack")
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                console.print("\n[red]Error:[/] GEMINI_API_KEY environment variable not set")
                console.print("[yellow]Please set your API key:[/]")
                console.print("export GEMINI_API_KEY=your-api-key")
                return
            
            analyzer = StackAnalyzer(api_key)
            with console.status("[bold yellow]Analyzing project requirements...", spinner="dots"):
                template_name, analysis = await analyzer.analyze_requirements(description)
            
            # Display analysis results
            console.print("\n[bold cyan]AI Analysis Results[/]")
            
            if "stack" in analysis:
                console.print("\n[bold]Recommended Stack:[/]")
                for key, value in analysis["stack"].items():
                    if isinstance(value, list):
                        console.print(f"[green]• {key}:[/] {', '.join(value)}")
                    else:
                        console.print(f"[green]• {key}:[/] {value}")
            
            if "reasoning" in analysis:
                console.print("\n[bold]Reasoning:[/]")
                for key, value in analysis["reasoning"].items():
                    console.print(f"[blue]• {key}:[/] {value}")
            
            if "additional_considerations" in analysis:
                console.print("\n[bold]Additional Considerations:[/]")
                for consideration in analysis["additional_considerations"]:
                    console.print(f"[yellow]• {consideration}")
            
            if not Prompt.ask("\n[bold]Would you like to proceed with this stack?[/]", choices=["y", "n"], default="y") == "y":
                console.print("\n[yellow]Operation cancelled[/]")
                return
            
            with console.status(f"[bold green]Creating project: {project_name}...", spinner="dots"):
                template = TEMPLATES[stack_name](project_name, analysis)
                await template.generate()
        else:
            with console.status(f"[bold green]Creating project: {project_name}...", spinner="dots"):
                template_class = TEMPLATES[stack_name]
                template = template_class(project_name)
                await template.generate()
        
        console.print(f"\n[bold green]✨ Project {project_name} created successfully![/]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/] {str(e)}")

def run() -> None:
    """Run the interactive CLI."""
    display_header()

    # Get project name
    while True:
        project_name = Prompt.ask("[cyan]Project name")
        if not project_name:
            console.print("[yellow]Please enter a project name[/]")
            continue
        if os.path.exists(project_name):
            console.print(f"[yellow]Directory '{project_name}' already exists[/]")
            continue
        break

    # Stack descriptions
    stack_descriptions = {
        'modern-react': 'Next.js + Tailwind + Shadcn',
        't3': 'Full-Stack T3 Stack (Next.js, tRPC, Prisma, NextAuth)',
        'enterprise-react': 'Enterprise-grade React setup',
        'jamstack-blog': 'JAMstack blog with MDX and Contentlayer',
        'django': 'Django + DRF + PostgreSQL',
        'flask': 'Flask + SQLAlchemy + PostgreSQL',
        'fastapi': 'FastAPI + Pydantic',
        'expressjs': 'Express.js + Node.js',
        'custom': 'AI-generated custom stack based on requirements'
    }

    # Create values for selector
    values = [(name, f"{name:<15} - {desc}") for name, desc in stack_descriptions.items()]

    # Show stack selector
    selector = InlineSelector(values)
    stack_name = selector.select()

    if stack_name is None:
        console.print("\n[yellow]Operation cancelled[/]")
        return

    # Get project description for custom stack
    description = None
    if stack_name == "custom":
        console.print("\n[bold cyan]Describe your project requirements:[/]")
        console.print("[dim]Example: I need a modern web app with authentication, blog functionality, and a newsletter system[/]")
        description = Prompt.ask("\n[cyan]Description")
        if not description:
            console.print("[yellow]Description is required for custom stack[/]")
            return

    # Create project
    asyncio.run(create_project(project_name, stack_name, description)) 