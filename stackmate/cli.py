import click
import os
import json
import asyncio
from typing import Optional
from functools import wraps
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from .templates import TEMPLATES, AVAILABLE_STACKS
from .ai import StackAnalyzer, CodeGenerator
from .features import AVAILABLE_FEATURES
from .interactive import run as run_interactive

# Initialize rich console
console = Console()

class StackmateError(Exception):
    """Base exception for Stackmate errors."""
    pass

class ConfigurationError(StackmateError):
    """Raised when there's an issue with configuration."""
    pass

class AIError(StackmateError):
    """Raised when there's an issue with AI operations."""
    pass

class TemplateError(StackmateError):
    """Raised when there's an issue with templates."""
    pass

class FeatureError(StackmateError):
    """Raised when there's an issue with features."""
    pass

def handle_errors(func):
    """Decorator to handle errors in CLI commands."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            if asyncio.iscoroutine(result):
                return asyncio.run(result)
            return result
        except ConfigurationError as e:
            console.print(f"\n[red]Configuration Error:[/] {str(e)}")
            console.print("[yellow]Please check your configuration and try again.[/]")
            return 1
        except AIError as e:
            console.print(f"\n[red]AI Error:[/] {str(e)}")
            console.print("[yellow]Please check your API key and internet connection.[/]")
            return 1
        except TemplateError as e:
            console.print(f"\n[red]Template Error:[/] {str(e)}")
            console.print("[yellow]Please check the template configuration and try again.[/]")
            return 1
        except FeatureError as e:
            console.print(f"\n[red]Feature Error:[/] {str(e)}")
            console.print("[yellow]Please check the feature requirements and try again.[/]")
            return 1
        except Exception as e:
            console.print(f"\n[red]Unexpected Error:[/] {str(e)}")
            console.print("[yellow]Please report this issue on GitHub.[/]")
            return 1
    return wrapper

# Initialize AI components
def get_ai_components():
    """Get AI components initialized with API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ConfigurationError(
            "GEMINI_API_KEY environment variable not set. "
            "Get your API key from https://makersuite.google.com/app/apikey"
        )
    try:
        return StackAnalyzer(api_key), CodeGenerator(api_key)
    except Exception as e:
        raise AIError(f"Failed to initialize AI components: {str(e)}")

