# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based document summarization microservice that uses LangChain and Anthropic's Claude model. The project implements a clean architecture with async processing for iterative document summarization, accepting markdown input and returning markdown-formatted summaries.

## Architecture

The application follows clean architecture principles with clear separation of concerns:

```
src/
├── domain/          # Core business logic and interfaces
├── use_cases/       # Application business rules
├── infrastructure/  # External concerns (LLM, storage)
└── web/            # HTTP API interface
```

### Core Components

- **Domain Layer** (`src/domain/`): Contains business models and abstract interfaces
- **Use Cases** (`src/use_cases/`): Implements business logic for summary creation
- **Infrastructure** (`src/infrastructure/`): LangChain LLM service and repository implementations
- **Web Layer** (`src/web/`): FastAPI REST API with async background processing

## Development Commands

### Installation
```bash
# Install production dependencies
make install

# Install development dependencies (includes testing, linting)
make install-dev
```

### Running the Application
```bash
# Run the microservice
make run
# or
python main.py

# Using Docker
make docker-build
make docker-run
```

### Testing
```bash
# Run all tests
make test

# Run specific test suites
make test-unit
make test-integration

# Run with coverage
make test-coverage
```

### Code Quality
```bash
# Lint code
make lint

# Format code
make format

# Type checking
make type-check

# Run full CI pipeline locally
make ci
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
LOG_FILE=logs/summary_service.log
```

## API Endpoints

- **POST /summaries**: Create new summary request (returns request_id)
- **GET /summaries/{request_id}/status**: Get processing status and progress
- **GET /summaries/{request_id}**: Get final summary result
- **GET /health**: Health check endpoint

## Key Patterns

- **Clean Architecture**: Domain-driven design with dependency inversion
- **Async Processing**: FastAPI background tasks for non-blocking summary creation
- **Repository Pattern**: Abstract storage interface with in-memory implementation
- **Dependency Injection**: Services injected via FastAPI dependency system
- **Comprehensive Logging**: Structured logging throughout all layers
- **Type Safety**: Full mypy type checking with Pydantic models

## Testing Strategy

- **Unit Tests**: Test individual components in isolation with mocks
- **Integration Tests**: Test API endpoints and component interactions
- **Coverage**: Minimum 80% test coverage requirement
- **Async Testing**: All async code properly tested with pytest-asyncio

## CI/CD Pipeline

GitLab CI pipeline includes:
- **Build**: Dependency installation and validation
- **Test**: Unit tests, integration tests, coverage reporting
- **Quality**: Linting, type checking, formatting validation
- **Security**: Safety check for vulnerabilities, Bandit SAST scanning
- **Docker**: Container build and basic smoke tests
- **Deploy**: Manual deployment to staging/production environments