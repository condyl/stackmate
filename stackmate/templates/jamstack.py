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
            "remark-gfm": "^4.0.0",
            "rss": "^1.2.2",
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

    def generate(self) -> None:
        """Generate a JAMstack blog project structure."""
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
  "include": [
    "next-env.d.ts",
    "**/*.ts",
    "**/*.tsx",
    ".next/types/**/*.ts",
    ".contentlayer/generated"
  ],
  "exclude": ["node_modules"]
}''')

        # 3. Create Next.js configuration with Contentlayer
        self.create_file('next.config.js', '''const { withContentlayer } = require('next-contentlayer');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
};

module.exports = withContentlayer(nextConfig);''')

        # 4. Configure Contentlayer
        self.create_file('contentlayer.config.ts', '''import { defineDocumentType, makeSource } from 'contentlayer/source-files';
import readingTime from 'reading-time';
import rehypeAutolinkHeadings from 'rehype-autolink-headings';
import rehypePrettyCode from 'rehype-pretty-code';
import rehypeSlug from 'rehype-slug';
import remarkGfm from 'remark-gfm';

export const Post = defineDocumentType(() => ({
  name: 'Post',
  filePathPattern: `posts/**/*.mdx`,
  contentType: 'mdx',
  fields: {
    title: { type: 'string', required: true },
    date: { type: 'date', required: true },
    description: { type: 'string', required: true },
    tags: { type: 'list', of: { type: 'string' }, default: [] },
    image: { type: 'string', required: false },
  },
  computedFields: {
    slug: {
      type: 'string',
      resolve: (doc) => doc._raw.sourceFileName.replace(/\.mdx$/, ''),
    },
    url: {
      type: 'string',
      resolve: (doc) => `/blog/posts/${doc._raw.sourceFileName.replace(/\.mdx$/, '')}`,
    },
    readingTime: {
      type: 'json',
      resolve: (doc) => readingTime(doc.body.raw),
    },
  },
}));

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
});''')

        # 5. Configure Tailwind
        self.create_file('tailwind.config.ts', '''import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
          },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};

