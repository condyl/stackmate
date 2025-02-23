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
        """Add a feature to an existing project."""
        console.print(Panel.fit(
            f"[bold blue]Adding {feature} to project[/]",
            title="Stackmate"
        ))
        return asyncio.run(_add(feature, project_dir))

    return add

async def _add(feature: str, project_dir: str):
    """Async implementation of add command."""
    if not os.path.exists(project_dir):
        raise ConfigurationError(f"Project directory '{project_dir}' does not exist")
        
    try:
        feature_handler = AVAILABLE_FEATURES[feature](project_dir)
        await feature_handler.add()
    except KeyError:
        raise FeatureError(f"Unknown feature: {feature}")
    except Exception as e:
        raise FeatureError(f"Failed to add feature: {str(e)}")

def customize_command():
    @cli.command()
    @click.option('--project-dir', '-d',
                 default='.',
                 help='Project directory (defaults to current directory)')
    @click.option('--ai', '-a',
                 is_flag=True,
                 help='Use AI to analyze and suggest customizations')
    @handle_errors
    def customize(project_dir: str, ai: bool = False):
        """Customize an existing project with additional features and configurations.

        Examples:
            stackmate customize                 Show interactive customization menu
            stackmate customize --ai            Get AI-powered customization suggestions
        """
        return asyncio.run(_customize(project_dir, ai))

    return customize

