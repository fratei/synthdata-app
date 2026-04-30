# SynthData API Documentation

## Base URL

```
https://api.synthdata.creativeware.ai/api/v1
```

Local development: `http://localhost:8000/api/v1`

## Authentication

All API requests require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <your-api-key>
```

## Endpoints

### Health Check

```
GET /health
```

Returns service health status. No authentication required.

**Response** `200 OK`
```json
{
  "status": "healthy",
  "service": "SynthData",
  "version": "0.1.0"
}
```

---

### Generate Synthetic Data

```
POST /api/v1/generate
```

Submit a synthetic data generation job.

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `data_type` | string | ✅ | `tabular`, `text`, or `audio` |
| `schema_definition` | object | For tabular | Column definitions |
| `count` | integer | No (default: 100) | Number of records (1–10,000) |
| `output_format` | string | No (default: json) | `json`, `csv`, or `parquet` |
| `text_options` | object | For text | Text generation options |
| `audio_options` | object | For audio | Audio generation options |
| `seed` | integer | No | Random seed for reproducibility |

**Example — Tabular Data**
```json
{
  "data_type": "tabular",
  "schema_definition": {
    "columns": [
      { "name": "first_name", "type": "string" },
      { "name": "last_name", "type": "string" },
      { "name": "email", "type": "email" },
      { "name": "age", "type": "integer", "min": 18, "max": 90 },
      { "name": "city", "type": "string" }
    ]
  },
  "count": 500,
  "output_format": "csv"
}
```

**Example — Text Data**
```json
{
  "data_type": "text",
  "count": 20,
  "text_options": {
    "domain": "healthcare",
    "tone": "formal",
    "document_type": "email",
    "min_length": 200,
    "max_length": 800
  }
}
```

**Example — Audio Data**
```json
{
  "data_type": "audio",
  "count": 5,
  "audio_options": {
    "voice": "en-US-JennyNeural",
    "language": "en-US",
    "format": "wav",
    "speakers": 2,
    "include_transcript": true,
    "topic": "customer support",
    "transcript_format": "srt"
  }
}
```

`audio_options` fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `voice` | string | `en-US-JennyNeural` | Azure Neural voice name |
| `language` | string | `en-US` | BCP-47 language code |
| `format` | string | `wav` | Audio format: `wav`, `mp3`, `ogg`, `flac` |
| `speakers` | integer | `1` | Number of speakers (1–10). >1 generates a conversation. |
| `include_transcript` | boolean | `true` | Include aligned transcript in the response |
| `topic` | string | `null` | Topic or domain for transcript generation (e.g. `"medical dictation"`) |
| `transcript_format` | string | `text` | Transcript output format: `text`, `json`, `srt`, `vtt` |
| `noise_type` | string | `null` | *(Phase 2)* Background noise: `office`, `car`, `street`, `cafe` |
| `acoustic_condition` | string | `null` | *(Phase 2)* Acoustic simulation: `reverb`, `phone`, `voip`, `clean` |

**Response** `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "estimated_time_seconds": 12,
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

### List Schema Templates

```
GET /api/v1/schemas
```

Returns a list of pre-built schema templates for common use cases.

**Response** `200 OK`
```json
[
  {
    "id": "users",
    "name": "User Profiles",
    "description": "Synthetic user profiles with name, email, address, and demographics",
    "data_type": "tabular",
    "columns": [
      { "name": "id", "type": "uuid" },
      { "name": "first_name", "type": "string" },
      { "name": "email", "type": "email" }
    ]
  }
]
```

---

### Check Job Status

```
GET /api/v1/jobs/{job_id}
```

Check the status of a data generation job.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `job_id` | string (UUID) | Job identifier from generate response |

**Response** `200 OK`
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "data_type": "tabular",
  "count": 500,
  "created_at": "2025-01-15T10:30:00Z",
  "dataset_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Status Values**: `queued`, `processing`, `completed`, `failed`

**Response** `404 Not Found`
```json
{
  "detail": "Job 550e8400-... not found"
}
```

---

### Download Generated Dataset

```
GET /api/v1/datasets/{dataset_id}
```

Retrieve metadata and a time-limited download URL for a generated dataset.

**Path Parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset_id` | string (UUID) | Dataset identifier from job status |

**Response** `200 OK`
```json
{
  "dataset_id": "660e8400-e29b-41d4-a716-446655440001",
  "download_url": "https://synthdata.blob.core.windows.net/datasets/...",
  "format": "csv",
  "row_count": 500,
  "size_bytes": 45320,
  "created_at": "2025-01-15T10:30:15Z",
  "expires_at": "2025-01-16T10:30:15Z",
  "metadata": {
    "data_type": "tabular",
    "schema_id": "users"
  }
}
```

## Error Responses

All errors follow the standard format:

```json
{
  "detail": "Human-readable error message"
}
```

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request — invalid parameters |
| 401 | Unauthorized — missing or invalid API key |
| 404 | Not Found — resource does not exist |
| 422 | Validation Error — request body schema mismatch |
| 429 | Rate Limited — too many requests |
| 500 | Internal Server Error |

## Rate Limits

| Plan | Requests/min | Max rows/request | Max concurrent jobs |
|------|-------------|------------------|-------------------|
| Free | 10 | 100 | 1 |
| Pro | 60 | 10,000 | 10 |
| Enterprise | 300 | 100,000 | 50 |
