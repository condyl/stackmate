"""
T3 Stack template using Next.js, tRPC, Prisma, and NextAuth.
"""

import os
from .base import BaseTemplate

class T3Template(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "next": "^14.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "@prisma/client": "^5.8.0",
            "@tanstack/react-query": "^4.36.1",
            "@trpc/client": "^10.45.0",
            "@trpc/next": "^10.45.0",
            "@trpc/react-query": "^10.45.0",
            "@trpc/server": "^10.45.0",
            "next-auth": "^4.24.5",
            "@next-auth/prisma-adapter": "^1.0.7",
            "superjson": "^2.2.1",
            "zod": "^3.22.4",
            "tailwindcss": "^3.4.0",
            "postcss": "^8.4.31",
            "autoprefixer": "^10.4.16",
        }

    @property
    def dev_dependencies(self) -> dict:
        return {
            "typescript": "^5.0.0",
            "@types/node": "^20.0.0",
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "prisma": "^5.8.0",
            "eslint": "^8.56.0",
            "eslint-config-next": "14.0.0",
            "prettier": "^3.1.0",
            "@typescript-eslint/parser": "^6.18.0",
            "@typescript-eslint/eslint-plugin": "^6.18.0",
        }

    async def generate(self) -> None:
        """Generate the project structure."""
        self.create_project_directory()
        
        # Create package.json with smart dependency management
        await self.create_package_json()
        
        # Create configuration files
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

        self.create_file('next.config.js', '''/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig''')

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

        # Create Prisma schema
        self.create_file('prisma/schema.prisma', '''generator client {
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

        # Create tRPC setup
        self.create_file('src/server/api/trpc.ts', '''import { initTRPC, TRPCError } from "@trpc/server";
import { type CreateNextContextOptions } from "@trpc/server/adapters/next";
import { type Session } from "next-auth";
import superjson from "superjson";
import { ZodError } from "zod";
import { getServerAuthSession } from "@/server/auth";
import { prisma } from "@/server/db";

type CreateContextOptions = {
  session: Session | null;
};

const createInnerTRPCContext = (opts: CreateContextOptions) => {
  return {
    session: opts.session,
    prisma,
  };
};

export const createTRPCContext = async (opts: CreateNextContextOptions) => {
  const { req, res } = opts;
  const session = await getServerAuthSession({ req, res });
  return createInnerTRPCContext({ session });
};

const t = initTRPC.context<typeof createTRPCContext>().create({
  transformer: superjson,
  errorFormatter({ shape, error }) {
    return {
      ...shape,
      data: {
        ...shape.data,
        zodError:
          error.cause instanceof ZodError ? error.cause.flatten() : null,
      },
    };
  },
});

export const createTRPCRouter = t.router;
export const publicProcedure = t.procedure;

const enforceUserIsAuthed = t.middleware(({ ctx, next }) => {
  if (!ctx.session?.user) {
    throw new TRPCError({ code: "UNAUTHORIZED" });
  }
  return next({
    ctx: {
      session: { ...ctx.session, user: ctx.session.user },
    },
  });
});

export const protectedProcedure = t.procedure.use(enforceUserIsAuthed);''')

        # Create NextAuth setup
        self.create_file('src/server/auth.ts', '''import { PrismaAdapter } from "@next-auth/prisma-adapter";
import { type GetServerSidePropsContext } from "next";
import {
  getServerSession,
  type DefaultSession,
  type NextAuthOptions,
} from "next-auth";
import { prisma } from "@/server/db";

declare module "next-auth" {
  interface Session extends DefaultSession {
    user: DefaultSession["user"] & {
      id: string;
    };
  }
}

export const authOptions: NextAuthOptions = {
  callbacks: {
    session: ({ session, user }) => ({
      ...session,
      user: {
        ...session.user,
        id: user.id,
      },
    }),
  },
  adapter: PrismaAdapter(prisma),
  providers: [
    // Add providers here
  ],
};

export const getServerAuthSession = (ctx: {
  req: GetServerSidePropsContext["req"];
  res: GetServerSidePropsContext["res"];
}) => {
  return getServerSession(ctx.req, ctx.res, authOptions);
};''')

        # Create database client
        self.create_file('src/server/db.ts', '''import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log:
      process.env.NODE_ENV === "development" ? ["query", "error", "warn"] : ["error"],
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;''')

        # Create basic app structure
        self.create_file('src/app/layout.tsx', '''import { type Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'T3 Stack App',
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
      <h1 className="text-4xl font-bold">Welcome to T3 Stack</h1>
      <p className="mt-4 text-xl">Get started by editing src/app/page.tsx</p>
    </main>
  )
}''')

        # Create README.md
        self.create_file('README.md', f'''# {self.project_name}

A full-stack application built with the T3 Stack.

## Features

- Next.js 14 with App Router
- tRPC for type-safe APIs
- Prisma for database access
- NextAuth.js for authentication
- TypeScript for type safety
- Tailwind CSS for styling
- Modern development tooling

## Prerequisites

- Node.js 18+
- PostgreSQL database
- npm or yarn

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` with your database and authentication settings.

3. Initialize the database:
   ```bash
   npx prisma generate
   npx prisma db push
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
{self.project_name}/
├── prisma/             # Database schema and migrations
├── src/
│   ├── app/           # Next.js app router
│   │   ├── server/  # Backend code
│   │   │   ├── api/ # tRPC procedures
│   │   │   ├── auth.ts # Authentication setup
│   │   │   └── db.ts # Database client
│   │   └── utils/   # Shared utilities
│   └── public/        # Static assets
└── README.md          # Project documentation
```

## Development

- Run development server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm run start`
- Run linter: `npm run lint`
- Update database schema: `npx prisma db push`

## Learn More

- [T3 Stack Documentation](https://create.t3.gg)
- [Next.js Documentation](https://nextjs.org/docs)
- [tRPC Documentation](https://trpc.io)
- [Prisma Documentation](https://www.prisma.io/docs)
- [NextAuth.js Documentation](https://next-auth.js.org)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## License

This project is licensed under the MIT License.
''')

        # Create .env.example
        self.create_file('.env.example', '''# Database URL for PostgreSQL
DATABASE_URL="postgresql://user:password@localhost:5432/your-database"

# NextAuth.js
NEXTAUTH_SECRET="your-secret-key"
NEXTAUTH_URL="http://localhost:3000"

# Add your OAuth provider credentials here
# Example for GitHub:
# GITHUB_ID="your-github-client-id"
# GITHUB_SECRET="your-github-client-secret"''')

        # Create .gitignore
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
next-env.d.ts

# Prisma
/prisma/*.db
/prisma/migrations/''')

        # Print success message
        self.print_success_message([
            f"cd {self.project_name}",
            "npm install",
            "cp .env.example .env  # Configure your environment variables",
            "npx prisma generate   # Generate Prisma client",
            "npx prisma db push    # Push database schema",
            "npm run dev",
            "\nThen open [link]http://localhost:3000[/link] in your browser",
            "\n[dim]Note: Make sure your database is running and configured in .env[/]"
        ]) 