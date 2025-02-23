"""
Components feature handler for Stackmate.
"""

import os
import json
from typing import Dict, List, Tuple
from rich.console import Console
from rich.panel import Panel
from ..utils.dependency_manager import DependencyManager

# Initialize rich console for consistent styling
console = Console()

async def is_components_installed(project_dir: str, ui_framework: str) -> Tuple[bool, str]:
    """Check if UI components are already installed."""
    try:
        with open(os.path.join(project_dir, 'package.json'), 'r') as f:
            package_json = json.load(f)
            deps = package_json.get('dependencies', {})
            
            if ui_framework == "mui" and "@mui/material" in deps:
                return True, "Material UI is already installed"
            elif ui_framework == "shadcn":
                if all(dep in deps for dep in ["tailwindcss", "class-variance-authority", "clsx"]):
                    return True, "Shadcn UI dependencies are already installed"
    except FileNotFoundError:
        return False, "No package.json found"
    
    # Check for configuration files
    config_files = {
        "shadcn": ["components.json", "src/lib/utils.ts"],
        "mui": ["src/theme/index.ts"]  # Common MUI theme configuration file
    }
    
    for file in config_files.get(ui_framework, []):
        if os.path.exists(os.path.join(project_dir, file)):
            return True, f"UI component configuration found in {file}"
    
    return False, ""

async def add_components(project_dir: str) -> None:
    """Add UI components to an existing project."""
    # Read package.json to determine project type and dependencies
    try:
        with open(os.path.join(project_dir, 'package.json'), 'r') as f:
            package_json = json.load(f)
    except FileNotFoundError:
        console.print("\n[red]Error:[/] No package.json found. Make sure you're in a Node.js project directory.")
        return
    except json.JSONDecodeError:
        console.print("\n[red]Error:[/] Invalid package.json file. Please check the file format.")
        return

    deps = package_json.get('dependencies', {})
    
    # Determine UI framework based on existing dependencies
    ui_framework = determine_ui_framework(deps)
    
    # Check if components are already installed
    is_installed, message = await is_components_installed(project_dir, ui_framework)
    if is_installed:
        console.print(f"\n[yellow]UI Components are already installed:[/] {message}")
        console.print("\n[blue]No changes were made to your project.[/]")
        return
    
    try:
        with console.status("[bold green]Adding UI components...[/]"):
            # Initialize dependency manager
            dep_manager = DependencyManager()
            
            # Add required dependencies based on UI framework
            new_deps = await get_component_dependencies(ui_framework, dep_manager)
            
            # Update package.json
            package_json['dependencies'].update(new_deps)
            with open(os.path.join(project_dir, 'package.json'), 'w') as f:
                json.dump(package_json, f, indent=2)
            
            # Create component files and configurations
            await create_component_files(project_dir, ui_framework)
        
        console.print(f"\n[bold green]✨ UI Components ({ui_framework}) have been added to your project![/]")
        console.print("\n[bold]Next steps:[/]")
        console.print("1. [cyan]npm install[/]")
        
        if ui_framework == "shadcn":
            console.print("2. [cyan]Add components using: npx shadcn-ui@latest add <component-name>[/]")
        elif ui_framework == "mui":
            console.print("2. [cyan]Import components from @mui/material[/]")
        
        console.print("3. [cyan]Check the documentation for usage examples[/]")
        
    except Exception as e:
        console.print(f"\n[red]Error:[/] Failed to add UI components: {str(e)}")
        console.print("\n[yellow]Your project may be in an inconsistent state. Please check the changes made.[/]")
        return

def determine_ui_framework(deps: Dict[str, str]) -> str:
    """Determine the best UI framework based on existing dependencies."""
    if "@mui/material" in deps:
        return "mui"
    elif "tailwindcss" in deps:
        return "shadcn"  # Shadcn uses Tailwind
    else:
        return "shadcn"  # Default choice

async def get_component_dependencies(framework: str, dep_manager: DependencyManager) -> Dict[str, str]:
    """Get required dependencies for the chosen UI framework."""
    deps = {}
    
    if framework == "shadcn":
        base_deps = {
            "tailwindcss": "^3.4.0",
            "postcss": "^8.4.31",
            "autoprefixer": "^10.4.16",
            "@radix-ui/react-icons": "^1.3.0",
            "class-variance-authority": "^0.7.0",
            "clsx": "^2.0.0",
            "tailwind-merge": "^2.0.0",
        }
        deps_analysis = await dep_manager.analyze_dependencies(base_deps)
        deps = deps_analysis["updated_dependencies"]
        
    elif framework == "mui":
        base_deps = {
            "@mui/material": "^5.15.3",
            "@mui/icons-material": "^5.15.3",
            "@emotion/react": "^11.11.3",
            "@emotion/styled": "^11.11.0",
        }
        deps_analysis = await dep_manager.analyze_dependencies(base_deps)
        deps = deps_analysis["updated_dependencies"]
    
    return deps

async def create_component_files(project_dir: str, framework: str) -> None:
    """Create component files and configurations."""
    if framework == "shadcn":
        # Create components.json configuration
        with open(os.path.join(project_dir, 'components.json'), 'w') as f:
            f.write('''{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}''')

        # Create utils file
        os.makedirs(os.path.join(project_dir, 'src/lib'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/lib/utils.ts'), 'w') as f:
            f.write('''import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}''')

        # Update tailwind.config.js
        with open(os.path.join(project_dir, 'tailwind.config.js'), 'w') as f:
            f.write('''/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}''')

        # Update globals.css
        os.makedirs(os.path.join(project_dir, 'src/app'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/app/globals.css'), 'w') as f:
            f.write('''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 224.3 76.3% 48%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}''')

    elif framework == "mui":
        # Create theme configuration
        os.makedirs(os.path.join(project_dir, 'src/theme'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/theme/index.ts'), 'w') as f:
            f.write('''import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
      '"Apple Color Emoji"',
      '"Segoe UI Emoji"',
      '"Segoe UI Symbol"',
    ].join(','),
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});

export const darkTheme = createTheme({
  ...theme,
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});''')

        # Create theme provider wrapper
        os.makedirs(os.path.join(project_dir, 'src/components'), exist_ok=True)
        with open(os.path.join(project_dir, 'src/components/ThemeRegistry.tsx'), 'w') as f:
            f.write('''"use client";

import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { theme } from '@/theme';

export function ThemeRegistry({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}''')

        # Update layout to use ThemeRegistry
        layout_path = os.path.join(project_dir, 'src/app/layout.tsx')
        if os.path.exists(layout_path):
            with open(layout_path, 'r') as f:
                content = f.read()
            
            if 'ThemeRegistry' not in content:
                new_content = content.replace(
                    'export default function RootLayout',
                    '''import { ThemeRegistry } from '@/components/ThemeRegistry';\n\nexport default function RootLayout'''
                ).replace(
                    '{children}',
                    '<ThemeRegistry>{children}</ThemeRegistry>'
                )
                with open(layout_path, 'w') as f:
                    f.write(new_content) 