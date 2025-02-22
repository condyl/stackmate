import click
from .templates import TEMPLATES, AVAILABLE_STACKS

@click.group()
def cli():
    """Stackmate - AI-Powered Tech Stack Generator"""
    pass

@cli.command()
@click.argument('project_name')
@click.option('--stack', type=click.Choice(AVAILABLE_STACKS), help='Choose a predefined stack template')
@click.option('--describe', help='Describe your project requirements in natural language')
def new(project_name: str, stack: str = None, describe: str = None):
    """Create a new project with the specified stack."""
    click.echo(f"Creating new project: {project_name}")
    
    if describe:
        click.echo(f"Project description: {describe}")
        click.echo("AI stack suggestion feature coming soon!")
    elif stack:
        click.echo(f"Using stack template: {stack}")
        template_class = TEMPLATES[stack]
        template = template_class(project_name)
        template.generate()
    else:
        click.echo("No stack specified. Interactive wizard coming soon!")

@cli.command()
@click.argument('feature')
def add(feature: str):
    """Add a feature to your project."""
    click.echo(f"Adding feature: {feature}")
    click.echo("Feature addition coming soon!")

@cli.command()
def customize():
    """Customize your project using AI."""
    click.echo("AI customization coming soon!")

def main():
    cli()

if __name__ == "__main__":
    main() 