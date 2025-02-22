"""
Development tools feature handler for Stackmate.
"""

import os
import json
from typing import Dict, List
from ..utils.dependency_manager import DependencyManager

async def add_tools(project_dir: str) -> None:
    """Add development tools to an existing project."""
    try:
        # Read package.json to determine project type and dependencies
        try:
            with open(os.path.join(project_dir, 'package.json'), 'r') as f:
                package_json = json.load(f)
        except FileNotFoundError:
            raise Exception("No package.json found. Make sure you're in a Node.js project directory.")

        deps = package_json.get('dependencies', {})
        dev_deps = package_json.get('devDependencies', {})
        
        # Initialize dependency manager
        dep_manager = DependencyManager()
        
        # Add required development tools
        new_dev_deps = await get_dev_tool_dependencies(deps, dev_deps, dep_manager)
        
        # Update package.json
        if 'devDependencies' not in package_json:
            package_json['devDependencies'] = {}
        package_json['devDependencies'].update(new_dev_deps)
        
        # Add scripts
        if 'scripts' not in package_json:
            package_json['scripts'] = {}
        package_json['scripts'].update({
            "test": "jest",
            "test:watch": "jest --watch",
            "test:coverage": "jest --coverage",
            "lint": "eslint . --ext .js,.jsx,.ts,.tsx",
            "lint:fix": "eslint . --ext .js,.jsx,.ts,.tsx --fix",
            "format": "prettier --write .",
            "prepare": "husky install",
            "typecheck": "tsc --noEmit",
        })
        
        with open(os.path.join(project_dir, 'package.json'), 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create configuration files
        await create_tool_configs(project_dir)
        
        print("\nDevelopment tools have been added to your project!")
        print("\nNext steps:")
        print("1. npm install")
        print("2. npm run prepare  # Set up Git hooks")
        print("3. Start using the tools:")
        print("   - npm run test       # Run tests")
        print("   - npm run lint       # Check code style")
        print("   - npm run format     # Format code")
        print("   - npm run typecheck  # Check TypeScript")
    except Exception as e:
        raise Exception(f"Failed to add development tools: {str(e)}")

async def get_dev_tool_dependencies(deps: Dict[str, str], dev_deps: Dict[str, str], dep_manager: DependencyManager) -> Dict[str, str]:
    """Get required development tool dependencies."""
    base_dev_deps = {
        # TypeScript
        "typescript": "^5.0.0",
        "@types/node": "^20.0.0",
        "@types/react": "^18.2.0",
        "@types/react-dom": "^18.2.0",
        
        # Testing
        "jest": "^29.7.0",
        "@testing-library/react": "^14.1.2",
        "@testing-library/jest-dom": "^6.2.0",
        "@testing-library/user-event": "^14.5.1",
        "jest-environment-jsdom": "^29.7.0",
        
        # Linting
        "eslint": "^8.56.0",
        "eslint-config-next": "14.0.0",
        "@typescript-eslint/parser": "^6.18.0",
        "@typescript-eslint/eslint-plugin": "^6.18.0",
        "eslint-plugin-react": "^7.33.2",
        "eslint-plugin-react-hooks": "^4.6.0",
        "eslint-plugin-jsx-a11y": "^6.8.0",
        
        # Code formatting
        "prettier": "^3.1.0",
        "eslint-config-prettier": "^9.1.0",
        "eslint-plugin-prettier": "^5.1.2",
        
        # Git hooks
        "husky": "^8.0.3",
        "lint-staged": "^15.2.0",
    }
    
    deps_analysis = await dep_manager.analyze_dependencies(base_dev_deps)
    return deps_analysis["updated_dependencies"]

async def create_tool_configs(project_dir: str) -> None:
    """Create configuration files for development tools."""
    try:
        # ESLint configuration
        eslint_config = {
            "extends": [
                "next/core-web-vitals",
                "plugin:@typescript-eslint/recommended",
                "plugin:react/recommended",
                "plugin:react-hooks/recommended",
                "plugin:jsx-a11y/recommended",
                "prettier"
            ],
            "plugins": [
                "@typescript-eslint",
                "react",
                "jsx-a11y",
                "prettier"
            ],
            "rules": {
                "react/react-in-jsx-scope": "off",
                "react/prop-types": "off",
                "@typescript-eslint/explicit-module-boundary-types": "off",
                "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
                "prettier/prettier": "error"
            },
            "settings": {
                "react": {
                    "version": "detect"
                }
            }
        }
        with open(os.path.join(project_dir, '.eslintrc.json'), 'w') as f:
            json.dump(eslint_config, f, indent=2)

        # Prettier configuration
        prettier_config = {
            "semi": True,
            "singleQuote": True,
            "tabWidth": 2,
            "trailingComma": "es5",
            "printWidth": 100,
            "arrowParens": "avoid"
        }
        with open(os.path.join(project_dir, '.prettierrc'), 'w') as f:
            json.dump(prettier_config, f, indent=2)

        # VS Code settings
        os.makedirs(os.path.join(project_dir, '.vscode'), exist_ok=True)
        vscode_settings = {
            "editor.formatOnSave": True,
            "editor.defaultFormatter": "esbenp.prettier-vscode",
            "editor.codeActionsOnSave": {
                "source.fixAll.eslint": True
            },
            "[typescript]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "[typescriptreact]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode"
            },
            "typescript.tsdk": "node_modules/typescript/lib"
        }
        with open(os.path.join(project_dir, '.vscode/settings.json'), 'w') as f:
            json.dump(vscode_settings, f, indent=2)

        # Jest configuration
        jest_config = '''const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/types/**/*',
  ],
}

module.exports = createJestConfig(customJestConfig)'''
        with open(os.path.join(project_dir, 'jest.config.js'), 'w') as f:
            f.write(jest_config)

        # Jest setup
        jest_setup = '''import '@testing-library/jest-dom';'''
        with open(os.path.join(project_dir, 'jest.setup.js'), 'w') as f:
            f.write(jest_setup)

        # Husky configuration
        os.makedirs(os.path.join(project_dir, '.husky'), exist_ok=True)
        pre_commit_hook = '''#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

npx lint-staged'''
        with open(os.path.join(project_dir, '.husky/pre-commit'), 'w') as f:
            f.write(pre_commit_hook)
        os.chmod(os.path.join(project_dir, '.husky/pre-commit'), 0o755)

        # lint-staged configuration
        lint_staged_config = {
            "*.{js,jsx,ts,tsx}": [
                "eslint --fix",
                "prettier --write"
            ],
            "*.{json,md,yml,yaml}": [
                "prettier --write"
            ]
        }
        with open(os.path.join(project_dir, '.lintstagedrc'), 'w') as f:
            json.dump(lint_staged_config, f, indent=2)

        # TypeScript configuration (if not exists)
        if not os.path.exists(os.path.join(project_dir, 'tsconfig.json')):
            ts_config = {
                "compilerOptions": {
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [
                        {
                            "name": "next"
                        }
                    ],
                    "paths": {
                        "@/*": ["./src/*"]
                    }
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                "exclude": ["node_modules"]
            }
            with open(os.path.join(project_dir, 'tsconfig.json'), 'w') as f:
                json.dump(ts_config, f, indent=2)
    except Exception as e:
        raise Exception(f"Failed to create tool configurations: {str(e)}") 