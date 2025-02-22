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

    def generate(self) -> None:
        """Generate a T3 stack project structure."""
        self.create_project_directory()
        
        # 1. Create package.json with additional scripts
        self.create_package_json({
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                "prisma:studio": "prisma studio",
                "prisma:generate": "prisma generate",
                "prisma:migrate": "prisma migrate dev",
                "postinstall": "prisma generate"
            }
        })

        # 2. Create TypeScript configuration
        self.create_file('tsconfig.json', '''{
  "compilerOptions": {
    "target": "es2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "checkJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "noUncheckedIndexedAccess": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": [
    ".eslintrc.cjs",
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    "**/*.cjs",
    "**/*.mjs"
  ],
  "exclude": ["node_modules"]
}''')

        # 3. Create Next.js configuration
        self.create_file('next.config.mjs', '''/** @type {import("next").NextConfig} */
const config = {
  reactStrictMode: true,
  i18n: {
    locales: ["en"],
    defaultLocale: "en",
  },
};
export default config;''')

        # 4. Create Prisma schema
        self.create_file('prisma/schema.prisma', '''generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Example {
  id        String   @id @default(cuid())
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

// NextAuth.js Models
// https://next-auth.js.org/schemas/models
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
  user              User    @relation(fields: [userId], references: [id], onDelete: Cascade)

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

        # 5. Set up tRPC
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

        # Add example router
        self.create_file('src/server/api/root.ts', '''import { createTRPCRouter } from "@/server/api/trpc";
import { exampleRouter } from "@/server/api/routers/example";

export const appRouter = createTRPCRouter({
  example: exampleRouter,
});

export type AppRouter = typeof appRouter;''')

        # Add example router implementation
        self.create_file('src/server/api/routers/example.ts', '''import { z } from "zod";
import { createTRPCRouter, publicProcedure, protectedProcedure } from "@/server/api/trpc";

export const exampleRouter = createTRPCRouter({
  hello: publicProcedure
    .input(z.object({ text: z.string() }))
    .query(({ input }) => {
      return {
        greeting: `Hello ${input.text}`,
      };
    }),

  getSecretMessage: protectedProcedure.query(() => {
    return "you can now see this secret message!";
  }),
});''')

        # Add tRPC shared utilities
        self.create_file('src/trpc/shared.ts', '''import { type inferRouterInputs, type inferRouterOutputs } from "@trpc/server";
import { type AppRouter } from "@/server/api/root";
import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient();

export function getBaseUrl() {
  if (typeof window !== "undefined") return "";
  if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`;
  return `http://localhost:${process.env.PORT ?? 3000}`;
}

export function getUrl() {
  return `${getBaseUrl()}/api/trpc`;
}

/**
 * Inference helper for inputs.
 *
 * @example type HelloInput = RouterInputs['example']['hello']
 */
export type RouterInputs = inferRouterInputs<AppRouter>;

/**
 * Inference helper for outputs.
 *
 * @example type HelloOutput = RouterOutputs['example']['hello']
 */
export type RouterOutputs = inferRouterOutputs<AppRouter>;''')

        # Update tRPC client setup with imports
        self.create_file('src/trpc/react.tsx', '''import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createTRPCReact } from "@trpc/react-query";
import { loggerLink } from "@trpc/client";
import { httpBatchLink } from "@trpc/client";
import { type AppRouter } from "@/server/api/root";
import { getUrl, queryClient } from "./shared";

export const api = createTRPCReact<AppRouter>();

export function TRPCReactProvider(props: {
  children: React.ReactNode;
  headers: Headers | null;
}) {
  return (
    <QueryClientProvider client={queryClient}>
      <api.Provider
        client={api.createClient({
          links: [
            loggerLink({
              enabled: (opts) =>
                process.env.NODE_ENV === "development" ||
                (opts.direction === "down" && opts.result instanceof Error),
            }),
            httpBatchLink({
              url: getUrl(),
              headers() {
                const heads = new Map(props.headers);
                heads.set("x-trpc-source", "react");
                return Object.fromEntries(heads);
              },
            }),
          ],
        })}
      >
        {props.children}
      </api.Provider>
    </QueryClientProvider>
  );
}''')

        # Update tRPC server utils with imports
        self.create_file('src/trpc/server.ts', '''import { httpBatchLink } from "@trpc/client";
