"""
Stack analyzer using Google's Gemini model for project requirement analysis.
"""

import google.generativeai as genai
import json
from typing import Dict, List, Optional

class StackAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the stack analyzer with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def analyze_requirements(self, description: str) -> Dict:
        """Analyze project requirements and suggest appropriate stack."""
        prompt = f"""
        Analyze the following project requirements and suggest an appropriate tech stack:
        
        {description}
        
        Consider the following aspects:
        1. Core framework and architecture
        2. Database requirements
        3. Authentication needs
        4. UI/UX requirements
        5. API requirements
        6. Performance considerations
        7. Scalability needs
        8. Development tooling
        
        Format the response as a JSON object with the following structure:
        {{
            "stack": {{
                "framework": "string",
                "database": "string",
                "auth": "string",
                "ui": ["string"],
                "api": ["string"],
                "tools": ["string"]
            }},
            "reasoning": {{
                "framework": "string",
                "database": "string",
                "auth": "string",
                "ui": "string",
                "api": "string"
            }},
            "additional_considerations": ["string"]
        }}

        IMPORTANT: Ensure the response is valid JSON that can be parsed. Do not include any additional text before or after the JSON object.
        """
        
        # Generate content synchronously since the API doesn't support async
        response = self.model.generate_content(prompt)
        
        try:
            # Try to parse the response as JSON
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError as e:
            # If parsing fails, try to clean up the response and parse again
            cleaned_text = response.text.strip()
            # Remove any markdown code block markers if present
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            try:
                result = json.loads(cleaned_text)
                return result
            except json.JSONDecodeError:
                # If still can't parse, return a default structure with error message
                return {
                    "stack": {
                        "framework": "next.js",
                        "database": "postgresql",
                        "auth": "next-auth",
                        "ui": ["tailwindcss", "shadcn-ui"],
                        "api": ["rest"],
                        "tools": ["typescript", "eslint", "prettier"]
                    },
                    "reasoning": {
                        "framework": "Modern, production-ready framework with good developer experience",
                        "database": "Reliable, scalable SQL database",
                        "auth": "Well-integrated authentication solution",
                        "ui": "Modern styling with component library",
                        "api": "Standard REST API for simplicity"
                    },
                    "additional_considerations": [
                        "Error occurred while analyzing requirements, using default modern stack",
                        f"Original error: {str(e)}"
                    ]
                }
        
    async def validate_stack(self, stack: Dict) -> List[str]:
        """Validate the suggested stack for compatibility and best practices."""
        stack_desc = "\n".join([f"{k}: {v}" for k, v in stack.items()])
        prompt = f"""
        Validate the following tech stack for compatibility and best practices:
        
        {stack_desc}
        
        Consider:
        1. Version compatibility between components
        2. Known issues or conflicts
        3. Production readiness
        4. Community support and maintenance
        5. Performance implications
        
        Return a list of potential issues or recommendations.
        """
        
        # Generate content synchronously
        response = self.model.generate_content(prompt)
        return response.text.split("\n")  # List of recommendations
        
    async def suggest_dependencies(self, stack: Dict) -> Dict[str, str]:
        """Suggest appropriate dependency versions for the stack."""
        stack_desc = "\n".join([f"{k}: {v}" for k, v in stack.items()])
        prompt = f"""
        Suggest appropriate dependency versions for the following tech stack:
        
        {stack_desc}
        
        Consider:
        1. Latest stable versions
        2. Version compatibility
        3. Security considerations
        4. LTS versions where applicable
        
        Format the response as a JSON object mapping dependencies to version strings.
        """
        
        # Generate content synchronously
        response = self.model.generate_content(prompt)
        return response.text  # Will be parsed as JSON by the caller 