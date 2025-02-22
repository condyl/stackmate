"""
Base template class for all stack templates.
"""

from abc import ABC, abstractmethod
import json
import os
from typing import Dict, List, Any

class BaseTemplate(ABC):
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.project_dir = os.path.abspath(project_name)

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
    def generate(self) -> None:
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

    def create_package_json(self, extra_fields: Dict[str, Any] = None) -> None:
        """Create a package.json file with the project's dependencies."""
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
            "dependencies": self.dependencies,
            "devDependencies": self.dev_dependencies
        }

        if extra_fields:
            package_json.update(extra_fields)

        self.create_file('package.json', json.dumps(package_json, indent=2)) 