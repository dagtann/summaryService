# Document Summary Service

A Python microservice for creating iterative document summaries using LangChain and Anthropic's Claude model. The service accepts markdown-formatted documents and returns refined summaries through a REST API.

## Features

- **Clean Architecture**: Domain-driven design with clear separation of concerns
- **Async Processing**: Non-blocking summary generation using FastAPI background tasks
- **Markdown Support**: Accepts and returns markdown-formatted content
- **Iterative Refinement**: Uses the refine strategy to progressively improve summaries
- **Comprehensive Logging**: Structured logging throughout all layers
- **Full Test Coverage**: Unit and integration tests with coverage reporting
- **CI/CD Ready**: GitLab CI pipeline with testing, security scanning, and deployment

## Quick Start

### Prerequisites

- Python 3.9+
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd summaryService

# Install dependencies
make install-dev

# Copy environment file and configure
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Running the Service

```bash
# Start the service
make run

# Or with Docker
make docker-build
make docker-run
```

The service will be available at `http://localhost:8000`

### API Usage

1. **Create a summary request:**
```bash
curl -X POST http://localhost:8000/summaries \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "content": "# Document 1\n\nThis is the first document content...",
        "title": "Document 1"
      },
      {
        "content": "# Document 2\n\nThis is the second document content...",
        "title": "Document 2"
      }
    ]
  }'
```

2. **Check processing status:**
```bash
curl http://localhost:8000/summaries/{request_id}/status
```

3. **Get the final summary:**
```bash
curl http://localhost:8000/summaries/{request_id}
```

## Development

### Testing

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test suites
make test-unit
make test-integration
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type checking
make type-check

# Run full CI pipeline locally
make ci
```

## Architecture

```
src/
├── domain/          # Core business logic and interfaces
│   ├── models.py    # Domain models (Document, SummaryRequest, etc.)
│   └── interfaces.py # Abstract interfaces
├── use_cases/       # Application business rules
│   └── summary_use_case.py # Summary creation logic
├── infrastructure/  # External concerns
│   ├── llm_service.py      # LangChain LLM integration
│   └── repository.py       # In-memory storage
└── web/            # HTTP API interface
    ├── api.py      # FastAPI endpoints
    └── models.py   # API request/response models
```

## API Endpoints

- `GET /health` - Health check
- `POST /summaries` - Create summary request
- `GET /summaries/{request_id}/status` - Get processing status
- `GET /summaries/{request_id}` - Get summary result

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Anthropic API key (required) | - |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `LOG_FILE` | Log file path | `logs/summary_service.log` |

## License

MIT License