import { createTRPCProxyClient } from "@trpc/client";
import { type AppRouter } from "@/server/api/root";
import { getUrl } from "./shared";

export const api = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: getUrl(),
    }),
  ],
});''')

        # 6. Set up NextAuth
        self.create_file('src/server/auth.ts', '''import { type GetServerSidePropsContext } from "next";
import {
  getServerSession,
  type NextAuthOptions,
  type DefaultSession,
} from "next-auth";
import { PrismaAdapter } from "@next-auth/prisma-adapter";
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
  providers: [], // Add your providers here
};

export const getServerAuthSession = (ctx: {
  req: GetServerSidePropsContext["req"];
  res: GetServerSidePropsContext["res"];
}) => {
  return getServerSession(ctx.req, ctx.res, authOptions);
};''')

        # 7. Set up Prisma client
        self.create_file('src/server/db.ts', '''import { PrismaClient } from "@prisma/client";

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined;
};

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    log:
      process.env.NODE_ENV === "development"
        ? ["query", "error", "warn"]
        : ["error"],
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;''')

        # 8. Create basic app structure
        self.create_file('src/app/layout.tsx', '''import { type Metadata } from "next";
import { headers } from "next/headers";
import { TRPCReactProvider } from "@/trpc/react";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "T3 App",
  description: "Generated by Stackmate",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <TRPCReactProvider headers={headers()}>{children}</TRPCReactProvider>
      </body>
    </html>
  );
}''')

        self.create_file('src/app/page.tsx', '''import { getServerAuthSession } from "@/server/auth";
import { api } from "@/trpc/server";

export default async function Home() {
  const session = await getServerAuthSession();

  return (
    <main className="flex min-h-screen flex-col items-center justify-center">
      <div className="container flex flex-col items-center justify-center gap-12 px-4 py-16">
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-[5rem]">
          T3 App
        </h1>
        <div className="flex flex-col items-center gap-2">
          {session?.user ? (
            <p className="text-2xl">
              Logged in as {session.user.name}
            </p>
          ) : (
            <p className="text-2xl">
              Not logged in
            </p>
          )}
        </div>
      </div>
    </main>
  );
}''')

        # 9. Create environment files
        self.create_file('.env.example', '''# Since the ".env" file is gitignored, you can use the ".env.example"
# file to commit your env vars and use it as a reference
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/t3-app"

# Next Auth
# You can generate the secret via 'openssl rand -base64 32' on Linux
NEXTAUTH_SECRET=""
NEXTAUTH_URL="http://localhost:3000"''')

        self.create_file('.env', '''DATABASE_URL="postgresql://postgres:postgres@localhost:5432/t3-app"
NEXTAUTH_SECRET="your-secret-key"
NEXTAUTH_URL="http://localhost:3000"''')

        # 10. Create .gitignore
        self.create_file('.gitignore', '''# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# database
/prisma/db.sqlite
/prisma/db.sqlite-journal

# next.js
/.next/
/out/
next-env.d.ts

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# local env files
.env
.env*.local

# typescript
*.tsbuildinfo''')

        # 11. Create ESLint configuration
        self.create_file('.eslintrc.json', '''{
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "./tsconfig.json"
  },
  "plugins": ["@typescript-eslint"],
  "extends": ["next/core-web-vitals", "plugin:@typescript-eslint/recommended"],
  "rules": {
    "@typescript-eslint/consistent-type-imports": [
      "warn",
      {
        "prefer": "type-imports",
        "fixStyle": "inline-type-imports"
      }
    ]
  }
}''')

        # 12. Create Prettier configuration
        self.create_file('.prettierrc', '''{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": false,
  "tabWidth": 2,
  "useTabs": false
}''')

        # Add Tailwind CSS configuration
        self.create_file('tailwind.config.ts', '''import { type Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
} satisfies Config;''')

        self.create_file('postcss.config.js', '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}''')

        self.create_file('src/styles/globals.css', '''@tailwind base;
@tailwind components;
@tailwind utilities;''')

        print(f"\nProject {self.project_name} created successfully!")
        print("\nNext steps:")
        print("1. cd", self.project_name)
        print("2. npm install")
        print("3. Update .env with your database credentials and NextAuth secret")
        print("4. npx prisma db push")
        print("5. npm run dev") 