"""
Basic Flask template for simple web applications.
"""

import os
from .base import BaseTemplate

class FlaskTemplate(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "flask": ">=3.0.0",
            "python-dotenv": ">=1.0.0",
        }

    @property
    def dev_dependencies(self) -> dict:
        return {
            "pytest": ">=7.4.3",
            "black": ">=23.12.1",
            "flake8": ">=6.1.0",
        }

    async def generate(self) -> None:
        """Generate a basic Flask project structure."""
        self.create_project_directory()

        # Create project structure
        dirs = [
            "src",
            "src/static",
            "src/templates",
            "tests",
        ]
        for dir_path in dirs:
            os.makedirs(os.path.join(self.project_dir, dir_path), exist_ok=True)

        # Create main application file
        self.create_file('src/__init__.py', '''from flask import Flask

def create_app():
    app = Flask(__name__)

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app''')

        # Create routes
        self.create_file('src/routes.py', '''from flask import Blueprint, render_template

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/about')
def about():
    return render_template('about.html')''')

        # Create templates
        self.create_file('src/templates/base.html', '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}{% endblock %} - Flask App</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <nav>
        <a href="{{ url_for('main.index') }}">Home</a>
        <a href="{{ url_for('main.about') }}">About</a>
    </nav>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>''')

        self.create_file('src/templates/index.html', '''{% extends 'base.html' %}

{% block title %}Home{% endblock %}

{% block content %}
    <h1>Welcome to Flask</h1>
    <p>This is a simple Flask application template.</p>
{% endblock %}''')

        self.create_file('src/templates/about.html', '''{% extends 'base.html' %}

{% block title %}About{% endblock %}

{% block content %}
    <h1>About</h1>
    <p>This is a basic Flask template created with Stackmate.</p>
{% endblock %}''')

        # Create static files
        self.create_file('src/static/style.css', '''body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
}

nav {
    margin-bottom: 20px;
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

nav a {
    margin-right: 15px;
    text-decoration: none;
    color: #333;
}

nav a:hover {
    color: #666;
}

h1 {
    color: #333;
}''')

        # Create application entry point
        self.create_file('app.py', '''from src import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)''')

        # Create simple test
        self.create_file('tests/test_app.py', '''def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_about_page(client):
    response = client.get('/about')
    assert response.status_code == 200''')

        # Create test configuration
        self.create_file('tests/conftest.py', '''import pytest
from src import create_app

@pytest.fixture
def app():
    app = create_app()
    return app

@pytest.fixture
def client(app):
    return app.test_client()''')

        # Create requirements files
        self.create_file('requirements.txt', '\n'.join([
            f"{pkg}{ver}" for pkg, ver in self.dependencies.items()
        ]))

        self.create_file('requirements-dev.txt', '''
-r requirements.txt

''' + '\n'.join([
            f"{pkg}{ver}" for pkg, ver in self.dev_dependencies.items()
        ]))

        # Create README
        self.create_file('README.md', f'''# {self.project_name}

A simple Flask web application.

## Features

- Basic Flask 3.0 setup
- Simple routing with Blueprints
- HTML templates with Jinja2
- Basic CSS styling
- Testing setup with pytest

## Prerequisites

- Python 3.8+

## Installation

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # for development
   ```

3. Run the development server:
   ```bash
   python app.py
   ```

   Open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

```
{self.project_name}/
├── src/
│   ├── static/        # CSS, JavaScript, and other static files
│   ├── templates/     # HTML templates
│   ├── __init__.py   # Application factory
│   └── routes.py     # Route definitions
├── tests/            # Test suite
└── app.py           # Application entry point
```

## Development

- Run development server: `python app.py`
- Run tests: `pytest`
- Format code: `black .`
- Check code style: `flake8`

## License

This project is licensed under the MIT License.
''')

        # Create .gitignore
        self.create_file('.gitignore', '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment variables
.env
.env.*
!.env.example

# Coverage reports
.coverage
htmlcov/''')

        # Print success message
        self.print_success_message([
            f"cd {self.project_name}",
            "python -m venv venv",
            "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
            "pip install -r requirements.txt",
            "python app.py",
            "\nThen open [link]http://localhost:5000[/link] in your browser"
        ]) 