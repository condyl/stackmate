"""
Stackmate template system for generating project stacks.
"""

from .base import BaseTemplate
from .modern_react import ModernReactTemplate
from .t3 import T3Template
from .enterprise_react import EnterpriseReactTemplate
from .jamstack import JamstackTemplate
from .custom import CustomTemplate
from .django import DjangoTemplate
from .flask import FlaskTemplate
from .fastapi import FastAPITemplate

# Available stack choices
AVAILABLE_STACKS = [
    'modern-react',    # Next.js + Tailwind + Shadcn
    't3',             # Full-Stack T3
    'enterprise-react',
    'jamstack-blog',
    'django',         # Django + DRF + PostgreSQL
    'flask',          # Flask + SQLAlchemy + PostgreSQL
    'fastapi',        # FastAPI + Pydantic
    'custom',         # AI-generated custom stack
]

# Template registry
TEMPLATES = {
    'modern-react': ModernReactTemplate,
    't3': T3Template,
    'enterprise-react': EnterpriseReactTemplate,
    'jamstack-blog': JamstackTemplate,
    'django': DjangoTemplate,
    'flask': FlaskTemplate,
    'fastapi': FastAPITemplate,
    'custom': CustomTemplate,
} 