"""
Authentication feature handler for Stackmate.
"""

import os
import json
from typing import Dict, Optional
from ..utils.dependency_manager import DependencyManager

async def add_auth(project_dir: str) -> None:
    """Add authentication to an existing project."""
    # Read package.json to determine project type and dependencies
    try:
        with open(os.path.join(project_dir, 'package.json'), 'r') as f:
            package_json = json.load(f)
    except FileNotFoundError:
        raise Exception("No package.json found. Make sure you're in a Node.js project directory.")

    deps = package_json.get('dependencies', {})
    
    # Determine the auth strategy based on existing dependencies
    auth_strategy = determine_auth_strategy(deps)
    
    # Initialize dependency manager
    dep_manager = DependencyManager()
    
    # Add required dependencies based on auth strategy
    new_deps = await get_auth_dependencies(auth_strategy, dep_manager)
    
    # Update package.json
    package_json['dependencies'].update(new_deps)
    with open(os.path.join(project_dir, 'package.json'), 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Create auth configuration files
    await create_auth_config(project_dir, auth_strategy)
    
    print(f"\nAuthentication ({auth_strategy}) has been added to your project!")
    print("\nNext steps:")
    print("1. npm install")
    print("2. Configure your environment variables")
    if auth_strategy == "next-auth":
        print("3. Add your OAuth providers in src/app/api/auth/[...nextauth]/route.ts")
    elif auth_strategy == "clerk":
        print("3. Set up your Clerk Dashboard and add your API keys")
    elif auth_strategy == "firebase":
        print("3. Add your Firebase configuration in src/lib/firebase.ts")

def determine_auth_strategy(deps: Dict[str, str]) -> str:
    """Determine the best auth strategy based on existing dependencies."""
    if "next" in deps:
        if "@prisma/client" in deps:
            return "next-auth"  # Next.js + Prisma = NextAuth.js
        elif "@clerk/nextjs" in deps:
            return "clerk"  # Already using Clerk
        else:
            return "next-auth"  # Default for Next.js
    elif "firebase" in deps:
        return "firebase"  # Already using Firebase
    else:
        return "next-auth"  # Default choice

async def get_auth_dependencies(strategy: str, dep_manager: DependencyManager) -> Dict[str, str]:
    """Get required dependencies for the chosen auth strategy."""
    deps = {}
    
    if strategy == "next-auth":
        base_deps = {
            "next-auth": "^4.24.5",
            "@prisma/client": "^5.8.0",
        }
        deps_analysis = await dep_manager.analyze_dependencies(base_deps)
        deps = deps_analysis["updated_dependencies"]
        
    elif strategy == "clerk":
        base_deps = {
            "@clerk/nextjs": "^4.29.1",
            "@clerk/themes": "^1.7.9",
        }
        deps_analysis = await dep_manager.analyze_dependencies(base_deps)
        deps = deps_analysis["updated_dependencies"]
        
    elif strategy == "firebase":
        base_deps = {
            "firebase": "^10.7.1",
            "firebase-admin": "^12.0.0",
            "react-firebase-hooks": "^5.1.1",
        }
        deps_analysis = await dep_manager.analyze_dependencies(base_deps)
        deps = deps_analysis["updated_dependencies"]
    
    return deps

async def create_auth_config(project_dir: str, strategy: str) -> None:
    """Create authentication configuration files."""
    if strategy == "next-auth":
        # Create NextAuth.js API route
        os.makedirs(os.path.join(project_dir, 'src/app/api/auth/[...nextauth]'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/app/api/auth/[...nextauth]/route.ts'), 'w') as f:
            f.write('''import NextAuth from "next-auth"
import { authOptions } from "@/lib/auth"

const handler = NextAuth(authOptions)
export { handler as GET, handler as POST }''')

        # Create auth configuration
        os.makedirs(os.path.join(project_dir, 'src/lib'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/lib/auth.ts'), 'w') as f:
            f.write('''import { PrismaAdapter } from "@next-auth/prisma-adapter"
import { type NextAuthOptions } from "next-auth"
import GithubProvider from "next-auth/providers/github"
import GoogleProvider from "next-auth/providers/google"
import { prisma } from "./db"

export const authOptions: NextAuthOptions = {
  adapter: PrismaAdapter(prisma),
  session: {
    strategy: "jwt",
  },
  pages: {
    signIn: "/auth/signin",
  },
  providers: [
    GithubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    GoogleProvider({
      clientId: process.env.GOOGLE_ID!,
      clientSecret: process.env.GOOGLE_SECRET!,
    }),
  ],
  callbacks: {
    async session({ token, session }) {
      if (token) {
        session.user.id = token.id
        session.user.name = token.name
        session.user.email = token.email
        session.user.image = token.picture
      }

      return session
    },
    async jwt({ token, user }) {
      const dbUser = await prisma.user.findFirst({
        where: {
          email: token.email,
        },
      })

      if (!dbUser) {
        if (user) {
          token.id = user?.id
        }
        return token
      }

      return {
        id: dbUser.id,
        name: dbUser.name,
        email: dbUser.email,
        picture: dbUser.image,
      }
    },
  },
}''')

        # Create Prisma schema if it doesn't exist
        os.makedirs(os.path.join(project_dir, 'prisma'), exist_ok=True)
        if not os.path.exists(os.path.join(project_dir, 'prisma/schema.prisma')):
            with open(os.path.join(project_dir, 'prisma/schema.prisma'), 'w') as f:
                f.write('''generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String?   @unique
  emailVerified DateTime?
  image         String?
  accounts      Account[]
  sessions      Session[]
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}''')

    elif strategy == "clerk":
        # Create Clerk middleware
        with open(os.path.join(project_dir, 'middleware.ts'), 'w') as f:
            f.write('''import { authMiddleware } from "@clerk/nextjs"

export default authMiddleware({
  publicRoutes: ["/", "/api/public(.*)"],
})

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
}''')

        # Create auth utils
        os.makedirs(os.path.join(project_dir, 'src/lib'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/lib/auth.ts'), 'w') as f:
            f.write('''import { currentUser } from "@clerk/nextjs"
import { redirect } from "next/navigation"

export async function getUser() {
  const user = await currentUser()
  
  if (!user) {
    redirect("/sign-in")
  }
  
  return user
}''')

    elif strategy == "firebase":
        # Create Firebase configuration
        os.makedirs(os.path.join(project_dir, 'src/lib'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/lib/firebase.ts'), 'w') as f:
            f.write('''import { initializeApp, getApps } from "firebase/app"
import { getAuth } from "firebase/auth"
import { getFirestore } from "firebase/firestore"

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
}

// Initialize Firebase
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0]
const auth = getAuth(app)
const db = getFirestore(app)

export { app, auth, db }''')

        # Create auth hooks
        with open(os.path.join(project_dir, 'src/lib/auth-hooks.ts'), 'w') as f:
            f.write('''import { useEffect, useState } from "react"
import { User } from "firebase/auth"
import { auth } from "./firebase"

export function useUser() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    return auth.onAuthStateChanged((user) => {
      setUser(user)
      setLoading(false)
    })
  }, [])

  return { user, loading }
}''')

    # Update .env.example with auth-specific variables
    env_vars = []
    if strategy == "next-auth":
        env_vars.extend([
            "DATABASE_URL=postgresql://user:password@localhost:5432/your-database",
            "NEXTAUTH_URL=http://localhost:3000",
            "NEXTAUTH_SECRET=your-secret-key",
            "GITHUB_ID=your-github-client-id",
            "GITHUB_SECRET=your-github-client-secret",
            "GOOGLE_ID=your-google-client-id",
            "GOOGLE_SECRET=your-google-client-secret",
        ])
    elif strategy == "clerk":
        env_vars.extend([
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your-publishable-key",
            "CLERK_SECRET_KEY=your-secret-key",
        ])
    elif strategy == "firebase":
        env_vars.extend([
            "NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key",
            "NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-auth-domain",
            "NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id",
            "NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-storage-bucket",
            "NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id",
            "NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id",
        ])

    env_example_path = os.path.join(project_dir, '.env.example')
    try:
        with open(env_example_path, 'r') as f:
            existing_vars = f.read().splitlines()
    except FileNotFoundError:
        existing_vars = []

    # Add new variables while preserving existing ones
    all_vars = list(set(existing_vars + env_vars))
    with open(env_example_path, 'w') as f:
        f.write('\n'.join(all_vars) + '\n') 