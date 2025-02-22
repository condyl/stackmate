"""
Code generator using Google's Gemini model for generating project code and configurations.
"""

import google.generativeai as genai
from typing import Dict, List, Optional

class CodeGenerator:
    def __init__(self, api_key: str):
        """Initialize the code generator with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def generate_component(self, 
                               description: str, 
                               stack: Dict,
                               component_type: str) -> str:
        """Generate a component based on description and stack."""
        prompt = f"""
        Generate a {component_type} component with the following requirements:
        
        Description: {description}
        Tech Stack: {stack}
        
        Consider:
        1. Best practices for the specified stack
        2. Type safety and error handling
        3. Performance optimization
        4. Component reusability
        5. Testing considerations
        
        Return the complete code for the component.
        """
        
        # Generate content synchronously since the API doesn't support async
        response = self.model.generate_content(prompt)
        return response.text
        
    async def generate_configuration(self, 
                                   stack: Dict,
                                   config_type: str) -> str:
        """Generate configuration files for the project."""
        prompt = f"""
        Generate {config_type} configuration for the following stack:
        
        {stack}
        
        Consider:
        1. Best practices for the stack
        2. Security considerations
        3. Development vs production settings
        4. Common configuration patterns
        5. Documentation needs
        
        Return the complete configuration file content.
        """
        
        # Generate content synchronously
        response = self.model.generate_content(prompt)
        return response.text
        
    async def generate_documentation(self,
                                   project_info: Dict,
                                   doc_type: str) -> str:
        """Generate project documentation."""
        prompt = f"""
        Generate {doc_type} documentation for the following project:
        
        {project_info}
        
        Include:
        1. Project overview
        2. Setup instructions
        3. Architecture overview
        4. API documentation (if applicable)
        5. Development guidelines
        6. Deployment instructions
        
        Format the documentation in Markdown.
        """
        
        # Generate content synchronously
        response = self.model.generate_content(prompt)
        return response.text
        
    async def optimize_code(self, 
                          code: str,
                          optimization_goals: List[str]) -> str:
        """Optimize existing code based on specified goals."""
        prompt = f"""
        Optimize the following code according to these goals:
        
        Code:
        {code}
        
        Optimization Goals:
        {"\n".join(optimization_goals)}
        
        Consider:
        1. Performance improvements
        2. Code readability
        3. Best practices
        4. Memory usage
        5. Error handling
        
        Return the optimized code with comments explaining the changes.
        """
        
        # Generate content synchronously
        response = self.model.generate_content(prompt)
        return response.text 