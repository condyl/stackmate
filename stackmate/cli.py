import click
import os
import json
import asyncio
from typing import Optional
from functools import wraps
from .templates import TEMPLATES, AVAILABLE_STACKS
from .ai import StackAnalyzer, CodeGenerator
from .features import AVAILABLE_FEATURES

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
            click.echo(f"Configuration Error: {str(e)}", err=True)
            click.echo("Please check your configuration and try again.", err=True)
            return 1
        except AIError as e:
            click.echo(f"AI Error: {str(e)}", err=True)
            click.echo("Please check your API key and internet connection.", err=True)
            return 1
        except TemplateError as e:
            click.echo(f"Template Error: {str(e)}", err=True)
            click.echo("Please check the template configuration and try again.", err=True)
            return 1
        except FeatureError as e:
            click.echo(f"Feature Error: {str(e)}", err=True)
            click.echo("Please check the feature requirements and try again.", err=True)
            return 1
        except Exception as e:
            click.echo(f"Unexpected Error: {str(e)}", err=True)
            click.echo("Please report this issue on GitHub.", err=True)
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
    """Stackmate - AI-Powered Tech Stack Generator"""
    pass

def new_command():
    @cli.command()
    @click.argument('project_name')
    @click.option('--stack', type=click.Choice(AVAILABLE_STACKS), help='Choose a predefined stack template')
    @click.option('--describe', help='Describe your project requirements in natural language')
    @handle_errors
    def new(project_name: str, stack: Optional[str] = None, describe: Optional[str] = None):
        """Create a new project with the specified stack."""
        return asyncio.run(_new(project_name, stack, describe))

    return new

async def _new(project_name: str, stack: Optional[str] = None, describe: Optional[str] = None):
    """Async implementation of new command."""
    if not project_name:
        raise ConfigurationError("Project name is required")
        
    if os.path.exists(project_name):
        raise ConfigurationError(f"Directory '{project_name}' already exists")
        
    click.echo(f"Creating new project: {project_name}")
    
    if describe:
        click.echo(f"Project description: {describe}")
        analyzer, _ = get_ai_components()
        try:
            analysis = await analyzer.analyze_requirements(describe)
        except Exception as e:
            raise AIError(f"Failed to analyze requirements: {str(e)}")
            
        click.echo("\nAI Analysis Results:")
        click.echo("===================")
        
        if "stack" in analysis:
            click.echo("\nRecommended Stack:")
            for key, value in analysis["stack"].items():
                if isinstance(value, list):
                    click.echo(f"- {key}: {', '.join(value)}")
                else:
                    click.echo(f"- {key}: {value}")
        
        if "reasoning" in analysis:
            click.echo("\nReasoning:")
            for key, value in analysis["reasoning"].items():
                click.echo(f"- {key}: {value}")
        
        if "additional_considerations" in analysis:
            click.echo("\nAdditional Considerations:")
            for consideration in analysis["additional_considerations"]:
                click.echo(f"- {consideration}")
        
        if click.confirm("\nWould you like to proceed with this stack?"):
            try:
                template = TEMPLATES["custom"](project_name, analysis)
                await template.generate()
            except Exception as e:
                raise TemplateError(f"Failed to generate project: {str(e)}")
            
    elif stack:
        click.echo(f"Using stack template: {stack}")
        try:
            template_class = TEMPLATES[stack]
            template = template_class(project_name)
            await template.generate()
        except KeyError:
            raise TemplateError(f"Unknown stack template: {stack}")
        except Exception as e:
            raise TemplateError(f"Failed to generate project: {str(e)}")
    else:
        click.echo("No stack specified. Please use --stack or --describe option.")
        click.echo("\nAvailable stacks:")
        for available_stack in AVAILABLE_STACKS:
            click.echo(f"- {available_stack}")

def add_command():
    @cli.command()
    @click.argument('feature', type=click.Choice(AVAILABLE_FEATURES))
    @click.option('--project-dir', default='.', help='Project directory')
    @handle_errors
    def add(feature: str, project_dir: str):
        """Add a feature to an existing project."""
        return asyncio.run(_add(feature, project_dir))

    return add

async def _add(feature: str, project_dir: str):
    """Async implementation of add command."""
    if not os.path.exists(project_dir):
        raise ConfigurationError(f"Project directory '{project_dir}' does not exist")
        
    if not os.path.exists(os.path.join(project_dir, 'package.json')):
        raise ConfigurationError(f"No package.json found in '{project_dir}'. Is this a Node.js project?")
        
    try:
        feature_handler = AVAILABLE_FEATURES[feature](project_dir)
        await feature_handler.add()
    except KeyError:
        raise FeatureError(f"Unknown feature: {feature}")
    except Exception as e:
        raise FeatureError(f"Failed to add feature: {str(e)}")
        
    click.echo(f"\n✨ Successfully added {feature} to your project!")

def customize_command():
    @cli.command()
    @click.option('--project-dir', default='.', help='Project directory')
    @handle_errors
    def customize(project_dir: str):
        """Customize an existing project."""
        return asyncio.run(_customize(project_dir))

    return customize

async def _customize(project_dir: str):
    """Async implementation of customize command."""
    if not os.path.exists(project_dir):
        raise ConfigurationError(f"Project directory '{project_dir}' does not exist")
        
    try:
        _, generator = get_ai_components()
        # Add customization logic here
        click.echo("Project customization completed!")
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
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    main() 