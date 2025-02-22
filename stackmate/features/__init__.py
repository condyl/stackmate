"""
Feature addition system for Stackmate.
"""

from .auth import add_auth
from .components import add_components
from .tools import add_tools

# Available features and their handlers
AVAILABLE_FEATURES = {
    'auth': add_auth,
    'components': add_components,
    'tools': add_tools,
}

__all__ = ['AVAILABLE_FEATURES'] 