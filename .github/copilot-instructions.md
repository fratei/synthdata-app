# Copilot Coding Agent — SynthData

## Project overview
SynthData is a CreativeWare product — an AI-powered synthetic data generation platform. It generates privacy-compliant tabular data, text documents, and audio/speech recordings using Azure AI services.

## Architecture
- **Backend**: Python 3.12 with FastAPI — located in `backend/src/`
- **Frontend**: React/Next.js — located in `frontend/`
- **AI Services**: Azure OpenAI (GPT-4o) for text/tabular, Azure Speech Services for audio
- **Storage**: Azure Blob Storage for generated datasets
- **Infrastructure**: Azure Container Apps or AKS, defined in `infrastructure/`
- **IaC**: Bicep templates in `infrastructure/bicep/`, K8s manifests in `infrastructure/k8s/`

## Coding conventions
- **Language**: Python 3.12+ with type hints (`from __future__ import annotations`)
- **Framework**: FastAPI with Pydantic v2 models
- **Module system**: Package-based (`backend/src/` is the root package)
- **Formatting**: Follow PEP 8, use double quotes for strings
- **Docstrings**: Google style docstrings on all public classes and functions
- **Dependencies**: Pinned versions in `backend/requirements.txt`
- **Testing**: pytest with `pytest-asyncio` for async tests
- **API routes**: All API routes live under `/api/v1/` prefix

## Key patterns
- **Generators**: All data generators extend `BaseGenerator` in `backend/src/generators/base.py`
- **Async-first**: All generation and Azure service calls are async
- **Config**: Environment-based config via `backend/src/config.py` using `python-dotenv`
- **Error handling**: FastAPI `HTTPException` for API errors, logging for internal errors
- **API models**: Pydantic models in `backend/src/schemas/models.py` for all request/response types
- **Service clients**: Lazy-initialized Azure clients in `backend/src/services/`

## Environment variables
See `.env.example` for the full list. Key variables:
- `AZURE_OPENAI_ENDPOINT` — Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` — Azure OpenAI API key
- `AZURE_SPEECH_KEY` — Azure Speech Services subscription key
- `AZURE_SPEECH_REGION` — Azure Speech region (default: eastus)
- `AZURE_STORAGE_CONNECTION_STRING` — Azure Blob Storage connection string

## Important files
- `README.md` — Product overview
- `backend/src/main.py` — FastAPI application entry point
- `backend/src/generators/base.py` — Base generator interface
- `backend/src/schemas/models.py` — API request/response models
- `docs/ARCHITECTURE.md` — System architecture with Mermaid diagrams
- `docs/API.md` — API documentation
- `strategy/README.md` — Product strategy and roadmap
- `docs/agents/HANDBOOK.md` — Agent operating standards
- `docs/agents/DASHBOARD.md` — Live agent dashboard
