from setuptools import setup, find_packages

setup(
    name="stackmate",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",  # CLI interface
        "google-generativeai>=0.3.0",  # Gemini API
        "rich>=13.0.0",  # Terminal UI
        "textual>=0.47.1",  # Interactive TUI
        "jinja2>=3.0.0",  # Template rendering
        "pyyaml>=6.0.0",  # Configuration management
        "gitpython>=3.1.0",  # Git integration
        "aiohttp>=3.9.0",  # Async HTTP client
        "prompt_toolkit>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "stackmate=stackmate.cli:main",
        ],
    },
    author="Your Name",
    description="A CLI tool for stack management",
    python_requires=">=3.8",  # Updated for better async support
) 