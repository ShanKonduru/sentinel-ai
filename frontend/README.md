# Sentinel AI Dashboard

React-based frontend dashboard for monitoring AI agent performance and metrics.

## Features

- Real-time metrics visualization
- Historical data analysis
- Agent performance monitoring
- Cost tracking and analysis
- Data export functionality
- Responsive design for desktop and tablet

## Technology Stack

- React 18 with TypeScript
- Vite for build tooling
- D3.js for advanced data visualizations
- Ant Design for UI components
- Socket.IO for real-time updates
- Recharts for charts and graphs

## Development Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build

# Lint and format
npm run lint
npm run format
```

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/         # Page components (Dashboard, AgentDetail)
├── services/      # API client and real-time services
├── utils/         # Utility functions and helpers
└── main.tsx       # Application entry point

tests/
├── components/    # Component tests
├── integration/   # Integration tests
├── unit/         # Unit tests
└── performance/  # Performance tests
```

## Environment Variables

- `VITE_API_URL`: Backend API base URL
- `VITE_WS_URL`: WebSocket server URL