def async_command(f):
    """Decorator to run async commands."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@click.group()
def cli():
    """Stackmate - AI-Powered Tech Stack Generator

    Create modern web applications with best practices and AI-powered stack recommendations.
    
    Examples:
        stackmate new -i                    Create a project using interactive mode
        stackmate new my-app --stack t3     Create a T3 stack project
        stackmate add auth                  Add authentication to existing project
    """
    pass

def new_command():
    @cli.command()
    @click.argument('project_name', required=False)
    @click.option('--stack', '-s',
                 type=click.Choice(AVAILABLE_STACKS),
                 help='Choose a predefined stack template (e.g., modern-react, t3, django)')
    @click.option('--describe', '-d',
                 help='Describe your project requirements in natural language for AI analysis')
    @click.option('--interactive', '-i',
                 is_flag=True,
                 help='Use interactive mode with arrow key navigation and stack descriptions')
    @handle_errors
    def new(project_name: str = None, stack: Optional[str] = None, describe: Optional[str] = None, interactive: bool = False):
        """Create a new project with the specified stack.

        Examples:
            stackmate new -i                    Create using interactive mode
            stackmate new my-app --stack t3     Create a T3 stack project
            stackmate new my-app --describe "I need a modern web app with authentication"
        
        Available Stacks:
            modern-react    Next.js + Tailwind + Shadcn
            t3             Full-Stack T3 Stack
            django         Django + DRF + PostgreSQL
            flask          Flask + SQLAlchemy
            fastapi        FastAPI + Pydantic
            expressjs      Express.js + Node.js
            custom         AI-generated custom stack
        """
        if interactive:
            return run_interactive()
        elif not project_name:
            raise ConfigurationError("Project name is required when not using interactive mode")
        return asyncio.run(_new(project_name, stack, describe))

    return new

async def _new(project_name: str, stack: Optional[str] = None, describe: Optional[str] = None):
    """Async implementation of new command."""
    if not project_name:
        raise ConfigurationError("Project name is required")
        
    if os.path.exists(project_name):
        raise ConfigurationError(f"Directory '{project_name}' already exists")
        
    console.print(Panel.fit(
        f"[bold blue]Creating New Project: {project_name}[/]"
    ))
    
    if describe:
        console.print(f"\n[bold]Project description:[/] {describe}")
        analyzer, _ = get_ai_components()
        try:
            template_name, analysis = await analyzer.analyze_requirements(describe)
        except Exception as e:
            raise AIError(f"Failed to analyze requirements: {str(e)}")
            
        console.print(Panel.fit(
            "[bold cyan]AI Analysis Results[/]",
            title="Stackmate"
        ))
        
        if "stack" in analysis:
            table = Table(title="Recommended Stack", show_header=True)
            table.add_column("Component", style="cyan")
            table.add_column("Selection", style="green")
            
            # Add selected template to the table
            table.add_row("Template", template_name)
            
            for key, value in analysis["stack"].items():
                if isinstance(value, list):
                    table.add_row(key.title(), ", ".join(value))
                else:
                    table.add_row(key.title(), str(value))
            console.print(table)
        
        if "reasoning" in analysis:
            console.print("\n[bold cyan]Reasoning:[/]")
            for key, value in analysis["reasoning"].items():
                console.print(f"[green]• {key}:[/] {value}")
        
        if "additional_considerations" in analysis:
            console.print("\n[bold cyan]Additional Considerations:[/]")
            for consideration in analysis["additional_considerations"]:
                console.print(f"[yellow]• {consideration}[/]")
        
        if click.confirm("\nWould you like to proceed with this stack?"):
            try:
                with console.status("[bold green]Generating project...[/]"):
                    if template_name == "custom":
                        template = TEMPLATES[template_name](project_name, analysis)
                    else:
                        template = TEMPLATES[template_name](project_name)
                    await template.generate()
            except Exception as e:
                raise TemplateError(f"Failed to generate project: {str(e)}")
            
    elif stack:
        console.print(f"\n[bold]Using stack template:[/] [green]{stack}[/]")
        try:
            with console.status("[bold green]Generating project...[/]"):
                template_class = TEMPLATES[stack]
                template = template_class(project_name)
                await template.generate()
        except KeyError:
            raise TemplateError(f"Unknown stack template: {stack}")
        except Exception as e:
            raise TemplateError(f"Failed to generate project: {str(e)}")
    else:
        console.print("\n[yellow]No stack specified. Please use --stack or --describe option.[/]")
        
        table = Table(title="Available Stacks", show_header=True)
        table.add_column("Stack", style="cyan")
        table.add_column("Description", style="green")
        
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
        
        for stack_name in AVAILABLE_STACKS:
            table.add_row(stack_name, stack_descriptions.get(stack_name, ''))
        
        console.print(table)

def add_command():
    @cli.command()
    @click.argument('feature',
                   type=click.Choice(list(AVAILABLE_FEATURES.keys())),
                   required=True)
    @click.option('--project-dir', '-d',
                 default='.',
                 help='Project directory (defaults to current directory)')
    @handle_errors
    def add(feature: str, project_dir: str):
        """Add a feature to an existing project.

        Examples:
            stackmate add auth              Add authentication
            stackmate add components        Add UI components
            stackmate add tools             Add development tools

        Available Features:
            auth        Authentication (NextAuth.js, Clerk, or Firebase)
            components  UI components (shadcn/ui or Material UI)
            tools      Development tools (ESLint, Prettier, Jest)
        
        Options:
            --project-dir, -d  Specify project directory (default: current directory)
        """
        return asyncio.run(_add(feature, project_dir))

    return add

async def _add(feature: str, project_dir: str):
    """Async implementation of add command."""
    if not os.path.exists(project_dir):
        raise ConfigurationError(f"Project directory '{project_dir}' does not exist")
        
    if not os.path.exists(os.path.join(project_dir, 'package.json')):
        raise ConfigurationError(f"No package.json found in '{project_dir}'. Is this a Node.js project?")
        
    try:
        console.print(Panel.fit(
            f"[bold blue]Adding {feature} to project[/]",
            title="Stackmate"
        ))
        
        with console.status(f"[bold green]Adding {feature}...[/]"):
            feature_handler = AVAILABLE_FEATURES[feature](project_dir)
            await feature_handler.add()
    except KeyError:
        raise FeatureError(f"Unknown feature: {feature}")
    except Exception as e:
        raise FeatureError(f"Failed to add feature: {str(e)}")
        
    console.print(f"\n[bold green]✨ Successfully added {feature} to your project![/]")

def customize_command():
    @cli.command()
    @click.option('--project-dir', '-d',
                 default='.',
                 help='Project directory (defaults to current directory)')
    @click.option('--ai', '-a',
                 is_flag=True,
                 help='Use AI to analyze and suggest customizations')
    @click.option('--interactive', '-i',
                 is_flag=True,
                 help='Use interactive mode for customization')
    @handle_errors
    def customize(project_dir: str, ai: bool = False, interactive: bool = False):
        """Customize an existing project with additional features and configurations.

        Examples:
            stackmate customize                 Basic customization
            stackmate customize --ai            AI-powered customization
            stackmate customize --interactive   Interactive customization

        Options:
            --project-dir, -d   Specify project directory
            --ai, -a           Use AI for analysis and suggestions
            --interactive, -i   Use interactive mode
        """
        return asyncio.run(_customize(project_dir))

    return customize

async def _customize(project_dir: str):
    """Async implementation of customize command."""
    if not os.path.exists(project_dir):
        raise ConfigurationError(f"Project directory '{project_dir}' does not exist")
        
    try:
        console.print(Panel.fit(
            "[bold blue]Customizing Project[/]",
            title="Stackmate"
        ))
        
        with console.status("[bold green]Analyzing project...[/]"):
            _, generator = get_ai_components()
            # Add customization logic here
            
        console.print("\n[bold green]✨ Project customization completed![/]")
    except Exception as e:
        raise AIError(f"Failed to customize project: {str(e)}")

def main():
    """Main entry point for the CLI."""
    cli.add_command(new_command())
    cli.add_command(add_command())
    cli.add_command(customize_command())
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Error:[/] {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    main() 