async def _customize(project_dir: str, ai: bool = False):
    """Async implementation of customize command."""
    if not os.path.exists(project_dir):
        raise ConfigurationError(f"Project directory '{project_dir}' does not exist")

    try:
        # Read package.json to analyze current project setup
        try:
            with open(os.path.join(project_dir, 'package.json'), 'r') as f:
                package_json = json.load(f)
        except FileNotFoundError:
            raise ConfigurationError("No package.json found. Make sure you're in a Node.js project directory.")
        except json.JSONDecodeError:
            raise ConfigurationError("Invalid package.json file. Please check the file format.")

        if ai:
            # Use AI to analyze project and suggest customizations
            analyzer, generator = get_ai_components()
            
            with console.status("[bold green]Analyzing project...[/]"):
                # Analyze package.json and project structure
                project_analysis = {
                    "dependencies": package_json.get("dependencies", {}),
                    "devDependencies": package_json.get("devDependencies", {}),
                    "scripts": package_json.get("scripts", {}),
                }
                
                # Get AI suggestions
                suggestions = await analyzer.analyze_project(project_analysis)
            
            console.print(Panel.fit(
                "[bold cyan]Project Analysis Results[/]",
                title="Stackmate"
            ))

            # Display workflow improvements
            if suggestions.get("workflow_improvements"):
                console.print("\n[bold cyan]Workflow Improvements[/]")
                table = Table(show_header=True)
                table.add_column("Category", style="cyan")
                table.add_column("Suggestion", style="white")
                table.add_column("Priority", style="yellow")
                table.add_column("Implementation", style="green")
                
                for improvement in suggestions["workflow_improvements"]:
                    table.add_row(
                        improvement["category"],
                        improvement["suggestion"],
                        improvement["priority"].upper(),
                        improvement["implementation"]
                    )
                console.print(table)

            # Display dependency updates
            if suggestions.get("dependency_updates"):
                console.print("\n[bold cyan]Dependency Updates[/]")
                table = Table(show_header=True)
                table.add_column("Package", style="cyan")
                table.add_column("Current", style="yellow")
                table.add_column("Suggested", style="green")
                table.add_column("Reason", style="white")
                
                for update in suggestions["dependency_updates"]:
                    table.add_row(
                        update["package"],
                        update["current_version"],
                        update["suggested_version"],
                        update["reason"]
                    )
                console.print(table)

            # Display performance suggestions
            if suggestions.get("performance_suggestions"):
                console.print("\n[bold cyan]Performance Improvements[/]")
                table = Table(show_header=True)
                table.add_column("Area", style="cyan")
                table.add_column("Issue", style="white")
                table.add_column("Solution", style="green")
                table.add_column("Impact", style="yellow")
                
                for suggestion in suggestions["performance_suggestions"]:
                    table.add_row(
                        suggestion["area"],
                        suggestion["issue"],
                        suggestion["solution"],
                        suggestion["impact"].upper()
                    )
                console.print(table)

            # Display developer experience improvements
            if suggestions.get("dx_improvements"):
                console.print("\n[bold cyan]Developer Experience Improvements[/]")
                table = Table(show_header=True)
                table.add_column("Category", style="cyan")
                table.add_column("Suggestion", style="white")
                table.add_column("Benefit", style="green")
                
                for improvement in suggestions["dx_improvements"]:
                    table.add_row(
                        improvement["category"],
                        improvement["suggestion"],
                        improvement["benefit"]
                    )
                console.print(table)

            # Display best practices
            if suggestions.get("best_practices"):
                console.print("\n[bold cyan]Best Practices[/]")
                table = Table(show_header=True)
                table.add_column("Category", style="cyan")
                table.add_column("Current State", style="yellow")
                table.add_column("Recommendation", style="green")
                
                for practice in suggestions["best_practices"]:
                    table.add_row(
                        practice["category"],
                        practice["current_state"],
                        practice["recommendation"]
                    )
                console.print(table)

            # Ask if user wants to apply any of these suggestions
            if click.confirm("\nWould you like to apply any of these suggestions?"):
                # Show interactive menu of available improvements
                options = []
                
                # Add workflow improvements
                for imp in suggestions.get("workflow_improvements", []):
                    options.append((
                        f"workflow_{imp['category']}",
                        f"[Workflow] {imp['suggestion']} ({imp['priority'].upper()})"
                    ))
                
                # Add dependency updates
                for dep in suggestions.get("dependency_updates", []):
                    options.append((
                        f"dependency_{dep['package']}",
                        f"[Dependency] Update {dep['package']} to {dep['suggested_version']}"
                    ))
                
                # Add performance improvements
                for perf in suggestions.get("performance_suggestions", []):
                    options.append((
                        f"performance_{perf['area']}",
                        f"[Performance] {perf['solution']} ({perf['impact'].upper()})"
                    ))
                
                # Add DX improvements
                for dx in suggestions.get("dx_improvements", []):
                    options.append((
                        f"dx_{dx['category']}",
                        f"[DX] {dx['suggestion']}"
                    ))
                
                # Add best practices
                for practice in suggestions.get("best_practices", []):
                    options.append((
                        f"practice_{practice['category']}",
                        f"[Best Practice] {practice['recommendation']}"
                    ))
                
                # Add exit option
                options.append(("exit", "Exit - Return to command line"))

                from .interactive import InlineSelector
                
                while True:
                    # Show improvement selector
                    selector = InlineSelector(options)
                    improvement = selector.select()
                    
                    if improvement is None or improvement == "exit":
                        break
                    
                    # TODO: Implement the actual application of improvements
                    console.print("\n[yellow]Automatic improvement application is not yet implemented.[/]")
                    console.print("[yellow]This feature will be available in a future update.[/]")
                    
                    if not click.confirm("\nWould you like to select another improvement?"):
                        break
            return

        # Show interactive customization menu
        console.print("\n[bold cyan]Stackmate Project Customization[/]")
        console.print("[dim]Customize your project with additional features and configurations[/]\n")
        console.print("[dim]Use ↑/↓ arrows to select an option, Enter to confirm[/]\n")

        # Define customization options with descriptions
        options = [
            ("auth", "Authentication - Add NextAuth.js, Clerk, or Firebase"),
            ("components", "UI Components - Add shadcn/ui or Material UI"),
            ("tools", "Development Tools - Add ESLint, Prettier, Jest"),
            ("deployment", "Deployment - Configure deployment settings"),
            ("database", "Database - Add database integration"),
            ("api", "API - Add API integration"),
            ("testing", "Testing - Add testing setup"),
            ("cicd", "CI/CD - Add workflow configuration"),
            ("exit", "Exit - Return to command line")
        ]

        from .interactive import InlineSelector
        
        while True:
            # Show feature selector
            selector = InlineSelector(options)
            feature = selector.select()
            
            if feature is None or feature == "exit":
                break
                
            if feature in ["auth", "components", "tools"]:
                try:
                    feature_handler = AVAILABLE_FEATURES[feature](project_dir)
                    await feature_handler.add()
                except Exception as e:
                    console.print(f"\n[red]Error:[/] Failed to add {feature}: {str(e)}")
            else:
                console.print("\n[yellow]This feature is not yet implemented.[/]")
            
            # Ask to continue only if we successfully reached this point
            if not click.confirm("\nWould you like to make more customizations?"):
                break
        
    except Exception as e:
        raise ConfigurationError(f"Failed to customize project: {str(e)}")

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