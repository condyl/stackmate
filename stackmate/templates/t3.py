"""
T3 Stack template using Next.js, tRPC, Prisma, and NextAuth.
"""

from .base import BaseTemplate

class T3Template(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "next": "^14.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "@prisma/client": "^5.8.0",
            "@tanstack/react-query": "^5.17.0",
            "@trpc/client": "^11.0.0",
            "@trpc/next": "^11.0.0",
            "@trpc/react-query": "^11.0.0",
            "@trpc/server": "^11.0.0",
            "next-auth": "^4.24.5",
            "superjson": "^2.2.1",
            "zod": "^3.22.4",
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
        # TODO: Implement project generation
        # 1. Create package.json
        # 2. Set up Next.js
        # 3. Configure Prisma
        # 4. Set up tRPC
        # 5. Configure NextAuth
        # 6. Add TypeScript configurations
        # 7. Set up ESLint and Prettier
        pass 