export default config;''')

        self.create_file('postcss.config.js', '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}''')

        # 6. Create example blog post
        self.create_file('content/posts/hello-world.mdx', '''---
title: Hello World
date: 2024-01-01
description: Welcome to my JAMstack blog built with Next.js, MDX, and Contentlayer.
tags: [nextjs, mdx, contentlayer]
---

# Hello World

Welcome to my blog! This is a starter template for building a modern JAMstack blog using:

- [Next.js](https://nextjs.org) - React framework
- [MDX](https://mdxjs.com) - Markdown + JSX
- [Contentlayer](https://contentlayer.dev) - Content SDK
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS

## Code Example

```typescript
function greet(name: string) {
  return `Hello, ${name}!`;
}
```

## Features

- ✨ MDX for content
- 📚 Contentlayer for type-safe content
- 🎨 Tailwind CSS for styling
- 🔍 SEO optimized
- 📱 Responsive design
- 🚀 Fast build times''')

        # 7. Create components
        self.create_file('src/components/PostCard.tsx', '''import Link from 'next/link';
import { format } from 'date-fns';
import type { Post } from 'contentlayer/generated';

export function PostCard(post: Post) {
  return (
    <div className="mb-8">
      <h2 className="mb-1 text-xl">
        <Link
          href={post.url}
          className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
        >
          {post.title}
        </Link>
      </h2>
      <time dateTime={post.date} className="mb-2 block text-xs text-gray-600 dark:text-gray-400">
        {format(new Date(post.date), 'MMMM dd, yyyy')}
      </time>
      <div className="text-sm text-gray-700 dark:text-gray-300">{post.description}</div>
    </div>
  );
}''')

        self.create_file('src/components/MDXComponents.tsx', '''import Image from 'next/image';
import Link from 'next/link';

export const MDXComponents = {
  Image: (props: any) => <Image {...props} />,
  a: ({ href = '', ...props }) => {
    if (href.startsWith('http')) {
      return <a href={href} target="_blank" rel="noopener noreferrer" {...props} />;
    }
    return <Link href={href} {...props} />;
  },
};''')

        # 8. Create app structure
        self.create_file('src/app/layout.tsx', '''import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'My Blog',
  description: 'A modern JAMstack blog built with Next.js and MDX',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100`}>
        <div className="mx-auto max-w-3xl px-4 py-8">
          {children}
        </div>
      </body>
    </html>
  );
}''')

        self.create_file('src/app/globals.css', '''@tailwind base;
@tailwind components;
@tailwind utilities;

.prose {
  @apply text-gray-900 dark:text-gray-100;
}

.prose pre {
  @apply bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg overflow-x-auto;
}

.prose code {
  @apply bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100 px-1 py-0.5 rounded-md;
}

.prose a {
  @apply text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300;
}

.prose h1 {
  @apply text-gray-900 dark:text-gray-100;
}

.prose h2 {
  @apply text-gray-900 dark:text-gray-100 mt-8 mb-4;
}

.prose h3 {
  @apply text-gray-900 dark:text-gray-100 mt-6 mb-3;
}

.prose strong {
  @apply text-gray-900 dark:text-gray-100;
}

.prose ol > li::marker {
  @apply text-gray-600 dark:text-gray-400;
}

.prose ul > li::marker {
  @apply text-gray-600 dark:text-gray-400;
}''')

        self.create_file('src/app/page.tsx', '''import { allPosts } from 'contentlayer/generated';
import { PostCard } from '@/components/PostCard';

export default function Home() {
  const posts = allPosts.sort((a, b) => {
    return new Date(b.date).getTime() - new Date(a.date).getTime();
  });

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold">Blog Posts</h1>
      {posts.map((post, idx) => (
        <PostCard key={idx} {...post} />
      ))}
    </div>
  );
}''')

        self.create_file('src/app/blog/posts/[slug]/page.tsx', '''import { format } from 'date-fns';
import { allPosts } from 'contentlayer/generated';
import { getMDXComponent } from 'next-contentlayer/hooks';
import { MDXComponents } from '@/components/MDXComponents';
import type { Metadata } from 'next';

export async function generateStaticParams() {
  return allPosts.map((post) => ({
    slug: post.slug,
  }));
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  const post = allPosts.find((post) => post.slug === params.slug);

  return {
    title: post?.title,
    description: post?.description,
  };
}

export default function PostPage({ params }: { params: { slug: string } }) {
  const post = allPosts.find((post) => post.slug === params.slug);

  if (!post) {
    return <div>Post not found</div>;
  }

  const Content = getMDXComponent(post.body.code);

  return (
    <article className="prose prose-lg mx-auto">
      <h1>{post.title}</h1>
      <div className="mb-8 text-sm text-gray-600 dark:text-gray-400">
        <time dateTime={post.date}>
          {format(new Date(post.date), 'MMMM dd, yyyy')}
        </time>
        <span className="mx-2">•</span>
        <span>{post.readingTime.text}</span>
      </div>
      <Content components={MDXComponents} />
    </article>
  );
}''')

        # 9. Create RSS feed generation
        self.create_file('src/app/feed.xml/route.ts', '''import { allPosts } from 'contentlayer/generated';
import RSS from 'rss';

export async function GET() {
  const feed = new RSS({
    title: 'My Blog',
    description: 'A modern JAMstack blog built with Next.js and MDX',
    site_url: 'https://yourdomain.com',
    feed_url: 'https://yourdomain.com/feed.xml',
  });

  allPosts.map((post) => {
    feed.item({
      title: post.title,
      description: post.description,
      url: `https://yourdomain.com${post.url}`,
      date: post.date,
    });
  });

  return new Response(feed.xml({ indent: true }), {
    headers: {
      'Content-Type': 'application/xml',
    },
  });
}''')

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

# typescript
*.tsbuildinfo
next-env.d.ts

# contentlayer
.contentlayer''')

        print(f"\nProject {self.project_name} created successfully!")
        print("\nNext steps:")
        print("1. cd", self.project_name)
        print("2. npm install")
        print("3. npm run dev")
        print("\nStart writing your blog posts in the content/posts directory using MDX!") 