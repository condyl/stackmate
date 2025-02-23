"""
Django template using Django, Django REST framework, and PostgreSQL.
"""

import os
from .base import BaseTemplate

class DjangoTemplate(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "django": "5.0.1",
            "djangorestframework": "3.14.0",
            "django-cors-headers": "4.3.1",
            "django-environ": "0.11.2",
            "psycopg": "3.1.18",  # Modern PostgreSQL driver that's more compatible
            "gunicorn": "21.2.0",
            "whitenoise": "6.6.0",
            "dj-database-url": "2.1.0",
            "python-dotenv": "1.0.0",
            "celery": "5.3.6",
            "redis": "5.0.1",
            # Pillow is temporarily removed for Python 3.13 compatibility
        }

    @property
    def dev_dependencies(self) -> dict:
        return {
            "pytest": "8.0.2",
            "pytest-django": "4.8.0",
            "pytest-cov": "4.1.0",
            "black": "24.2.0",
            "isort": "5.13.2",
            "flake8": "7.0.0",
            "django-debug-toolbar": "4.2.0",
            "factory-boy": "3.3.0",
        }

    async def generate(self) -> None:
        """Generate the project structure."""
        self.create_project_directory()
        
        # Create requirements.txt instead of pyproject.toml for better compatibility
        self.create_file('requirements.txt', '''# Core
django==5.0.1
djangorestframework==3.14.0
django-cors-headers==4.3.1
django-environ==0.11.2
psycopg==3.1.18  # Modern PostgreSQL driver

# Deployment
gunicorn==21.2.0
whitenoise==6.6.0
dj-database-url==2.1.0
python-dotenv==1.0.0

# Task Queue
celery==5.3.6
redis==5.0.1

# Image Processing
# Pillow is temporarily removed for Python 3.13 compatibility

# Development
pytest==8.0.2
pytest-django==4.8.0
pytest-cov==4.1.0
black==24.2.0
isort==5.13.2
flake8==7.0.0
django-debug-toolbar==4.2.0
factory-boy==3.3.0''')
        
        # Create pyproject.toml with dependency management
        await self.create_package_json()
        
        # Create Django project
        self.create_file('manage.py', '''#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
''')

        # Create project configuration
        self.create_file('config/__init__.py', '')
        
        self.create_file('config/settings.py', '''"""
Django settings for config project.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    DATABASE_URL=(str, 'postgres://postgres:postgres@localhost:5432/postgres'),
)

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='your-secret-key-here')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party apps
    'rest_framework',
    'corsheaders',
    'debug_toolbar',
    # Local apps
    'apps.core',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': env.db(),
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom user model
AUTH_USER_MODEL = 'users.User'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

# Debug toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
]

# Celery settings
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
''')

        self.create_file('config/urls.py', '''"""
URL configuration for config project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.core.urls')),
    path('api/users/', include('apps.users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
''')

        self.create_file('config/wsgi.py', '''"""
WSGI config for config project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
''')

        self.create_file('config/asgi.py', '''"""
ASGI config for config project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
''')

        # Create Celery configuration
        self.create_file('config/celery.py', '''"""
Celery configuration for config project.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
''')

        # Create apps directory
        os.makedirs(os.path.join(self.project_dir, 'apps/core'), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, 'apps/users'), exist_ok=True)

        # Create core app
        self.create_file('apps/core/__init__.py', '')
        self.create_file('apps/core/apps.py', '''from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
''')
        self.create_file('apps/core/urls.py', '''from django.urls import path

app_name = 'core'

urlpatterns = [
    # Add your URL patterns here
]
''')

        # Create users app
        self.create_file('apps/users/__init__.py', '')
        self.create_file('apps/users/apps.py', '''from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
''')
        self.create_file('apps/users/models.py', '''from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model."""
    pass
''')
        self.create_file('apps/users/urls.py', '''from django.urls import path

app_name = 'users'

urlpatterns = [
    # Add your URL patterns here
]
''')

        # Create tests directory
        os.makedirs(os.path.join(self.project_dir, 'tests'), exist_ok=True)
        self.create_file('tests/__init__.py', '')
        self.create_file('tests/conftest.py', '''import pytest
from django.conf import settings

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass
''')

        # Create static and media directories
        os.makedirs(os.path.join(self.project_dir, 'static'), exist_ok=True)
        os.makedirs(os.path.join(self.project_dir, 'media'), exist_ok=True)

        # Create templates directory
        os.makedirs(os.path.join(self.project_dir, 'templates'), exist_ok=True)

        # Create Docker configuration
        self.create_file('Dockerfile', '''FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    postgresql-client \\
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]''')

        self.create_file('docker-compose.yml', '''version: '3.8'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres

  redis:
    image: redis:7

  celery:
    build: .
    command: celery -A config worker -l INFO
    volumes:
      - .:/app
    environment:
      - DEBUG=1
      - DATABASE_URL=postgres://postgres:postgres@db:5432/postgres
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - web
      - redis

volumes:
  postgres_data:
''')

        # Create .env.example
        self.create_file('.env.example', '''DEBUG=1
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://postgres:postgres@localhost:5432/postgres
REDIS_URL=redis://localhost:6379/0
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

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
''')

        # Create README.md with Python 3.13 note
        self.create_file('README.md', f'''# {self.project_name}

A Django project with REST framework and PostgreSQL.

## Important Note for Python 3.13 Users

This project template has been configured for Python 3.13 compatibility. However, some image processing features that depend on Pillow are currently disabled as Pillow is not yet fully compatible with Python 3.13. If you need image processing capabilities, consider:

1. Using Python 3.11 or 3.12 instead
2. Waiting for Pillow to release a Python 3.13 compatible version
3. Using alternative image processing libraries

## Prerequisites

- Python 3.13
- PostgreSQL 12 or higher

## Installation

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
{self.project_name}/
├── apps/                   # Django applications
│   ├── core/              # Core functionality
│   └── users/             # User management
├── config/                # Project configuration
├── static/                # Static files
├── media/                 # User-uploaded files
├── templates/             # HTML templates
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Check style: `flake8`
- Sort imports: `isort .`

## Deployment

1. Set up your production environment variables
2. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Start the Gunicorn server:
   ```bash
   gunicorn config.wsgi:application
   ```

## License

This project is licensed under the MIT License.
''')

        # Print success message
        self.print_success_message([
            f"cd {self.project_name}",
            "python -m venv venv",
            "source venv/bin/activate  # On Windows: venv\\Scripts\\activate",
            "pip install -r requirements.txt",
            "cp .env.example .env  # Configure your environment variables",
            "python manage.py migrate",
            "python manage.py runserver",
            "\nThen open [link]http://localhost:8000[/link] in your browser",
            "\n[dim]Note: Image processing features are currently disabled for Python 3.13 compatibility.[/]"
        ]) 