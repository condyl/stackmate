"""
Enterprise React stack template using Next.js, Redux Toolkit, Material UI, and more.
"""

import os
from .base import BaseTemplate

class EnterpriseReactTemplate(BaseTemplate):
    @property
    def dependencies(self) -> dict:
        return {
            "next": "^14.0.0",
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "@mui/material": "^5.15.3",
            "@mui/icons-material": "^5.15.3",
            "@emotion/react": "^11.11.3",
            "@emotion/styled": "^11.11.0",
            "@reduxjs/toolkit": "^2.0.1",
            "react-redux": "^9.0.4",
            "@tanstack/react-query": "^5.17.0",
            "axios": "^1.6.5",
            "formik": "^2.4.5",
            "yup": "^1.3.3",
        }

    @property
    def dev_dependencies(self) -> dict:
        return {
            "typescript": "^5.0.0",
            "@types/node": "^20.0.0",
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "@storybook/react": "^7.6.7",
            "@storybook/builder-webpack5": "^7.6.7",
            "cypress": "^13.6.2",
            "jest": "^29.7.0",
            "@testing-library/react": "^14.1.2",
            "@testing-library/jest-dom": "^6.2.0",
            "eslint": "^8.56.0",
            "eslint-config-next": "14.0.0",
            "prettier": "^3.1.0",
        }

    def generate(self) -> None:
        """Generate an Enterprise React project structure."""
        self.create_project_directory()
        
        # 1. Create package.json with additional scripts
        self.create_package_json({
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint",
                "test": "jest",
                "test:watch": "jest --watch",
                "test:e2e": "cypress run",
                "cypress": "cypress open",
                "storybook": "storybook dev -p 6006",
                "build-storybook": "storybook build"
            }
        })

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

        # 4. Set up Redux store
        self.create_file('src/store/index.ts', '''import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    ui: uiReducer,
  },
  devTools: process.env.NODE_ENV !== 'production',
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;''')

        # 5. Create Redux slices
        self.create_file('src/store/slices/authSlice.ts', '''import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  isAuthenticated: boolean;
  user: {
    id?: string;
    name?: string;
    email?: string;
  } | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
};

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<AuthState['user']>) => {
      state.isAuthenticated = !!action.payload;
      state.user = action.payload;
    },
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
    },
  },
});

export const { setUser, logout } = authSlice.actions;
export default authSlice.reducer;''')

        self.create_file('src/store/slices/uiSlice.ts', '''import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  isDarkMode: boolean;
  sidebarOpen: boolean;
}

const initialState: UIState = {
  isDarkMode: false,
  sidebarOpen: true,
};

export const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    toggleDarkMode: (state) => {
      state.isDarkMode = !state.isDarkMode;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
  },
});

export const { toggleDarkMode, toggleSidebar } = uiSlice.actions;
export default uiSlice.reducer;''')

        # 6. Create Material UI theme
        self.create_file('src/theme/index.ts', '''"use client";

import { createTheme } from '@mui/material/styles';

export const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

export const darkTheme = createTheme({
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

        # 7. Create API client
        self.create_file('src/api/client.ts', '''import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});''')

        # 8. Create example components
        self.create_file('src/components/Layout/index.ts', '''export { default as AppBar } from './AppBar';
export { default as Sidebar } from './Sidebar';''')

        self.create_file('src/components/Layout/AppBar.tsx', '''import { AppBar as MuiAppBar, Toolbar, Typography, IconButton } from '@mui/material';
import { Menu as MenuIcon, Brightness4, Brightness7 } from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { toggleSidebar, toggleDarkMode } from '@/store/slices/uiSlice';
import type { RootState } from '@/store';

export default function AppBar() {
  const dispatch = useDispatch();
  const isDarkMode = useSelector((state: RootState) => state.ui.isDarkMode);

  return (
    <MuiAppBar position="fixed">
      <Toolbar>
        <IconButton
          color="inherit"
          edge="start"
          onClick={() => dispatch(toggleSidebar())}
        >
          <MenuIcon />
        </IconButton>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Enterprise App
        </Typography>
        <IconButton
          color="inherit"
          onClick={() => dispatch(toggleDarkMode())}
        >
          {isDarkMode ? <Brightness7 /> : <Brightness4 />}
        </IconButton>
      </Toolbar>
    </MuiAppBar>
  );
}''')

        self.create_file('src/components/Layout/Sidebar.tsx', '''import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Home as HomeIcon,
  Person as PersonIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useSelector } from 'react-redux';
import type { RootState } from '@/store';

const drawerWidth = 240;

