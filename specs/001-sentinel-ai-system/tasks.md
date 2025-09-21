# Tasks: Sentinel AI System

**Input**: Design documents from `C:\MyProjects\sentinel_ai\specs\001-sentinel-ai-system\`
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓

## Phase 3.1: Setup
- [x] T001 Create project structure with backend/, frontend/, docker/, docs/ directories
- [x] T002 Initialize Python backend projects with Flask/FastAPI dependencies in backend/
- [x] T003 Initialize React frontend project with TypeScript and D3.js in frontend/
- [x] T004 [P] Configure Python linting (flake8, black, isort) in backend/
- [x] T005 [P] Configure frontend linting (ESLint, Prettier) in frontend/
- [x] T006 [P] Create Docker configuration files in docker/
- [x] T007 [P] Create environment configuration templates (.env.example)
- [x] T008 Setup PostgreSQL database schema and migrations in backend/src/database/

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests (API Endpoints)
- [x] T009 [P] Contract test POST /api/v1/metrics in backend/tests/contract/test_metrics_post.py
- [x] T010 [P] Contract test GET /api/v1/health (metrics API) in backend/tests/contract/test_health_check.py
- [x] T011 [P] Contract test GET /api/v1/agents in backend/tests/contract/test_agents_get.py
- [x] T012 [P] Contract test POST /api/v1/export in backend/tests/contract/test_export_post.py
- [x] T013 [P] Contract test GET /api/v1/metrics (data API) in backend/tests/contract/test_metrics_get.py
- [x] T014 [P] Contract test GET /api/v1/export in backend/tests/contract/test_export_get.py
- [x] T015 [P] Contract test GET /api/v1/health (data API) in backend/tests/contract/test_data_api_health.py

### Integration Tests (User Scenarios)
- [x] T016 [P] Integration test engineer performance diagnosis in backend/tests/integration/test_performance_diagnosis.py
- [x] T017 [P] Integration test team lead cost management in backend/tests/integration/test_cost_management.py
- [x] T018 [P] Integration test data analyst export workflow in backend/tests/integration/test_data_export.py
- [x] T019 [P] Integration test dashboard real-time updates in frontend/tests/integration/test_dashboard_realtime.test.tsx
- [x] T020 [P] Integration test dashboard filtering functionality in frontend/tests/integration/test_dashboard_filtering.test.tsx

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Database Models
- [ ] T021 [P] AI Agent model in backend/src/models/agent.py
- [ ] T022 [P] Performance Metrics model in backend/src/models/metrics.py
- [ ] T023 [P] User Session model in backend/src/models/session.py
- [ ] T024 [P] Monitoring Configuration model in backend/src/models/configuration.py
- [ ] T025 Database connection and session management in backend/src/database/connection.py

### Backend Services
- [ ] T026 [P] Agent service CRUD operations in backend/src/services/agent_service.py
- [ ] T027 [P] Metrics service data collection in backend/src/services/metrics_service.py
- [ ] T028 [P] Export service CSV/JSON generation in backend/src/services/export_service.py
- [ ] T029 [P] Validation service for metrics data in backend/src/services/validation_service.py

### Metrics Collection API (Flask)
- [ ] T030 POST /api/v1/metrics endpoint in backend/src/api/metrics_collection/routes.py
- [ ] T031 GET /api/v1/health endpoint in backend/src/api/metrics_collection/health.py
- [ ] T032 Flask application configuration in backend/src/api/metrics_collection/app.py
- [ ] T033 Request validation middleware in backend/src/api/metrics_collection/middleware.py

### Data Retrieval API (FastAPI)  
- [ ] T034 GET /api/v1/agents endpoint in backend/src/api/data_retrieval/agents.py
- [ ] T035 GET /api/v1/agents/{id} endpoint in backend/src/api/data_retrieval/agents.py
- [ ] T036 GET /api/v1/metrics endpoint in backend/src/api/data_retrieval/metrics.py
- [ ] T037 GET /api/v1/export endpoint in backend/src/api/data_retrieval/export.py
- [ ] T038 GET /api/v1/health endpoint in backend/src/api/data_retrieval/health.py
- [ ] T039 FastAPI application configuration in backend/src/api/data_retrieval/app.py

### Metrics Collector Component
- [ ] T040 [P] Lightweight metrics collector client in backend/src/collectors/agent_collector.py
- [ ] T041 [P] Collector configuration management in backend/src/collectors/config.py

### Frontend Dashboard Components
- [ ] T042 [P] Agent list component in frontend/src/components/AgentList.tsx
- [ ] T043 [P] Metrics visualization component in frontend/src/components/MetricsChart.tsx
- [ ] T044 [P] Dashboard filter component in frontend/src/components/FilterPanel.tsx
- [ ] T045 [P] Real-time data service in frontend/src/services/realtimeService.ts
- [ ] T046 [P] API client service in frontend/src/services/apiClient.ts
- [ ] T047 Main dashboard page in frontend/src/pages/Dashboard.tsx
- [ ] T048 Agent detail page in frontend/src/pages/AgentDetail.tsx

## Phase 3.4: Integration
- [ ] T049 Connect metrics collection API to PostgreSQL database
- [ ] T050 Connect data retrieval API to PostgreSQL database
- [ ] T051 Implement async data processing pipeline for metrics
- [ ] T052 Add CORS configuration for frontend-backend communication
- [ ] T053 Implement WebSocket connection for real-time dashboard updates
- [ ] T054 Configure logging and monitoring for all services
- [ ] T055 Database connection pooling optimization
- [ ] T056 Error handling and retry logic across services

## Phase 3.5: Polish
- [ ] T057 [P] Unit tests for agent model validation in backend/tests/unit/test_agent_model.py
- [ ] T058 [P] Unit tests for metrics model validation in backend/tests/unit/test_metrics_model.py
- [ ] T059 [P] Unit tests for validation service in backend/tests/unit/test_validation_service.py
- [ ] T060 [P] Unit tests for export service in backend/tests/unit/test_export_service.py
- [ ] T061 [P] Frontend component unit tests in frontend/tests/unit/
- [ ] T062 Performance tests for metrics collection API (>1000 req/s) in backend/tests/performance/test_metrics_api_load.py
- [ ] T063 Performance tests for dashboard load time (<3s) in frontend/tests/performance/test_dashboard_load.py
- [ ] T064 [P] API documentation generation in docs/api/
- [ ] T065 [P] Deployment documentation in docs/deployment/
- [ ] T066 [P] Architecture documentation in docs/architecture/
- [ ] T067 Code coverage validation (>90%) across all services
- [ ] T068 Security audit and OWASP compliance check
- [ ] T069 Production Docker configuration optimization

## Dependencies
**Critical Path**:
- Setup (T001-T008) before all other phases
- Tests (T009-T020) before implementation (T021-T048)
- Models (T021-T025) before services (T026-T029)
- Services before API endpoints (T030-T039)
- Backend APIs before frontend integration (T042-T048)
- Core implementation before integration (T049-T056)
- Integration before polish (T057-T069)

**Sequential Dependencies**:
- T025 (DB connection) blocks T049, T050
- T026-T029 (Services) block T030-T039 (API endpoints)
- T045-T046 (Frontend services) block T047-T048 (Frontend pages)
- T053 (WebSocket) blocks T019 (Real-time dashboard test)

## Parallel Execution Examples

### Setup Phase Parallel Tasks:
```bash
# Run T004, T005, T006, T007 together:
Task: "Configure Python linting (flake8, black, isort) in backend/"
Task: "Configure frontend linting (ESLint, Prettier) in frontend/"
Task: "Create Docker configuration files in docker/"
Task: "Create environment configuration templates (.env.example)"
```

### Contract Tests Parallel Tasks:
```bash
# Run T009-T015 together:
Task: "Contract test POST /api/v1/metrics in backend/tests/contract/test_metrics_post.py"
Task: "Contract test GET /api/v1/health (metrics API) in backend/tests/contract/test_metrics_health.py"
Task: "Contract test GET /api/v1/agents in backend/tests/contract/test_agents_get.py"
Task: "Contract test GET /api/v1/agents/{id} in backend/tests/contract/test_agents_get_by_id.py"
Task: "Contract test GET /api/v1/metrics (data API) in backend/tests/contract/test_data_metrics_get.py"
Task: "Contract test GET /api/v1/export in backend/tests/contract/test_export_get.py"
Task: "Contract test GET /api/v1/health (data API) in backend/tests/contract/test_data_health.py"
```

### Models Parallel Tasks:
```bash
# Run T021-T024 together:
Task: "AI Agent model in backend/src/models/agent.py"
Task: "Performance Metrics model in backend/src/models/metrics.py"
Task: "User Session model in backend/src/models/session.py"
Task: "Monitoring Configuration model in backend/src/models/configuration.py"
```

### Services Parallel Tasks:
```bash
# Run T026-T029 together:
Task: "Agent service CRUD operations in backend/src/services/agent_service.py"
Task: "Metrics service data collection in backend/src/services/metrics_service.py"
Task: "Export service CSV/JSON generation in backend/src/services/export_service.py"
Task: "Validation service for metrics data in backend/src/services/validation_service.py"
```

## Notes
- [P] tasks = different files, no dependencies between them
- Verify all contract tests fail before implementing endpoints
- Commit after completing each task
- Maintain 90% test coverage throughout development
- Follow PEP 8 for Python code, ESLint rules for TypeScript
- Database operations must maintain immutability principle
- Performance targets: Metrics API >1000 req/s, Dashboard <3s load time

## Task Generation Validation
✅ All contract endpoints have corresponding tests (T009-T015)  
✅ All entities have model creation tasks (T021-T024)  
✅ All user scenarios have integration tests (T016-T020)  
✅ Tests are scheduled before implementation (TDD compliance)  
✅ Parallel tasks target different files  
✅ Dependencies respect architectural layers (models → services → APIs → frontend)  
✅ Performance and constitutional requirements addressed (T062-T069)