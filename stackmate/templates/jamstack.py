"""
JAMstack Blog template using Next.js, MDX, Contentlayer, and more.
"""

from .base import BaseTemplate

class JamstackTemplate(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "next": "^13.5.6",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "contentlayer": "^0.3.4",
            "next-contentlayer": "^0.3.4",
            "@tailwindcss/typography": "^0.5.10",
            "tailwindcss": "^3.4.0",
            "postcss": "^8.4.31",
            "autoprefixer": "^10.4.16",
            "date-fns": "^3.1.0",
            "reading-time": "^1.5.0",
            "rehype-autolink-headings": "^7.1.0",
            "rehype-pretty-code": "^0.12.3",
            "rehype-slug": "^6.0.0",
            "remark-gfm": "^3.0.1",
            "rss": "^1.2.2",
            "next-themes": "^0.2.1",
        }

    @property
    def dev_dependencies(self) -> dict:
        return {
            "typescript": "^5.0.0",
            "@types/node": "^20.0.0",
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "eslint": "^8.56.0",
            "eslint-config-next": "14.0.0",
            "prettier": "^3.1.0",
            "prettier-plugin-tailwindcss": "^0.5.9",
            "@tailwindcss/typography": "^0.5.10",
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
    "baseUrl": ".",
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"],
      "contentlayer/generated": ["./.contentlayer/generated"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".contentlayer/generated"],
  "exclude": ["node_modules"]
}''')

        self.create_file('next.config.js', '''const { withContentlayer } = require('next-contentlayer')

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = withContentlayer(nextConfig)''')

        self.create_file('tailwind.config.js', '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}",
    "./content/**/*.{md,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '65ch',
            color: 'inherit',
            a: {
              color: 'inherit',
              textDecoration: 'none',
              fontWeight: '500',
            },
            'h2,h3,h4': {
              'scroll-margin-top': '100px',
            },
            code: { color: 'inherit' },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}''')

        self.create_file('postcss.config.js', '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}''')

        self.create_file('contentlayer.config.ts', '''import { defineDocumentType, makeSource } from 'contentlayer/source-files'
import remarkGfm from 'remark-gfm'
import rehypePrettyCode from 'rehype-pretty-code'
import rehypeSlug from 'rehype-slug'
import rehypeAutolinkHeadings from 'rehype-autolink-headings'

export const Post = defineDocumentType(() => ({
  name: 'Post',
  filePathPattern: 'posts/**/*.mdx',
  contentType: 'mdx',
  fields: {
    title: {
      type: 'string',
      required: true,
    },
    date: {
      type: 'date',
      required: true,
    },
    description: {
      type: 'string',
      required: true,
    },
    published: {
      type: 'boolean',
      default: true,
    },
    tags: {
      type: 'list',
      of: { type: 'string' },
      default: [],
    },
  },
  computedFields: {
    slug: {
      type: 'string',
      resolve: (doc) => doc._raw.flattenedPath.replace(/posts\/?/, ''),
    },
  },
}))

export default makeSource({
  contentDirPath: 'content',
  documentTypes: [Post],
  mdx: {
    remarkPlugins: [remarkGfm],
    rehypePlugins: [
      rehypeSlug,
      [
        rehypePrettyCode,
        {
          theme: 'github-dark',
        },
      ],
      [
        rehypeAutolinkHeadings,
        {
          properties: {
            className: ['anchor'],
          },
        },
      ],
    ],
  },
})''')

        # Create basic app structure
        self.create_file('src/app/layout.tsx', '''import { type Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ThemeProvider } from '@/components/theme-provider'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'JAMstack Blog',
  description: 'Generated by Stackmate',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}''')

        self.create_file('src/app/globals.css', '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 240 10% 3.9%;
    --card: 0 0% 100%;
    --card-foreground: 240 10% 3.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 240 10% 3.9%;
    --primary: 240 5.9% 10%;
    --primary-foreground: 0 0% 98%;
    --secondary: 240 4.8% 95.9%;
    --secondary-foreground: 240 5.9% 10%;
    --muted: 240 4.8% 95.9%;
    --muted-foreground: 240 3.8% 46.1%;
    --accent: 240 4.8% 95.9%;
    --accent-foreground: 240 5.9% 10%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 5.9% 90%;
    --input: 240 5.9% 90%;
    --ring: 240 5.9% 10%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 240 10% 3.9%;
    --foreground: 0 0% 98%;
    --card: 240 10% 3.9%;
    --card-foreground: 0 0% 98%;
    --popover: 240 10% 3.9%;
    --popover-foreground: 0 0% 98%;
    --primary: 0 0% 98%;
    --primary-foreground: 240 5.9% 10%;
    --secondary: 240 3.7% 15.9%;
    --secondary-foreground: 0 0% 98%;
    --muted: 240 3.7% 15.9%;
    --muted-foreground: 240 5% 64.9%;
    --accent: 240 3.7% 15.9%;
    --accent-foreground: 0 0% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 0 0% 98%;
    --border: 240 3.7% 15.9%;
    --input: 240 3.7% 15.9%;
    --ring: 240 4.9% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}''')

        self.create_file('src/app/page.tsx', '''import { allPosts } from 'contentlayer/generated'
