# SynthData — System Architecture

## Overview

SynthData is a multi-tier application that generates privacy-compliant synthetic data using Azure AI services. The system processes generation requests asynchronously and stores results in Azure Blob Storage for download.

## Architecture Diagram

```mermaid
graph TB
    subgraph Client
        FE[React/Next.js Frontend]
    end

    subgraph Azure["Azure Cloud"]
        subgraph Compute["Compute (AKS / Container Apps)"]
            API[FastAPI Backend<br/>API Gateway + Business Logic]
            Workers[Background Workers<br/>Async Generation Jobs]
        end

        subgraph AI["Azure AI Services"]
            AOAI[Azure OpenAI<br/>GPT-4o]
            Speech[Azure Speech Services<br/>Neural TTS]
        end

        subgraph Storage["Storage"]
            Blob[Azure Blob Storage<br/>Generated Datasets]
            KV[Azure Key Vault<br/>Secrets & Keys]
        end

        subgraph Monitoring["Observability"]
            AppIns[Application Insights]
            Monitor[Azure Monitor]
        end
    end

    FE -->|HTTPS| API
    API -->|Queue Jobs| Workers
    Workers -->|Text & Tabular Generation| AOAI
    Workers -->|Audio Synthesis| Speech
    Workers -->|Store Datasets| Blob
    API -->|Retrieve Secrets| KV
    API -->|Download Links| Blob
    API -->|Telemetry| AppIns
    Workers -->|Telemetry| AppIns
```

## Component Details

### Frontend (React/Next.js)
- Schema builder UI for defining data structures
- Job dashboard for monitoring generation progress
- Dataset preview and download interface
- Authentication via Azure AD / GitHub OAuth

### API Backend (FastAPI)
- RESTful API for generation requests
- Schema validation and cost estimation
- Job orchestration and status tracking
- Authentication and rate limiting middleware

### Data Generators
| Generator | Input | AI Service | Output |
|-----------|-------|------------|--------|
| **Tabular** | Column schema + constraints | Azure OpenAI (GPT-4o) | JSON, CSV, Parquet |
| **Text** | Document type + domain + tone | Azure OpenAI (GPT-4o) | JSON array of documents |
| **Audio** | Voice + language + speakers | Azure Speech Services | WAV, MP3, OGG + transcripts |

### Background Workers
- Process generation jobs from a task queue
- Handle large datasets via chunked generation
- Report progress back to API for status polling
- Retry logic for transient Azure service failures

### Azure Blob Storage
- Stores generated datasets with configurable retention
- SAS token-based download URLs with expiration
- Lifecycle policies for automatic cleanup

### Azure Key Vault
- Stores Azure OpenAI API keys
- Stores Azure Speech subscription keys
- Stores storage connection strings
- Managed identity access from compute

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant W as Worker
    participant AI as Azure OpenAI
    participant S as Blob Storage

    U->>API: POST /api/v1/generate
    API->>API: Validate schema, estimate cost
    API->>W: Queue generation job
    API->>U: 200 {job_id, status: "queued"}

    U->>API: GET /api/v1/jobs/{job_id}
    API->>U: {status: "processing"}

    W->>AI: Generate synthetic data (batched)
    AI->>W: Generated records
    W->>S: Upload dataset
    W->>API: Mark job complete

    U->>API: GET /api/v1/jobs/{job_id}
    API->>U: {status: "completed", dataset_id}

    U->>API: GET /api/v1/datasets/{dataset_id}
    API->>S: Generate SAS URL
    API->>U: {download_url}
```

## Infrastructure

- **Compute**: Azure Kubernetes Service (AKS) or Azure Container Apps
- **Networking**: VNet-integrated with private endpoints for AI services
- **CI/CD**: GitHub Actions → Azure Container Registry → AKS
- **Secrets**: Azure Key Vault with managed identity
- **Monitoring**: Application Insights + Azure Monitor dashboards
