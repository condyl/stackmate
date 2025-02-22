from setuptools import setup, find_packages

setup(
    name="stackmate",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",  # Using Click for CLI interface
    ],
    entry_points={
        "console_scripts": [
            "stackmate=stackmate.cli:main",
        ],
    },
    author="Your Name",
    description="A CLI tool for stack management",
    python_requires=">=3.6",
) 