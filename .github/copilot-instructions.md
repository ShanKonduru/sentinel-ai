# Sentinel AI System Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-20

## Active Technologies
- Python 3.11 + Flask + FastAPI (001-sentinel-ai-system)
- React + D3.js (001-sentinel-ai-system)
- PostgreSQL + Docker (001-sentinel-ai-system)

## Project Structure
```
backend/
├── src/
│   ├── models/
│   ├── services/
│   ├── api/
│   └── collectors/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

docker/
└── compose files and Dockerfiles
```

## Commands
```bash
# Backend development
cd backend && python -m pytest && flake8 src/

# Frontend development  
cd frontend && npm test && npm run lint

# Docker services
docker-compose up -d && docker-compose ps
```

## Code Style
- Python: PEP 8 compliance, 90% test coverage required
- JavaScript/TypeScript: ESLint + Prettier, React best practices
- SQL: PostgreSQL conventions, immutable data patterns

## Recent Changes
- 001-sentinel-ai-system: Added Python 3.11 + Flask/FastAPI + React + PostgreSQL microservices architecture

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->