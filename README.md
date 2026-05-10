# SynthData

> AI-powered synthetic data generation platform

## Overview

| | |
|---|---|
| **Product** | SynthData |
| **Company** | [CreativeWare](https://github.com/fratei/creative-ware-hq) |
| **Owner** | [@fratei](https://github.com/fratei) |
| **Status** | 🏗️ Building |
| **Sister Product** | [AudioText](https://github.com/fratei/audiotext-app) |

SynthData generates privacy-compliant synthetic data for AI/ML training, software testing, and regulatory compliance. It produces realistic tabular data, text documents, and audio/speech recordings — all without exposing real PII.

### Key Use Cases

- **AI/ML Training** — Generate synthetic datasets to train models without exposing real data
- **Software Testing** — Realistic test data that mimics production without PII
- **Privacy Compliance** — GDPR/CCPA-compliant data substitutes for analytics and sharing
- **Audio/Speech Data** — Synthetic voice recordings, transcripts, and audio training data (leveraging [AudioText](https://github.com/fratei/audiotext-app)'s audio AI expertise)

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────────┐
│  React/Next  │────▶│  API Gateway │────▶│  FastAPI Backend      │
│  Frontend    │     │              │     │                      │
└─────────────┘     └──────────────┘     │  ┌────────────────┐  │
                                          │  │  Generators     │  │
                                          │  │  - Tabular      │  │
                                          │  │  - Text         │  │
                                          │  │  - Audio/Speech │  │
                                          │  └────────┬───────┘  │
                                          └───────────┼──────────┘
                                                      │
                              ┌────────────────────────┼────────────────┐
                              │                        │                │
                    ┌─────────▼──────┐   ┌─────────────▼───┐   ┌───────▼────────┐
                    │ Azure OpenAI   │   │ Azure Speech    │   │ Azure Blob     │
                    │ (text/tabular) │   │ (audio gen)     │   │ Storage        │
                    └────────────────┘   └─────────────────┘   └────────────────┘
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full architecture diagram.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI |
| Frontend | React, Next.js |
| AI Services | Azure OpenAI (GPT-4o), Azure Speech Services |
| Storage | Azure Blob Storage |
| Infrastructure | Azure (AKS / Container Apps), Bicep |
| CI/CD | GitHub Actions |

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 20+
- Azure CLI (`az`)
- Azure Developer CLI (`azd`)

### Local Development

```bash
# Clone the repo
git clone https://github.com/fratei/synthdata-app.git
cd synthdata-app

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env  # fill in your Azure keys
uvicorn src.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```

## Project Structure

```
synthdata-app/
├── backend/
│   ├── src/
│   │   ├── api/           # FastAPI routes and endpoints
│   │   ├── generators/    # Data generation engines (tabular, text, audio)
│   │   ├── schemas/       # Pydantic request/response models
│   │   ├── services/      # Azure service integrations
│   │   ├── config.py      # App configuration
│   │   └── main.py        # FastAPI entry point
│   ├── tests/             # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/              # React/Next.js frontend
├── docs/
│   ├── ARCHITECTURE.md    # System architecture
│   ├── API.md             # API documentation
│   └── agents/            # Agent fleet docs
├── infrastructure/
│   ├── bicep/             # Azure Bicep templates
│   └── k8s/               # Kubernetes manifests
├── strategy/              # Product strategy and roadmap
├── azure.yaml             # Azure Developer CLI config
└── .env.example           # Environment variable template
```

## API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/generate` | Generate synthetic data |
| `GET` | `/api/v1/schemas` | List available schema templates |
| `GET` | `/api/v1/jobs/{job_id}` | Check generation job status |
| `GET` | `/api/v1/datasets/{dataset_id}` | Download generated dataset |
| `GET` | `/health` | Health check |

See [docs/API.md](docs/API.md) for full API documentation.

## Contributing

1. Fork the repo and create a feature branch
2. Follow existing code patterns and include docstrings
3. Add tests for new functionality
4. Run `pytest` and ensure all tests pass
5. Submit a PR — the agent fleet will review automatically

## Agent System

This product runs an autonomous agent fleet:
- **Agent Fleet** — CPO/CFO/CTO review opportunities every 2h
- **PR Pipeline** — Autonomous review + merge with risk classification
- **Observability** — Monitoring + dashboard updates every 2h
- **CI/CD** — Automated lint → test → build → deploy

See [Agent Dashboard](docs/agents/DASHBOARD.md) for live status.
For repository-level rollout steps and manual controls, see the
[Agent Handbook checklist](docs/agents/HANDBOOK.md#humanadmin-actions-checklist).

## Links

- [CreativeWare HQ](https://github.com/fratei/creative-ware-hq)
- [Product Card](https://github.com/fratei/creative-ware-hq/blob/main/products/synthdata.md)
- [Architecture](docs/ARCHITECTURE.md)
- [API Docs](docs/API.md)
- [Agent Handbook](docs/agents/HANDBOOK.md)
- [Strategy](strategy/README.md)

## License

MIT — see [LICENSE](LICENSE) for details.

---
*Part of [CreativeWare](https://github.com/fratei/creative-ware-hq) — Autonomous AI Company*