export default function Sidebar() {
  const isOpen = useSelector((state: RootState) => state.ui.sidebarOpen);

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={isOpen}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <List>
        <ListItem button>
          <ListItemIcon>
            <HomeIcon />
          </ListItemIcon>
          <ListItemText primary="Home" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <PersonIcon />
          </ListItemIcon>
          <ListItemText primary="Profile" />
        </ListItem>
        <Divider />
        <ListItem button>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItem>
      </List>
    </Drawer>
  );
}''')

        # 9. Create app layout
        self.create_file('src/app/layout.tsx', '''import { type Metadata } from 'next';
import { Providers } from '@/providers';

export const metadata: Metadata = {
  title: 'Enterprise React App',
  description: 'Generated by Stackmate',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}''')

        # Create ClientLayout component
        self.create_file('src/components/Layout/ClientLayout.tsx', '''"use client";

import AppBar from './AppBar';
import Sidebar from './Sidebar';
import { Box } from '@mui/material';

export function ClientLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <AppBar />
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          ml: { sm: 30 },
        }}
      >
        {children}
      </Box>
    </>
  );
}''')

        # Create ThemeWrapper component
        self.create_file('src/components/Theme/ThemeWrapper.tsx', '''"use client";

import { useSelector } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { lightTheme, darkTheme } from '@/theme';
import type { RootState } from '@/store';

export function ThemeWrapper({ children }: { children: React.ReactNode }) {
  const isDarkMode = useSelector((state: RootState) => state.ui.isDarkMode);

  return (
    <ThemeProvider theme={isDarkMode ? darkTheme : lightTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}''')

        # Update providers to use ThemeWrapper
        self.create_file('src/providers/index.tsx', '''"use client";

import { Provider } from 'react-redux';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { store } from '@/store';
import { ThemeWrapper } from '@/components/Theme/ThemeWrapper';
import { ClientLayout } from '@/components/Layout/ClientLayout';

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeWrapper>
          <ClientLayout>{children}</ClientLayout>
        </ThemeWrapper>
      </QueryClientProvider>
    </Provider>
  );
}''')

        # 10. Create example page
        self.create_file('src/app/page.tsx', '''"use client";

import { Box, Typography, Button } from '@mui/material';
import { useDispatch } from 'react-redux';
import { toggleDarkMode } from '@/store/slices/uiSlice';

export default function Home() {
  const dispatch = useDispatch();

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 'calc(100vh - 64px)',
        padding: 3,
      }}
    >
      <Typography variant="h2" component="h1" gutterBottom>
        Welcome to Enterprise React
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={() => dispatch(toggleDarkMode())}
      >
        Toggle Theme
      </Button>
    </Box>
  );
}''')

        # 11. Create Storybook configuration
        self.create_file('.storybook/main.ts', '''import type { StorybookConfig } from "@storybook/nextjs";

const config: StorybookConfig = {
  stories: ["../src/**/*.mdx", "../src/**/*.stories.@(js|jsx|mjs|ts|tsx)"],
  addons: [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "@storybook/addon-onboarding",
    "@storybook/addon-interactions",
  ],
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
  docs: {
    autodocs: "tag",
  },
};
export default config;''')

        # 12. Create Jest configuration
        self.create_file('jest.config.js', '''const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
}

module.exports = createJestConfig(customJestConfig)''')

        self.create_file('jest.setup.js', '''import '@testing-library/jest-dom';''')

        # 13. Create Cypress configuration
        self.create_file('cypress.config.ts', '''import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: false,
  },
})''')

        # 14. Create example test
        self.create_file('src/components/Layout/AppBar.test.tsx', '''import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '@/store';
import AppBar from './AppBar';

describe('AppBar', () => {
  it('renders the app title', () => {
    render(
      <Provider store={store}>
        <AppBar />
      </Provider>
    );
    expect(screen.getByText('Enterprise App')).toBeInTheDocument();
  });
});''')

        # 15. Create example Storybook story
        self.create_file('src/components/Layout/AppBar.stories.tsx', '''import type { Meta, StoryObj } from '@storybook/react';
import { Provider } from 'react-redux';
import { store } from '@/store';
import AppBar from './AppBar';

const meta: Meta<typeof AppBar> = {
  title: 'Layout/AppBar',
  component: AppBar,
  decorators: [
    (Story) => (
      <Provider store={store}>
        <Story />
      </Provider>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof AppBar>;

export const Default: Story = {};''')

        print(f"\nProject {self.project_name} created successfully!")
        print("\nNext steps:")
        print("1. cd", self.project_name)
        print("2. npm install")
        print("3. npm run dev")
        print("\nAdditional commands:")
        print("- npm run storybook    # Start Storybook")
        print("- npm test            # Run tests")
        print("- npm run cypress     # Run E2E tests") 