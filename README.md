# Stackmate

A powerful CLI tool for generating modern web applications with AI-powered stack recommendations and best practices.

## Features

- 🤖 AI-powered stack analysis and recommendations
- 📦 Multiple pre-configured stack templates
- 🛠️ Custom stack generation based on project requirements
- ⚡ Quick setup with best practices
- 🔒 Secure configuration handling
- 📚 Comprehensive documentation generation

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package installer)
- Node.js and npm (for generated projects)
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/condyl/stackmate.git
   cd stackmate
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

4. Set up your environment variables:
   ```bash
   # Required
   export GEMINI_API_KEY=your_api_key  # Get from https://makersuite.google.com/app/apikey
   ```

## Usage

### Create a New Project

1. Using AI Analysis:
   ```bash
   stackmate new my-app --describe "I need a modern web app with authentication, blog functionality, and a newsletter system"
   ```

2. Using Pre-configured Templates:
   ```bash
   stackmate new my-app --stack modern-react
   ```

### Available Stack Templates

- `modern-react`: Next.js + Tailwind + Shadcn
- `t3`: Full-Stack T3 Stack (Next.js, tRPC, Prisma, NextAuth)
- `enterprise-react`: Enterprise-grade React setup
- `jamstack-blog`: JAMstack blog with MDX and Contentlayer
- `custom`: AI-generated custom stack based on requirements

### Add Features to Existing Project

```bash
stackmate add auth
stackmate add components
stackmate add tools
```

### Customize Project

```bash
stackmate customize
```

## Project Structure

```
stackmate/
├── stackmate/
│   ├── ai/              # AI integration components
│   ├── templates/       # Stack templates
│   ├── cli.py          # CLI implementation
│   └── __init__.py     # Package initialization
├── tests/              # Test suite
├── setup.py           # Package setup
└── README.md          # Documentation
```

## Development

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black stackmate
   ```

4. Check types:
   ```bash
   mypy stackmate
   ```

## Troubleshooting

### Common Issues

1. **GEMINI_API_KEY not set**
   ```bash
   Error: GEMINI_API_KEY environment variable not set
   Solution: Export your API key as shown in the installation section
   ```

2. **Stack generation fails**
   ```bash
   Error during AI analysis
   Solution: Check your internet connection and API key validity
   ```

3. **gRPC warning messages**
   ```bash
   WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
   Solution: This is a known issue with the Gemini API client and can be safely ignored
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google's Gemini API for AI capabilities
- The amazing open-source community
- All contributors who have helped shape this project 
