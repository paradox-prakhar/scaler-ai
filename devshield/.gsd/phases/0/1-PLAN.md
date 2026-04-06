---
phase: 0
plan: 1
wave: 1
---

# Plan 0.1: Frontend Scaffold

## Objective
Bootstrap the React + Vite frontend with Tailwind CSS, Monaco Editor,
Framer Motion, and Axios. The app should render a working shell at
http://localhost:5173 with routing and a dark theme.

## Context
- .gsd/SPEC.md

## Tasks

<task type="auto">
  <name>Scaffold Vite + React app</name>
  <files>
    devshield/client/
  </files>
  <action>
    Run in the devshield/ directory:
      npm create vite@latest client -- --template react
      cd client && npm install

    Then install additional packages:
      npm install -D tailwindcss@3 postcss autoprefixer
      npx tailwindcss init -p
      npm install @monaco-editor/react framer-motion axios react-router-dom

    Configure tailwind.config.js:
      content: ["./index.html", "./src/**/*.{js,jsx}"]
      darkMode: 'class'
      theme.extend: add custom colors:
        primary: '#6c63ff'
        dark: { bg: '#0f0f17', card: '#1a1a2e', border: '#2a2a3d' }

    In src/index.css add:
      @tailwind base;
      @tailwind components;
      @tailwind utilities;
      Body: background #0f0f17, color #e0e0f0, font Inter (Google Fonts)

    Create src/main.jsx — wrap App in BrowserRouter.

    Create src/App.jsx with routes:
      /           → HomePage (placeholder "DevShield")
      /code       → CodeBenchmarkPage (placeholder)
      /security   → SecurityTrainerPage (placeholder)
      /dashboard  → DashboardPage (placeholder)
      /login      → LoginPage (placeholder)

    Create src/components/Navbar.jsx:
      Dark sticky navbar
      Logo: "🛡 DevShield"
      Links: Code Benchmark | Security Trainer | Dashboard
      Right: Login button (route to /login)
      Use Framer Motion for hover animation on links

    Create src/pages/ with placeholder components for each route above.
    Each placeholder: centered text showing the page name.
  </action>
  <verify>
    cd devshield/client && npm run dev
    Open http://localhost:5173 — navbar visible, routing works between pages.
  </verify>
  <done>
    - npm run dev starts without errors
    - Navbar renders with dark theme
    - All 5 routes reachable without 404
    - Monaco package installed (import works)
  </done>
</task>
