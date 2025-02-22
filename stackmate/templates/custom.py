"""
Custom template for AI-generated stacks.
"""

import os
from typing import Dict, Any
from .base import BaseTemplate

class CustomTemplate(BaseTemplate):
    def __init__(self, project_name: str, analysis: Dict[str, Any] = None):
        super().__init__(project_name)
        self.analysis = analysis or {}
        
    @property
    def dependencies(self) -> dict:
        """Dynamically determine dependencies based on AI analysis."""
        deps = {}
        stack = self.analysis.get("stack", {})
        
        # Core framework
        if "next.js" in stack.get("framework", "").lower():
            deps.update({
                "next": "^14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
            })
        
        # Database
        if "mongodb" in stack.get("database", "").lower():
            deps["mongodb"] = "^6.3.0"
            deps["mongoose"] = "^8.0.3"
        elif "postgresql" in stack.get("database", "").lower():
            deps["@prisma/client"] = "^5.7.1"
        
        # Authentication
        if "firebase" in stack.get("auth", "").lower():
            deps["firebase"] = "^10.7.1"
            deps["firebase-admin"] = "^12.0.0"
        elif "next-auth" in stack.get("auth", "").lower():
            deps["next-auth"] = "^4.24.5"
        
        # UI
        ui_libs = [lib.lower() for lib in stack.get("ui", [])]
        if "tailwind" in str(ui_libs).lower():
            deps.update({
                "tailwindcss": "^3.4.0",
                "postcss": "^8.4.31",
                "autoprefixer": "^10.4.16",
            })
        if "chakra" in str(ui_libs).lower():
            deps.update({
                "@chakra-ui/react": "^2.8.2",
                "@emotion/react": "^11.11.3",
                "@emotion/styled": "^11.11.0",
                "framer-motion": "^10.17.9",
            })
        
        # API
        api_libs = [lib.lower() for lib in stack.get("api", [])]
        if "graphql" in str(api_libs).lower():
            deps.update({
                "graphql": "^16.8.1",
                "apollo-server-micro": "^3.13.0",
            })
        if "express" in str(api_libs).lower():
            deps["express"] = "^4.18.2"
        
        return deps

    @property
    def dev_dependencies(self) -> dict:
        """Development dependencies based on the stack."""
        dev_deps = {
            "typescript": "^5.0.0",
            "@types/node": "^20.0.0",
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "eslint": "^8.56.0",
            "prettier": "^3.1.0",
        }
        
        stack = self.analysis.get("stack", {})
        
        # Database
        if "postgresql" in stack.get("database", "").lower():
            dev_deps["prisma"] = "^5.7.1"
        
        # Testing and development tools
        tools = [tool.lower() for tool in stack.get("tools", [])]
        if "jest" in str(tools).lower():
            dev_deps.update({
                "jest": "^29.7.0",
                "@testing-library/react": "^14.1.2",
                "@testing-library/jest-dom": "^6.2.0",
            })
        
        return dev_deps

    def generate(self) -> None:
        """Generate the project structure based on AI analysis."""
        self.create_project_directory()
        
        # 1. Create package.json
        self.create_package_json()
        
        # 2. Create TypeScript configuration
        self.create_file('tsconfig.json', '''{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
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
}''')

        # 3. Create Next.js configuration
        self.create_file('next.config.js', '''/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig''')

        # 4. Set up Tailwind if used
        if any("tailwind" in lib.lower() for lib in self.analysis.get("stack", {}).get("ui", [])):
            self.create_file('tailwind.config.js', '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}''')
            
            self.create_file('postcss.config.js', '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}''')

        # 5. Create basic app structure
        self.create_file('src/app/layout.tsx', '''import { type Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Custom Stack App',
  description: 'Generated by Stackmate',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}''')

        self.create_file('src/app/globals.css', '''@tailwind base;
@tailwind components;
@tailwind utilities;''')

        self.create_file('src/app/page.tsx', '''export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold">Welcome to Your Custom Stack</h1>
      <p className="mt-4 text-xl">Get started by editing src/app/page.tsx</p>
    </main>
  )
}''')

        # 6. Create API routes if needed
        if any(api in str(self.analysis.get("stack", {}).get("api", [])).lower() for api in ["graphql", "express"]):
            self.create_file('src/app/api/route.ts', '''import { NextResponse } from 'next/server'
 
export async function GET() {
  return NextResponse.json({ message: 'Hello World!' })
}''')

        # 7. Create auth configuration if needed
        auth_system = self.analysis.get("stack", {}).get("auth", "").lower()
        if "firebase" in auth_system:
            self.create_file('src/config/firebase.ts', '''// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  // TODO: Add your Firebase configuration
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);''')
        elif "next-auth" in auth_system:
            self.create_file('src/app/api/auth/[...nextauth]/route.ts', '''import NextAuth from "next-auth"

const handler = NextAuth({
  providers: [
    // TODO: Add your authentication providers
  ],
})

export { handler as GET, handler as POST }''')

        # 8. Create database configuration
        db_system = self.analysis.get("stack", {}).get("database", "").lower()
        if "mongodb" in db_system:
            self.create_file('src/lib/mongodb.ts', '''import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/your-database';

export const connectDB = async () => {
  try {
    await mongoose.connect(MONGODB_URI);
    console.log('Connected to MongoDB');
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
    process.exit(1);
  }
};''')
        elif "postgresql" in db_system:
            self.create_file('prisma/schema.prisma', '''generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// TODO: Add your models here''')

        # 9. Create README.md
        stack_info = "\n".join([f"- {k}: {v}" for k, v in self.analysis.get("stack", {}).items()])
        env_vars = ["GEMINI_API_KEY=your_api_key  # Get from https://makersuite.google.com/app/apikey"]
        
        # Add stack-specific environment variables
        stack = self.analysis.get("stack", {})
        if "mongodb" in stack.get("database", "").lower():
            env_vars.append("MONGODB_URI=mongodb://localhost:27017/your-database")
        elif "postgresql" in stack.get("database", "").lower():
            env_vars.append("DATABASE_URL=postgresql://user:password@localhost:5432/dbname")
        
        if "firebase" in stack.get("auth", "").lower():
            env_vars.extend([
                "FIREBASE_API_KEY=your_api_key",
                "FIREBASE_AUTH_DOMAIN=your_domain",
                "FIREBASE_PROJECT_ID=your_project_id",
                "FIREBASE_STORAGE_BUCKET=your_bucket",
                "FIREBASE_MESSAGING_SENDER_ID=your_sender_id",
                "FIREBASE_APP_ID=your_app_id"
            ])
        elif "next-auth" in stack.get("auth", "").lower():
            env_vars.extend([
                "NEXTAUTH_URL=http://localhost:3000",
                "NEXTAUTH_SECRET=your_secret_key  # Generate with: openssl rand -base64 32"
            ])

        self.create_file('README.md', f'''# {self.project_name}

This project was generated using Stackmate with the following stack:

{stack_info}

## Prerequisites

Before you begin, ensure you have the following installed:
- Node.js (v18 or higher)
- npm or yarn
- Git

## Environment Setup

1. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```

2. Configure the following environment variables in your `.env` file:
   ```
   {chr(10).join(env_vars)}
   ```

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up the database:
   {f"""
   ```bash
   npx prisma generate
   npx prisma db push
   ```
   """ if "postgresql" in stack.get("database", "").lower() else ""}
   {f"""
   - Start your MongoDB server
   - Update MONGODB_URI in .env if needed
   """ if "mongodb" in stack.get("database", "").lower() else ""}

3. Run the development server:
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
{self.project_name}/
├── src/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   ├── lib/             # Utility functions
│   └── styles/          # Global styles
├── public/              # Static assets
└── {".env.example and .env files" if env_vars else "configuration files"}
```

## Features

{chr(10).join(f"- {feature}" for feature in [
    "TypeScript for type safety",
    f"Authentication via {stack.get('auth', 'Not configured')}",
    f"Database: {stack.get('database', 'Not configured')}",
    f"UI Framework: {', '.join(stack.get('ui', ['Not configured']))}",
    f"API: {', '.join(stack.get('api', ['Not configured']))}"
])}

## Stack Details

{self.analysis.get("reasoning", {})}

## Additional Considerations

{self.analysis.get("additional_considerations", [])}

## Development

- Run development server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm run start`
- Run linter: `npm run lint`

## Environment Files

- `.env.example`: Template for environment variables
- `.env`: Local environment variables (git-ignored)
- `.env.production`: Production environment variables

## Deployment

1. Set up your deployment platform (Vercel recommended for Next.js)
2. Configure environment variables on your platform
3. Deploy using the platform's recommended method

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add my feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## Support

For issues and feature requests, please create an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
''')

        # Create .env.example with the same variables
        self.create_file('.env.example', "\n".join(env_vars))

        # 10. Create .gitignore
        self.create_file('.gitignore', '''# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local
.env

# typescript
*.tsbuildinfo
next-env.d.ts''')

        print(f"\nProject {self.project_name} created successfully!")
        print("\nNext steps:")
        print("1. cd", self.project_name)
        print("2. npm install")
        print("3. Configure your environment variables")
        print("4. npm run dev") 