"""
FastAPI template for simple API applications.
"""

import os
from .base import BaseTemplate

class FastAPITemplate(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "fastapi": ">=0.109.0",
            "uvicorn": ">=0.27.0",
            "pydantic": ">=2.6.0",
        }

    @property
    def dev_dependencies(self) -> dict:
        return {
            "pytest": ">=7.4.3",
            "httpx": ">=0.26.0",
            "black": ">=23.12.1",
            "flake8": ">=6.1.0",
        }

    async def generate(self) -> None:
        """Generate a basic FastAPI project structure."""
        self.create_project_directory()

        # Create project structure
        dirs = [
            "app",
            "app/api",
            "app/core",
            "tests",
        ]
        for dir_path in dirs:
            os.makedirs(os.path.join(self.project_dir, dir_path), exist_ok=True)

        # Create main application file
        self.create_file('app/main.py', '''from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="FastAPI App",
    description="A simple FastAPI application",
    version="0.1.0"
)

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI"}''')

        # Create API router
        self.create_file('app/api/__init__.py', '''from fastapi import APIRouter
from .health import router as health_router

router = APIRouter()
router.include_router(health_router, prefix="/health", tags=["health"])''')

        # Create health check endpoint
        self.create_file('app/api/health.py', '''from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def health_check():
    return {"status": "ok"}''')

        # Create core module
        self.create_file('app/core/__init__.py', '')
        self.create_file('app/core/config.py', '''from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "FastAPI App"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()''')

        # Create tests
        self.create_file('tests/__init__.py', '')
        self.create_file('tests/conftest.py', '''import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)''')

        self.create_file('tests/test_health.py', '''from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}''')

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

A simple FastAPI application.

## Features

- FastAPI 0.109+ setup
- Pydantic for data validation
- Testing setup with pytest
- Code formatting with black
- Basic API structure

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
   uvicorn app.main:app --reload
   ```

   Open [http://localhost:8000](http://localhost:8000) in your browser.
   API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Project Structure

```
{self.project_name}/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   └── main.py       # Application entry point
└── tests/            # Test suite
```

## Development

- Run development server: `uvicorn app.main:app --reload`
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
            "cd " + self.project_name,
            "python -m venv venv",
            "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
            "pip install -r requirements.txt",
            "uvicorn app.main:app --reload",
            "\nThen open [link]http://localhost:8000/docs[/link] in your browser"
        ]) 