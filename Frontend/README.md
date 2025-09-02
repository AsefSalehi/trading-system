# Trading System Frontend

A modern React TypeScript frontend for the cryptocurrency trading system, built with Vite, TailwindCSS, and shadcn/ui.

## Features

- **Modern Stack**: React 19 + TypeScript + Vite
- **Styling**: TailwindCSS with shadcn/ui components
- **Data Fetching**: TanStack Query (React Query) for efficient API calls
- **Real-time Updates**: Automatic data refresh every 30 seconds
- **Responsive Design**: Mobile-first responsive layout
- **Docker Support**: Development and production Docker configurations

## Quick Start

### Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker Development

```bash
# Start with Docker Compose (includes backend)
docker-compose up frontend-dev

# Or build and run manually
docker build -t trading-frontend --target development .
docker run -p 5173:5173 trading-frontend
```

### Docker Production

```bash
# Start production build
docker-compose --profile production up frontend-prod

# Or build and run manually
docker build -t trading-frontend --target production .
docker run -p 3000:80 trading-frontend
```

## Project Structure

```
src/
├── components/          # React components
│   ├── CryptocurrencyCard.tsx
│   └── CryptocurrencyDashboard.tsx
├── services/           # API services
│   └── api.ts
├── types/              # TypeScript type definitions
│   └── cryptocurrency.ts
├── lib/                # Utility functions
│   └── utils.ts
├── App.tsx             # Main application component
└── main.tsx           # Application entry point
```

## API Integration

The frontend integrates with the backend API endpoints:

- `GET /api/v1/cryptocurrencies/` - List cryptocurrencies with filtering
- `GET /api/v1/cryptocurrencies/{symbol}` - Get specific cryptocurrency
- `GET /api/v1/cryptocurrencies/{symbol}/history` - Get price history
- `GET /api/v1/cryptocurrencies/top/{category}` - Get top cryptocurrencies
- `POST /api/v1/cryptocurrencies/sync` - Sync data from external APIs

## Environment Variables

### Development (.env.development)
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Trading System
VITE_APP_VERSION=1.0.0
```

### Production (.env.production)
```
VITE_API_BASE_URL=/api/v1
VITE_APP_NAME=Trading System
VITE_APP_VERSION=1.0.0
```

## Features Implemented

### ✅ FRONTEND-001 - Application Setup & Configuration

- [x] React with TypeScript in strict mode
- [x] Vite as bundler with fast builds and hot reloading
- [x] TailwindCSS and shadcn/ui for consistent styling
- [x] Docker and Docker Compose integration
- [x] Production-optimized builds with code splitting
- [x] Environment-based configuration

### Dashboard Features

- **Cryptocurrency Listing**: Display top cryptocurrencies with real-time data
- **Search & Filter**: Search by symbol and sort by various metrics
- **Real-time Updates**: Automatic refresh every 30 seconds
- **Responsive Design**: Works on desktop and mobile devices
- **Error Handling**: Graceful error handling with retry mechanisms
- **Loading States**: Proper loading indicators and skeleton states

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Technology Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **TanStack Query** - Data fetching and caching
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **Docker** - Containerization

## Performance Optimizations

- **Code Splitting**: Automatic vendor and feature-based chunks
- **Lazy Loading**: Components loaded on demand
- **Caching**: React Query handles API response caching
- **Compression**: Gzip compression in production
- **Asset Optimization**: Optimized images and static assets

## Security Features

- **Content Security Policy**: Configured in nginx
- **XSS Protection**: Security headers in production
- **CORS Handling**: Proper CORS configuration
- **Environment Variables**: Secure configuration management

## Next Steps

The following tickets are ready for implementation:

- **FRONTEND-002**: Authentication & Secure Access
- **FRONTEND-003**: Dashboard: Market Analysis Visualization
- **FRONTEND-004**: Dashboard: Risk Reporting
- **FRONTEND-005**: Dashboard: Trade Monitoring & Moderation
- **FRONTEND-006**: Real-Time Updates & Notifications
- **FRONTEND-007**: State Management
- **FRONTEND-008**: Logging & Error Handling

## Contributing

1. Follow the existing code style and TypeScript conventions
2. Add proper type definitions for new features
3. Include error handling and loading states
4. Test responsive design on multiple screen sizes
5. Update documentation for new features