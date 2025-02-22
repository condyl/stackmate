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
        if doc_type == "readme":
            prompt = f"""
            Generate a comprehensive README.md for the following project:
            
            {project_info}
            
            Include:
            1. Project Overview
               - Description
               - Key features
               - Tech stack overview
               - Live demo (if applicable)
            
            2. Prerequisites
               - Required software and tools
               - API keys and credentials
               - Development environment setup
            
            3. Installation
               - Step-by-step installation guide
               - Environment variables setup
               - Database initialization
               - Development server setup
            
            4. Project Structure
               - Directory organization
               - Key files and their purposes
               - Architecture overview
               - Component relationships
            
            5. Features
               - Detailed feature list
               - Usage examples
               - API endpoints (if applicable)
               - Configuration options
            
            6. Development
               - Getting started guide
               - Available scripts
               - Testing instructions
               - Code style and conventions
               - Contribution guidelines
            
            7. Deployment
               - Deployment prerequisites
               - Build instructions
               - Platform-specific guides
               - Environment configuration
            
            8. Troubleshooting
               - Common issues
               - Solutions and workarounds
               - Support resources
               - FAQ
            
            9. Security
               - Security best practices
               - Authentication setup
               - API key management
               - Data protection
            
            10. License & Credits
                - License information
                - Third-party credits
                - Contributors
                - Acknowledgments
            
            Format the documentation in Markdown with proper headings, code blocks, and formatting.
            """
        elif doc_type == "api":
            prompt = f"""
            Generate API documentation for the following project:
            
            {project_info}
            
            Include:
            1. API Overview
               - Base URL
               - Authentication methods
               - Rate limiting
               - Response formats
            
            2. Endpoints
               - Full endpoint list
               - Request/response examples
               - Query parameters
               - Request body schemas
            
            3. Authentication
               - Authentication methods
               - Token management
               - Permission levels
               - Security considerations
            
            4. Error Handling
               - Error codes
               - Error response format
               - Common error scenarios
               - Troubleshooting
            
            5. Examples
               - Code examples in multiple languages
               - Common use cases
               - Integration examples
               - Best practices
            
            Format the documentation in Markdown with proper headings, code blocks, and formatting.
            """
        elif doc_type == "deployment":
            prompt = f"""
            Generate deployment documentation for the following project:
            
            {project_info}
            
            Include:
            1. Deployment Overview
               - Supported platforms
               - System requirements
               - Architecture diagram
               - Performance considerations
            
            2. Prerequisites
               - Required accounts and services
               - Domain setup
               - SSL certificates
               - Environment preparation
            
            3. Build Process
               - Build configuration
               - Environment variables
               - Asset optimization
               - Output verification
            
            4. Deployment Steps
               - Platform-specific instructions
               - Configuration files
               - Database migration
               - Cache management
            
            5. Monitoring & Maintenance
               - Health checks
               - Logging setup
               - Backup procedures
               - Update process
            
            6. Scaling
               - Scaling strategies
               - Load balancing
               - Database scaling
               - Cache optimization
            
            7. Security
               - Security checklist
               - Firewall configuration
               - Access control
               - Data protection
            
            Format the documentation in Markdown with proper headings, code blocks, and formatting.
            """
        else:
            prompt = f"""
            Generate {doc_type} documentation for the following project:
            
            {project_info}
            
            Include:
            1. Overview and purpose
            2. Setup instructions
            3. Usage guidelines
            4. Configuration options
            5. Troubleshooting
            6. Additional resources
            
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