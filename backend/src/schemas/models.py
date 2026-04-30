"""Pydantic models for SynthData API request and response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ColumnDefinition(BaseModel):
    """Definition of a single column in a tabular schema."""

    name: str = Field(..., description="Column name")
    type: str = Field(..., description="Data type (string, integer, float, email, uuid, datetime, boolean)")
    min: float | None = Field(None, description="Minimum value for numeric types")
    max: float | None = Field(None, description="Maximum value for numeric types")
    pattern: str | None = Field(None, description="Regex pattern for string types")
    values: list[str] | None = Field(None, description="Allowed values (enum)")


class SchemaDefinition(BaseModel):
    """Schema definition for tabular data generation."""

    columns: list[ColumnDefinition] = Field(..., description="Column definitions")
    constraints: dict[str, Any] | None = Field(None, description="Cross-column constraints")


class TextOptions(BaseModel):
    """Options specific to text data generation."""

    domain: str = Field("general", description="Domain context (e.g., healthcare, finance, legal)")
    tone: str = Field("neutral", description="Writing tone (formal, casual, neutral)")
    min_length: int = Field(100, description="Minimum character length per document")
    max_length: int = Field(1000, description="Maximum character length per document")
    document_type: str = Field("paragraph", description="Type: paragraph, email, chat, article")


class AudioOptions(BaseModel):
    """Options specific to audio/speech data generation."""

    voice: str = Field("en-US-JennyNeural", description="Azure Speech voice name")
    language: str = Field("en-US", description="Language code")
    format: str = Field("wav", description="Audio format (wav, mp3, ogg, flac)")
    speakers: int = Field(1, description="Number of speakers for conversation generation")
    include_transcript: bool = Field(True, description="Include text transcript alongside audio")
    topic: str | None = Field(None, description="Topic or domain for transcript generation (e.g. 'customer support', 'medical dictation')")
    transcript_format: str = Field("text", description="Transcript output format (text, json, srt, vtt)")
    noise_type: str | None = Field(None, description="Background noise type for Phase 2 acoustic simulation (office, car, street, cafe)")
    acoustic_condition: str | None = Field(None, description="Acoustic condition for Phase 2 simulation (reverb, phone, voip, clean)")


class GenerateRequest(BaseModel):
    """Request body for the /generate endpoint."""

    data_type: str = Field(..., description="Type of data to generate: tabular, text, or audio")
    schema_definition: SchemaDefinition | None = Field(None, description="Schema for tabular data")
    count: int = Field(100, ge=1, le=10000, description="Number of records to generate")
    output_format: str = Field("json", description="Output format: json, csv, parquet")
    text_options: TextOptions | None = Field(None, description="Options for text generation")
    audio_options: AudioOptions | None = Field(None, description="Options for audio generation")
    seed: int | None = Field(None, description="Random seed for reproducibility")

    class Config:
        json_schema_extra = {
            "example": {
                "data_type": "tabular",
                "schema_definition": {
                    "columns": [
                        {"name": "name", "type": "string"},
                        {"name": "age", "type": "integer", "min": 18, "max": 90},
                        {"name": "email", "type": "email"},
                    ]
                },
                "count": 100,
                "output_format": "json",
            }
        }


class GenerateResponse(BaseModel):
    """Response returned when a generation job is submitted."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: queued, processing, completed, failed")
    estimated_time_seconds: int = Field(..., description="Estimated time to completion")
    created_at: datetime


class JobStatusResponse(BaseModel):
    """Response for job status queries."""

    job_id: str
    status: str = Field(..., description="Job status: queued, processing, completed, failed")
    data_type: str
    count: int
    created_at: str
    dataset_id: str | None = None
    error: str | None = None


class DatasetResponse(BaseModel):
    """Response for dataset download requests."""

    dataset_id: str
    download_url: str
    format: str
    row_count: int
    size_bytes: int
    created_at: datetime
    expires_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class SchemaTemplate(BaseModel):
    """A pre-built schema template for common data generation patterns."""

    id: str
    name: str
    description: str
    data_type: str
    columns: list[dict[str, Any]] = Field(default_factory=list)
