"""
Express.js template for simple web applications.
"""

import os
from .base import BaseTemplate

class ExpressTemplate(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "express": "^4.18.2",
            "cors": "^2.8.5",
            "dotenv": "^16.3.1",
            "morgan": "^1.10.0",
        }

    @property
    def dev_dependencies(self) -> dict:
        return {
            "nodemon": "^3.0.2",
            "eslint": "^8.56.0",
            "prettier": "^3.1.0",
        }

    async def generate(self) -> None:
        """Generate a basic Express.js project structure."""
        self.create_project_directory()

        # Create project structure
        dirs = [
            "src",
            "src/routes",
            "src/middleware",
            "src/utils",
        ]
        for dir_path in dirs:
            os.makedirs(os.path.join(self.project_dir, dir_path), exist_ok=True)

        # Create package.json with custom scripts
        await self.create_package_json({
            "scripts": {
                "start": "node src/index.js",
                "dev": "nodemon src/index.js",
                "lint": "eslint .",
                "format": "prettier --write ."
            }
        })

        # Create main application file
        self.create_file('src/index.js', '''require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const routes = require('./routes');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(morgan('dev'));
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.use('/', routes);

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something broke!' });
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});''')

        # Create routes
        self.create_file('src/routes/index.js', '''const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
  res.json({ message: 'Welcome to Express' });
});

router.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

module.exports = router;''')

        # Create example middleware
        self.create_file('src/middleware/logger.js', '''function logRequest(req, res, next) {
  console.log(`${req.method} ${req.url}`);
  next();
}

module.exports = logRequest;''')

        # Create utility functions
        self.create_file('src/utils/helpers.js', '''function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

module.exports = {
  asyncHandler,
};''')

        # Create configuration files
        self.create_file('.env.example', '''PORT=3000
NODE_ENV=development''')

        # Create ESLint configuration
        self.create_file('.eslintrc.json', '''{
  "env": {
    "node": true,
    "es2021": true
  },
  "extends": "eslint:recommended",
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "indent": ["error", 2],
    "linebreak-style": ["error", "unix"],
    "quotes": ["error", "single"],
    "semi": ["error", "always"]
  }
}''')

        # Create Prettier configuration
        self.create_file('.prettierrc', '''{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}''')

        # Create README
        self.create_file('README.md', f'''# {self.project_name}

A simple Express.js web application.

## Features

- Express.js 4.18+ setup
- CORS enabled
- Request logging with Morgan
- Environment variables with dotenv
- ESLint + Prettier for code quality
- Development mode with Nodemon

## Prerequisites

- Node.js 18+
- npm or yarn

## Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   The server will be running on [http://localhost:3000](http://localhost:3000).

## Project Structure

```
{self.project_name}/
├── src/
│   ├── routes/        # Route definitions
│   ├── middleware/    # Custom middleware
│   ├── utils/         # Utility functions
│   └── index.js       # Application entry point
└── .env              # Environment variables
```

## Available Scripts

- `npm start`: Run the server
- `npm run dev`: Run the server in development mode with hot reload
- `npm run lint`: Check code style
- `npm run format`: Format code

## API Endpoints

- `GET /`: Welcome message
- `GET /health`: Health check endpoint

## Development

1. Make your changes
2. Format code: `npm run format`
3. Check for linting errors: `npm run lint`
4. Test your changes
5. Commit and push

## License

This project is licensed under the MIT License.
''')

        # Create .gitignore
        self.create_file('.gitignore', '''# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db''')

        print(f"\nProject {self.project_name} created successfully!")
        print("\nNext steps:")
        print("1. cd", self.project_name)
        print("2. npm install")
        print("3. cp .env.example .env")
        print("4. npm run dev")
        print("\nThen open http://localhost:3000 in your browser") 