"""
Feature addition system for Stackmate.
"""

from .auth import add_auth
from .components import add_components
from .tools import add_tools

class FeatureHandler:
    def __init__(self, project_dir: str):
        self.project_dir = project_dir

    async def add(self):
        pass

class AuthFeatureHandler(FeatureHandler):
    async def add(self):
        await add_auth(self.project_dir)

class ComponentsFeatureHandler(FeatureHandler):
    async def add(self):
        await add_components(self.project_dir)

class ToolsFeatureHandler(FeatureHandler):
    async def add(self):
        await add_tools(self.project_dir)

# Available features and their handlers
AVAILABLE_FEATURES = {
    'auth': AuthFeatureHandler,
    'components': ComponentsFeatureHandler,
    'tools': ToolsFeatureHandler,
}

__all__ = ['AVAILABLE_FEATURES'] 