import click
import os
import json
import asyncio
from typing import Optional
from functools import wraps
from .templates import TEMPLATES, AVAILABLE_STACKS
from .ai import StackAnalyzer, CodeGenerator
from .features import AVAILABLE_FEATURES

# Initialize AI components
def get_ai_components():
    """Get AI components initialized with API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise click.ClickException(
            "GEMINI_API_KEY environment variable not set. "
            "Get your API key from https://makersuite.google.com/app/apikey"
        )
    return StackAnalyzer(api_key), CodeGenerator(api_key)

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
    @async_command
    async def new(project_name: str, stack: Optional[str] = None, describe: Optional[str] = None):
        """Create a new project with the specified stack."""
        click.echo(f"Creating new project: {project_name}")
        
        if describe:
            click.echo(f"Project description: {describe}")
            try:
                analyzer, _ = get_ai_components()
                analysis = await analyzer.analyze_requirements(describe)
                
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
                    template = TEMPLATES["custom"](project_name, analysis)
                    await template.generate()
                    
            except Exception as e:
                click.echo(f"Error during AI analysis: {str(e)}")
                click.echo("\nPlease try one of our predefined stacks instead:")
                for available_stack in AVAILABLE_STACKS:
                    click.echo(f"- {available_stack}")
                return
                
        elif stack:
            click.echo(f"Using stack template: {stack}")
            template_class = TEMPLATES[stack]
            template = template_class(project_name)
            await template.generate()
        else:
            click.echo("No stack specified. Please use --stack or --describe option.")
            click.echo("\nAvailable stacks:")
            for available_stack in AVAILABLE_STACKS:
                click.echo(f"- {available_stack}")
    return new

def add_command():
    @cli.command()
    @click.argument('feature', type=click.Choice(list(AVAILABLE_FEATURES.keys())))
    @click.option('--project-dir', default='.', help='Project directory')
    @async_command
    async def add(feature: str, project_dir: str):
        """Add a feature to an existing project."""
        click.echo(f"Adding {feature} to your project...")
        
        try:
            # Get the feature handler
            handler = AVAILABLE_FEATURES[feature]
            
            # Execute the handler
            await handler(project_dir)
            
        except Exception as e:
            click.echo(f"Error: {str(e)}")
            return
    
    return add

def customize_command():
    @cli.command()
    @click.option('--project-dir', default='.', help='Project directory')
    @async_command
    async def customize(project_dir: str):
        """Customize an existing project."""
        click.echo("Customizing project...")
        # Customization logic here
        pass
    return customize

def main():
    cli.add_command(new_command())
    cli.add_command(add_command())
    cli.add_command(customize_command())
    cli()

if __name__ == "__main__":
    main() 