import { compareDesc } from 'date-fns'
import Link from 'next/link'

export default function Home() {
  const posts = allPosts.sort((a, b) =>
    compareDesc(new Date(a.date), new Date(b.date))
  )

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-4xl font-bold">Welcome to JAMstack Blog</h1>
      <p className="mt-4 text-xl">A modern blog built with Next.js and MDX</p>
      
      <div className="mt-12">
        <h2 className="text-2xl font-bold">Latest Posts</h2>
        <div className="mt-6 grid gap-6">
          {posts.map((post) => (
            <Link 
              key={post.slug}
              href={`/posts/${post.slug}`}
              className="block group hover:bg-gray-50 dark:hover:bg-gray-900 p-6 rounded-lg transition"
            >
              <article>
                <h3 className="text-xl font-semibold group-hover:text-primary">{post.title}</h3>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                  {post.description}
                </p>
                <div className="mt-4 flex gap-2">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-gray-100 px-3 py-1 text-sm dark:bg-gray-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </article>
            </Link>
          ))}
        </div>
      </div>
    </main>
  )
}''')

        # Create theme provider component
        self.create_file('src/components/theme-provider.tsx', '''"use client"

import { createContext, useContext, useEffect, useState } from 'react'

type Theme = 'dark' | 'light' | 'system'

type ThemeProviderProps = {
  children: React.ReactNode
  defaultTheme?: Theme
  storageKey?: string
  attribute?: string
  enableSystem?: boolean
}

type ThemeProviderState = {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const ThemeProviderContext = createContext<ThemeProviderState | undefined>(
  undefined
)

export function ThemeProvider({
  children,
  defaultTheme = 'system',
  storageKey = 'theme',
  attribute = 'data-theme',
  enableSystem = true,
  ...props
}: ThemeProviderProps) {
  const [theme, setTheme] = useState<Theme>(defaultTheme)

  useEffect(() => {
    const savedTheme = localStorage.getItem(storageKey) as Theme
    if (savedTheme) {
      setTheme(savedTheme)
    }
  }, [storageKey])

  useEffect(() => {
    const root = window.document.documentElement

    root.classList.remove('light', 'dark')

    if (theme === 'system' && enableSystem) {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)')
        .matches
        ? 'dark'
        : 'light'

      root.classList.add(systemTheme)
      return
    }

    root.classList.add(theme)
  }, [theme, enableSystem])

  const value = {
    theme,
    setTheme: (theme: Theme) => {
      localStorage.setItem(storageKey, theme)
      setTheme(theme)
    },
  }

  return (
    <ThemeProviderContext.Provider {...props} value={value}>
      {children}
    </ThemeProviderContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined)
    throw new Error('useTheme must be used within a ThemeProvider')

  return context
}''')

        # Create example blog post
        self.create_file('content/posts/hello-world.mdx', '''---
title: Hello World
date: 2024-01-01
description: Welcome to my JAMstack blog built with Next.js, MDX, and Contentlayer.
published: true
tags: [next.js, mdx, contentlayer]
---

# Hello World

Welcome to my JAMstack blog! This is a starter template that uses:

