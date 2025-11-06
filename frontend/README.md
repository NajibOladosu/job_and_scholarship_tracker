# Trackly Frontend

Modern React/TypeScript frontend for Trackly with dark neon-green theme inspired by Leadverse.ai.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom dark theme
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Routing**: React Router DOM

## Theme Colors

- **Background**: `#0A0A0A`
- **Surface**: `#101010`
- **Border**: `#1A1A1A`
- **Accent**: `#00FF88` (Neon Green)
- **Text Primary**: `#EDEDED`
- **Text Secondary**: `#B5B5B5`

## Development

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── layout/          # Layout components (Navbar, Sidebar, Footer)
│   └── ui/              # Reusable UI components (Button, Card, Input)
├── pages/               # Page components
│   ├── Home.tsx         # Landing page
│   ├── Dashboard.tsx    # Dashboard with stats
│   ├── Applications.tsx # Applications management
│   ├── Documents.tsx    # Document upload/management
│   ├── Notifications.tsx# Notifications feed
│   ├── Profile.tsx      # User profile
│   └── Login.tsx        # Authentication
├── lib/
│   └── utils.ts         # Utility functions (cn helper)
├── App.tsx              # Main app with routing
├── main.tsx             # App entry point
└── index.css            # Global styles with Tailwind

## Features

- ✅ Dark theme with neon green accents
- ✅ Glassmorphism effects
- ✅ Smooth animations with Framer Motion
- ✅ Responsive design
- ✅ Clean, minimal aesthetic
- ✅ Reusable component library

## Django Integration

The Vite dev server proxies API requests to Django backend at `http://localhost:8000`.

For production, build the frontend and configure Django to serve static files:

```bash
npm run build
# Output will be in dist/ directory
```
