"""
Base template class for all stack templates.
"""

from abc import ABC, abstractmethod
import json
import os
from typing import Dict, List, Any
from ..utils.dependency_manager import DependencyManager

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
            print("\nDependency Analysis:")
            print("===================")
            
            if deps_analysis["compatibility_warnings"]:
                print("\nCompatibility Warnings:")
                for warning in deps_analysis["compatibility_warnings"]:
                    print(f"- {warning}")
            
            if deps_analysis["version_updates"]:
                print("\nVersion Updates:")
                for update in deps_analysis["version_updates"]:
                    print(f"- {update}")
            
            if deps_analysis["recommendations"]:
                print("\nRecommendations:")
                for rec in deps_analysis["recommendations"]:
                    print(f"- {rec}")

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