- [Next.js](https://nextjs.org) for the framework
- [MDX](https://mdxjs.com) for writing content
- [Contentlayer](https://contentlayer.dev) for content management
- [Tailwind CSS](https://tailwindcss.com) for styling
- [next-themes](https://github.com/pacocoursey/next-themes) for dark mode

## Features

- ✨ MDX for content
- 🎨 Syntax highlighting with rehype-pretty-code
- 🌙 Dark mode with next-themes
- 📱 Fully responsive
- 🔍 SEO friendly
- 📊 RSS feed
- 🎯 Zero runtime JavaScript
- ⚡️ Blazing fast page loads

## Code Example

```typescript
function hello(name: string) {
  console.log(`Hello, ${name}!`)
}
```

## Next Steps

1. Edit this post in `content/posts/hello-world.mdx`
2. Add your own posts in the `content/posts` directory
3. Customize the theme in `tailwind.config.js`
4. Update the metadata in `src/app/layout.tsx`
''')

        # Create README.md
        self.create_file('README.md', f'''# {self.project_name}

A modern JAMstack blog built with Next.js, MDX, and Contentlayer.

## Features

- Next.js 13+ with App Router
- MDX for content authoring
- Contentlayer for type-safe content
- Tailwind CSS for styling
- Dark mode support
- Syntax highlighting
- RSS feed
- SEO optimized
- TypeScript support

## Prerequisites

- Node.js 18+
- npm or yarn

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Project Structure

```
{self.project_name}/
├── content/            # Blog posts and content
│   └── posts/         # MDX blog posts
├── src/
│   ├── app/          # Next.js app router
│   ├── components/   # React components
│   └── styles/       # Global styles
└── public/           # Static assets
```

## Writing Content

1. Create new posts in the `content/posts` directory using MDX
2. Add frontmatter with title, date, description, and tags
3. Write your content using Markdown and MDX components
4. Posts will be automatically built and rendered

## Development

- Run development server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm run start`
- Run linter: `npm run lint`

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [MDX Documentation](https://mdxjs.com)
- [Contentlayer Documentation](https://contentlayer.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## License

This project is licensed under the MIT License.
''')

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

# contentlayer
.contentlayer''')

        # Create dynamic route for blog posts
        self.create_file('src/app/posts/[slug]/page.tsx', '''import { allPosts } from 'contentlayer/generated'
import { notFound } from 'next/navigation'
import { Metadata } from 'next'
import { format, parseISO } from 'date-fns'
import { MDXContent } from '@/components/mdx-content'

interface PostProps {
  params: {
    slug: string
  }
}

async function getPost(slug: string) {
  const post = allPosts.find((post) => post.slug === slug)

  if (!post) {
    notFound()
  }

  return post
}

export async function generateMetadata({ params }: PostProps): Promise<Metadata> {
  const post = await getPost(params.slug)

  return {
    title: post.title,
    description: post.description,
  }
}

export async function generateStaticParams() {
  return allPosts.map((post) => ({
    slug: post.slug,
  }))
}

export default async function PostPage({ params }: PostProps) {
  const post = await getPost(params.slug)

  return (
    <article className="mx-auto max-w-4xl px-6 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold">{post.title}</h1>
        <time dateTime={post.date} className="text-gray-600 dark:text-gray-400">
          {format(parseISO(post.date), 'LLLL d, yyyy')}
        </time>
        <div className="mt-4 flex gap-2">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-gray-100 px-3 py-1 text-sm dark:bg-gray-800"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
      <MDXContent code={post.body.code} />
    </article>
  )
}''')

        # Create MDX component
        self.create_file('src/components/mdx-content.tsx', '''"use client"

import { useMDXComponent } from 'next-contentlayer/hooks'

interface MDXContentProps {
  code: string
}

export function MDXContent({ code }: MDXContentProps) {
  const MDXComponent = useMDXComponent(code)

  return (
    <div className="prose dark:prose-invert max-w-none">
      <MDXComponent />
    </div>
  )
}''')

        print(f"\nProject {self.project_name} created successfully!")
        print("\nNext steps:")
        print("1. cd", self.project_name)
        print("2. npm install")
        print("3. npm run dev") 