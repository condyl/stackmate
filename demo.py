#!/usr/bin/env python3
"""
Stackmate Demo Script
This script demonstrates the key features of Stackmate by creating and customizing projects.
"""

import os
import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

console = Console()

async def run_command(cmd: str) -> None:
    """Run a shell command and display the output."""
    console.print(f"\n$ [bold green]{cmd}[/]")
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if stdout:
        console.print(stdout.decode())
    if stderr:
        console.print(f"[red]{stderr.decode()}[/]")
    
    if process.returncode != 0:
        raise Exception(f"Command failed with exit code {process.returncode}")
    
    return process.returncode

async def demo_project_creation():
    """Demonstrate project creation with different stacks."""
    console.print(Panel.fit(
        "[bold blue]Demo 1: Project Creation[/]\n"
        "We'll create projects using different stack templates and AI analysis."
    ))
    
    # 1. Create a project using Modern React stack
    console.print("\n[bold]1. Creating a project with Modern React stack[/]")
    await run_command("stackmate new modern-react-app --stack modern-react")
    
    # 2. Create a project using natural language description
    console.print("\n[bold]2. Creating a project using AI analysis[/]")
    console.print("[yellow]Note: Skipping AI analysis as it requires a valid Gemini API key.[/]")
    await run_command("stackmate new saas-app --stack enterprise-react")

async def demo_feature_addition():
    """Demonstrate adding features to an existing project."""
    console.print(Panel.fit(
        "[bold blue]Demo 2: Feature Addition[/]\n"
        "We'll add various features to an existing project."
    ))
    
    # Create a test project
    await run_command("stackmate new test-project --stack modern-react")
    os.chdir("test-project")
    
    try:
        # 1. Add authentication
        console.print("\n[bold]1. Adding authentication[/]")
        await run_command("stackmate add auth")
        
        # 2. Add UI components
        console.print("\n[bold]2. Adding UI components[/]")
        await run_command("stackmate add components")
        
        # 3. Add development tools
        console.print("\n[bold]3. Adding development tools[/]")
        await run_command("stackmate add tools")
    finally:
        os.chdir("..")

async def demo_customization():
    """Demonstrate project customization capabilities."""
    console.print(Panel.fit(
        "[bold blue]Demo 3: Project Customization[/]\n"
        "We'll customize an existing project with AI assistance."
    ))
    
    os.chdir("test-project")
    try:
        await run_command("stackmate customize")
    finally:
        os.chdir("..")

async def show_project_structure():
    """Display the structure of generated projects."""
    console.print(Panel.fit(
        "[bold blue]Project Structure Overview[/]\n"
        "Let's examine the structure of our generated projects."
    ))
    
    # Check if tree command is available
    try:
        await run_command("which tree")
        has_tree = True
    except Exception:
        has_tree = False
        console.print("[yellow]Note: 'tree' command not found. Using 'ls' instead.[/]")
    
    # Show Modern React project structure
    console.print("\n[bold]Modern React Project Structure:[/]")
    if has_tree:
        await run_command("tree modern-react-app -L 3")
    else:
        await run_command("ls -R modern-react-app")
    
    # Show SaaS project structure
    console.print("\n[bold]SaaS Project Structure:[/]")
    if has_tree:
        await run_command("tree saas-app -L 3")
    else:
        await run_command("ls -R saas-app")

async def cleanup():
    """Clean up demo projects."""
    console.print("\n[bold red]Cleaning up demo projects...[/]")
    for project in ["modern-react-app", "saas-app", "test-project"]:
        if os.path.exists(project):
            await run_command(f"rm -rf {project}")

async def main():
    """Run the complete demo."""
    console.print(Panel.fit(
        "[bold cyan]Stackmate Demo[/]\n"
        "AI-Powered Tech Stack Generator"
    ))
    
    try:
        # Ensure GEMINI_API_KEY is set
        if not os.getenv("GEMINI_API_KEY"):
            console.print(
                "[red]Error: GEMINI_API_KEY environment variable not set.\n"
                "Please set it before running the demo:[/]\n"
                "export GEMINI_API_KEY=your-api-key"
            )
            return 1
        
        # Run demos
        await demo_project_creation()
        await demo_feature_addition()
        await demo_customization()
        await show_project_structure()
        
        # Show cleanup prompt
        if click.confirm("\nWould you like to clean up the demo projects?"):
            await cleanup()
        
        console.print("\n[bold green]Demo completed successfully![/]")
        
    except Exception as e:
        console.print(f"\n[red]Error during demo: {str(e)}[/]")
        return 1

if __name__ == "__main__":
    asyncio.run(main()) 