"""
Base template class for all stack templates.
"""

from abc import ABC, abstractmethod
import json
import os
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from ..utils.dependency_manager import DependencyManager

# Initialize rich console
console = Console()

class BaseTemplate(ABC):
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_dir = os.path.abspath(project_name)
        self.dependency_manager = DependencyManager()

    @property
    @abstractmethod
    def dependencies(self) -> Dict[str, str]:
        """Return a dictionary of package dependencies and their versions."""
        pass

    @property
    @abstractmethod
    def dev_dependencies(self) -> Dict[str, str]:
        """Return a dictionary of development dependencies and their versions."""
        pass

    @abstractmethod
    async def generate(self) -> None:
        """Generate the project structure and files."""
        pass

    def create_project_directory(self) -> None:
        """Create the project directory if it doesn't exist."""
        os.makedirs(self.project_dir, exist_ok=True)

    def get_template_dir(self) -> str:
        """Get the directory containing template files for this stack."""
        return os.path.join(os.path.dirname(__file__), self.__class__.__name__.lower())

    def create_file(self, relative_path: str, content: str) -> None:
        """Create a file with the given content."""
        full_path = os.path.join(self.project_dir, relative_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)

    async def create_package_json(self, extra_fields: Dict[str, Any] = None) -> None:
        """Create a package.json file with the project's dependencies."""
        # Analyze dependencies for compatibility and updates
        deps_analysis = await self.dependency_manager.analyze_dependencies(self.dependencies)
        dev_deps_analysis = await self.dependency_manager.analyze_dependencies(self.dev_dependencies)

        # Print warnings and recommendations
        if deps_analysis["compatibility_warnings"] or deps_analysis["version_updates"]:
            console.print()  # Add spacing
            console.print(Panel(
                "[bold cyan]Dependency Analysis[/]",
                title="Stackmate",
                title_align="left",
                width=80
            ))
            
            if deps_analysis["compatibility_warnings"]:
                console.print("\n[bold]Compatibility Warnings:[/]")
                for warning in deps_analysis["compatibility_warnings"]:
                    console.print(f"[yellow]• {warning}[/]")
            
            if deps_analysis["version_updates"]:
                console.print("\n[bold]Version Updates:[/]")
                for update in deps_analysis["version_updates"]:
                    console.print(f"[green]• {update}[/]")
            
            if deps_analysis["recommendations"]:
                console.print("\n[bold]Recommendations:[/]")
                for rec in deps_analysis["recommendations"]:
                    console.print(f"[blue]• {rec}[/]")

        # Create package.json with optimized dependencies
        package_json = {
            "name": self.project_name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": deps_analysis["updated_dependencies"],
            "devDependencies": dev_deps_analysis["updated_dependencies"]
        }

        if extra_fields:
            package_json.update(extra_fields)

        self.create_file('package.json', json.dumps(package_json, indent=2))

        # Create .npmrc for better dependency management
        npmrc_content = """
# Ensure consistent dependency versions across the project
save-exact=true

# Improve installation performance
prefer-offline=true
cache-min=3600

# Security settings
audit=true
fund=false
        """.strip()
        self.create_file('.npmrc', npmrc_content)

    def print_success_message(self, additional_steps: List[str] = None):
        """Print a standardized success message with next steps."""
        console.print()  # Add spacing
        console.print(Panel(
            f"[bold green]✨ Project {self.project_name} created successfully![/]",
            title="Stackmate",
            title_align="left",
            border_style="green",
            width=80
        ))
        
        if additional_steps:
            console.print()  # Add spacing
            table = Table(
                title="[bold cyan]Next Steps[/]",
                show_header=False,
                box=None,
                padding=(0, 2),
                title_justify="left"
            )
            table.add_column(
                "Step",
                style="bright_white",
                no_wrap=False
            )
            
            for i, step in enumerate(additional_steps, 1):
                if step.startswith("\n"):  # Handle spacers
                    table.add_row("")
                    table.add_row(step.strip())
                else:
                    # Add command highlighting
                    if "#" in step:  # Handle comments
                        cmd, comment = step.split("#", 1)
                        table.add_row(f"[cyan]{i}.[/] [green]{cmd.strip()}[/] [dim]#{comment}[/]")
                    else:
                        if step.startswith("cd "):
                            table.add_row(f"[cyan]{i}.[/] [green]{step}[/]")
                        elif "http" in step:  # Handle URLs
                            table.add_row(f"[cyan]{i}.[/] {step}")
                        else:
                            table.add_row(f"[cyan]{i}.[/] [green]{step}[/]")
            
            console.print(table)
            console.print()  # Add final spacing 