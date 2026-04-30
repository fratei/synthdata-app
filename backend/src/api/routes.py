"""SynthData API routes for synthetic data generation."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..schemas.models import (
    DatasetResponse,
    GenerateRequest,
    GenerateResponse,
    JobStatusResponse,
    SchemaTemplate,
)

router = APIRouter(tags=["synthdata"])

# In-memory job store (replaced with persistent storage in production)
_jobs: dict[str, dict] = {}

# Built-in schema templates
_SCHEMA_TEMPLATES: list[SchemaTemplate] = [
    SchemaTemplate(
        id="users",
        name="User Profiles",
        description="Synthetic user profiles with name, email, address, and demographics",
        data_type="tabular",
        columns=[
            {"name": "id", "type": "uuid"},
            {"name": "first_name", "type": "string"},
            {"name": "last_name", "type": "string"},
            {"name": "email", "type": "email"},
            {"name": "age", "type": "integer", "min": 18, "max": 90},
            {"name": "city", "type": "string"},
            {"name": "country", "type": "string"},
        ],
    ),
    SchemaTemplate(
        id="transactions",
        name="Financial Transactions",
        description="Synthetic payment transactions with amounts, merchants, and timestamps",
        data_type="tabular",
        columns=[
            {"name": "transaction_id", "type": "uuid"},
            {"name": "user_id", "type": "uuid"},
            {"name": "amount", "type": "float", "min": 0.01, "max": 10000.0},
            {"name": "currency", "type": "string"},
            {"name": "merchant", "type": "string"},
            {"name": "timestamp", "type": "datetime"},
        ],
    ),
    SchemaTemplate(
        id="support-emails",
        name="Customer Support Emails",
        description="Synthetic customer support email threads",
        data_type="text",
        columns=[],
    ),
    SchemaTemplate(
        id="voice-recordings",
        name="Voice Recordings",
        description="Synthetic voice recordings with transcripts",
        data_type="audio",
        columns=[],
    ),
]


@router.post("/generate", response_model=GenerateResponse)
async def generate_data(request: GenerateRequest) -> GenerateResponse:
    """Submit a synthetic data generation job.

    Accepts a schema definition and generation parameters, then queues
    an asynchronous generation job. Returns a job ID for status polling.
    """
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    _jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "data_type": request.data_type,
        "count": request.count,
        "format": request.output_format,
        "created_at": now.isoformat(),
        "dataset_id": None,
    }

    # Estimate time based on data type and count
    estimated_seconds = _estimate_generation_time(request.data_type, request.count)

    return GenerateResponse(
        job_id=job_id,
        status="queued",
        estimated_time_seconds=estimated_seconds,
        created_at=now,
    )


@router.get("/schemas", response_model=list[SchemaTemplate])
async def list_schemas() -> list[SchemaTemplate]:
    """List available schema templates for data generation."""
    return _SCHEMA_TEMPLATES


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """Check the status of a data generation job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        data_type=job["data_type"],
        count=job["count"],
        created_at=job["created_at"],
        dataset_id=job.get("dataset_id"),
    )


@router.get("/datasets/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str) -> DatasetResponse:
    """Retrieve metadata and download URL for a generated dataset."""
    # Stub: in production this queries Azure Blob Storage
    raise HTTPException(
        status_code=404,
        detail=f"Dataset {dataset_id} not found",
    )


def _estimate_generation_time(data_type: str, count: int) -> int:
    """Estimate generation time in seconds based on type and row count."""
    base_times = {"tabular": 2, "text": 5, "audio": 30}
    base = base_times.get(data_type, 5)
    return base + (count // 100)
