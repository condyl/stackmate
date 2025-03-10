"""
Stack analyzer using Google's Gemini model for project requirement analysis.
"""

import google.generativeai as genai
import json
from typing import Dict, List, Optional, Tuple

class StackAnalyzer:
    def __init__(self, api_key: str):
        """Initialize the stack analyzer with Gemini API key."""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def _select_template(self, analysis: Dict) -> str:
        """Select the most appropriate template based on analysis results."""
        stack = analysis.get("stack", {})
        characteristics = analysis.get("project_characteristics", {})
        
        # Extract key information
        framework = stack.get("framework", "").lower()
        database = stack.get("database", "").lower()
        features = str(stack).lower()  # Convert entire stack to lowercase for searching
        description = str(analysis.get("reasoning", {})).lower()  # Include reasoning in analysis
        
        # Helper function to check if any keyword is in a string
        def has_keywords(text: str, keywords: List[str]) -> bool:
            return any(keyword in text for keyword in keywords)
        
        # Helper function to check if text is primarily about a topic
        def is_primarily_about(text: str, keywords: List[str], threshold: int = 2) -> bool:
            return sum(1 for keyword in keywords if keyword in text) >= threshold
        
        # First, check for real-time applications
        realtime_indicators = ["real-time", "realtime", "real time", "live", "streaming", "websocket", "concurrent"]
        if (characteristics.get("real_time") or 
            is_primarily_about(features + " " + description, realtime_indicators)):
            return "fastapi" if "python" in features else "expressjs"
        
        # Then check for blog/content-focused projects
        blog_indicators = ["blog", "mdx", "cms", "content management", "articles", "posts", "writing"]
        if (characteristics.get("content_focus") and 
            is_primarily_about(features + " " + description, blog_indicators)):
            return "jamstack-blog"
        
        # Check for enterprise requirements
        if characteristics.get("enterprise_grade"):
            if has_keywords(features, ["react", "next"]):
                return "enterprise-react"
        
        # Check for specific backend frameworks
        backend_indicators = {
            "django": ["django", "drf", "rest framework"],
            "flask": ["flask", "sqlalchemy"],
            "fastapi": ["fastapi", "pydantic", "async"],
            "expressjs": ["express", "node", "javascript backend"]
        }
        
        for template, keywords in backend_indicators.items():
            if has_keywords(framework + " " + features, keywords):
                return template
        
        # Check for specific frontend patterns
        if has_keywords(features, ["trpc", "prisma", "next"]) or "t3" in features:
            return "t3"
        
        # Check for specific project types
        if characteristics.get("complexity") == "high" and has_keywords(features, ["react", "redux", "material"]):
            return "enterprise-react"
        
        # Analyze requirements for modern web apps
        if has_keywords(framework + " " + features, ["next", "react"]):
            # Check if it's an enterprise application
            if characteristics.get("enterprise_grade"):
                return "enterprise-react"
            # Default to modern-react for other React/Next.js apps
            return "modern-react"
        
        # If no specific matches but we have some characteristics
        if characteristics:
            if characteristics.get("enterprise_grade"):
                return "enterprise-react"
        
        # Default to modern-react if no specific match
        return "modern-react"
        
    async def analyze_requirements(self, description: str) -> Tuple[str, Dict]:
        """Analyze project requirements and suggest appropriate stack."""
        prompt = f"""
        Analyze the following project requirements and suggest the most appropriate tech stack.
        Be specific about framework choices based on the project characteristics.
        
        Project Description:
        {description}
        
        First, determine the project characteristics:
        1. Is this primarily a content-focused site (blog, documentation, articles)? Set content_focus accordingly.
        2. Does it require real-time features (live updates, streaming, WebSocket)? Set real_time accordingly.
        3. What's the scale (startup, small business, enterprise)?
        4. What's the complexity level (low, medium, high)?
        5. Is SEO critical for this project?
        6. Does it need enterprise-grade features (SSO, audit logs, etc.)?
        
        Then consider these aspects for stack selection:
        
        1. Core Framework Selection:
           - For content-heavy sites (blogs, documentation): Next.js, Gatsby
           - For complex enterprise apps: Next.js with Redux, Angular
           - For simple REST APIs: Express.js, FastAPI, Flask
           - For complex backend systems: Django, NestJS
           - For real-time apps: Express.js, FastAPI
           - For monolithic apps: Django, Ruby on Rails
        
        2. Database Selection:
           - For document-based data: MongoDB
           - For relational data: PostgreSQL, MySQL
           - For real-time data: Firebase, MongoDB
           - For caching: Redis
        
        3. Authentication Requirements:
           - For simple auth: NextAuth, Firebase Auth
           - For complex auth: Keycloak, Auth0
           - For enterprise: Azure AD, Okta
        
        4. UI Framework Selection:
           - For rapid development: Tailwind + shadcn/ui
           - For enterprise: Material UI, Chakra UI
           - For custom design: styled-components
           - For complex forms: React Hook Form, Formik
        
        5. API Architecture:
           - For simple CRUD: REST
           - For complex operations: GraphQL
           - For real-time: WebSocket
           - For type-safety: tRPC
        
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
            "project_characteristics": {{
                "scale": "string",
                "complexity": "string",
                "content_focus": "boolean",
                "real_time": "boolean",
                "seo_critical": "boolean",
                "enterprise_grade": "boolean"
            }},
            "additional_considerations": ["string"]
        }}

        IMPORTANT: 
        1. Ensure the response is valid JSON that can be parsed.
        2. Set project_characteristics accurately based on the requirements.
        3. Do not include any additional text before or after the JSON object.
        """
        
        # Generate content synchronously since the API doesn't support async
        response = self.model.generate_content(prompt)
        
        try:
            # Try to parse the response as JSON
            result = json.loads(response.text)
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
            except json.JSONDecodeError:
                # If still can't parse, return a default structure with error message
                result = {
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
                    "project_characteristics": {
                        "scale": "startup",
                        "complexity": "medium",
                        "content_focus": False,
                        "real_time": False,
                        "seo_critical": True,
                        "enterprise_grade": False
                    },
                    "additional_considerations": [
                        "Error occurred while analyzing requirements, using default modern stack",
                        f"Original error: {str(e)}"
                    ]
                }
        
        # Select appropriate template based on analysis
        template = self._select_template(result)
        
        return template, result
        
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

    async def analyze_project(self, project_analysis: Dict) -> Dict:
        """Analyze the current project setup and suggest improvements."""
        deps = project_analysis.get("dependencies", {})
        dev_deps = project_analysis.get("devDependencies", {})
        scripts = project_analysis.get("scripts", {})

        prompt = f"""You are a senior software architect analyzing a Node.js project. Analyze the following project setup and suggest improvements.

Project Setup:
Dependencies: {json.dumps(deps, indent=2)}
Dev Dependencies: {json.dumps(dev_deps, indent=2)}
Scripts: {json.dumps(scripts, indent=2)}

Provide a detailed analysis in the following JSON format. Each suggestion should be specific and actionable:

{{
  "workflow_improvements": [
    {{
      "category": "Testing",
      "suggestion": "Add Jest testing framework",
      "priority": "high",
      "implementation": "Run: npm install --save-dev jest @types/jest"
    }}
  ],
  "dependency_updates": [
    {{
      "package": "react",
      "current_version": "17.0.2",
      "suggested_version": "18.2.0",
      "reason": "Access to new features and performance improvements"
    }}
  ],
  "performance_suggestions": [
    {{
      "area": "Bundle Size",
      "issue": "Large initial bundle",
      "solution": "Implement code splitting with dynamic imports",
      "impact": "high"
    }}
  ],
  "dx_improvements": [
    {{
      "category": "TypeScript",
      "suggestion": "Enable strict mode",
      "benefit": "Catch more potential bugs at compile time"
    }}
  ],
  "best_practices": [
    {{
      "category": "Environment",
      "current_state": "No .env.example file",
      "recommendation": "Add .env.example with documentation"
    }}
  ]
}}

Focus on:
1. Missing essential dependencies or tools
2. Outdated versions that should be updated
3. Performance optimizations
4. Developer experience improvements
5. Security concerns
6. Best practices for modern web development

Keep suggestions specific and actionable. Include exact commands or steps in implementation details where relevant.

IMPORTANT: Ensure the response is a valid JSON object with the exact structure shown above. Do not include any text outside the JSON object."""

        # Generate content synchronously
        try:
            response = self.model.generate_content(prompt)
            
            # Try to parse the response as JSON
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError as e:
                # If parsing fails, try to clean up the response
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
                except json.JSONDecodeError:
                    # If still can't parse, generate a basic analysis
                    result = self._generate_basic_analysis(project_analysis)
            
            # Validate the structure of the response
            required_keys = ["workflow_improvements", "dependency_updates", "performance_suggestions", 
                           "dx_improvements", "best_practices"]
            
            if not all(key in result for key in required_keys):
                result = self._generate_basic_analysis(project_analysis)
            
            return result
            
        except Exception as e:
            return self._generate_basic_analysis(project_analysis)

    def _generate_basic_analysis(self, project_analysis: Dict) -> Dict:
        """Generate a basic analysis when AI response fails."""
        deps = project_analysis.get("dependencies", {})
        dev_deps = project_analysis.get("devDependencies", {})
        
        # Initialize the result structure
        result = {
            "workflow_improvements": [],
            "dependency_updates": [],
            "performance_suggestions": [],
            "dx_improvements": [],
            "best_practices": []
        }
        
        # Add basic workflow improvements
        if not any("test" in script for script in project_analysis.get("scripts", {}).keys()):
            result["workflow_improvements"].append({
                "category": "Testing",
                "suggestion": "Add testing framework",
                "priority": "high",
                "implementation": "npm install --save-dev jest @types/jest"
            })
        
        # Check for essential dev tools
        essential_dev_tools = {
            "typescript": "^5.0.0",
            "eslint": "^8.0.0",
            "prettier": "^3.0.0"
        }
        
        for tool, version in essential_dev_tools.items():
            if tool not in dev_deps:
                result["dependency_updates"].append({
                    "package": tool,
                    "current_version": "not installed",
                    "suggested_version": version,
                    "reason": f"Essential development tool for code quality"
                })
        
        # Add basic performance suggestion
        result["performance_suggestions"].append({
            "area": "Build",
            "issue": "No build optimization configuration",
            "solution": "Add build optimization settings",
            "impact": "medium"
        })
        
        # Add basic DX improvement
        if "typescript" not in dev_deps:
            result["dx_improvements"].append({
                "category": "TypeScript",
                "suggestion": "Add TypeScript support",
                "benefit": "Better type safety and developer experience"
            })
        
        # Add basic best practice
        result["best_practices"].append({
            "category": "Documentation",
            "current_state": "Missing or incomplete documentation",
            "recommendation": "Add README.md with setup and development instructions"
        })
        
        return result 